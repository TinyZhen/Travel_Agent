import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from dotenv import load_dotenv
from smolagents import CodeAgent
import AttractionSearchTool as ats
import EventSearchTool as es
import HotelSearchTool as hs
import FlightSearchTool as fs
import SummaryTool as st
from model import OpenRouterModel
from collector import collected_results

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = OpenRouterModel(
    model="meta-llama/llama-3-70b-instruct",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    system_prompt=(
        "今天是2025年，请将用户说的任何日期（如 May 7、July 1）解释为2025年的该日期，"
        "除非用户特别指出了其他年份。"
        "请严格使用用户提供的日期作为航班和酒店的查询日期，不要提前或延后。"
        "你有四个工具：events、flights、hotels、attractions。"
        "无论用户重点提到哪个内容，都必须使用**所有四个工具**，每次都要调用它们。"
        "即使某个工具可能没有返回结果，也要尝试调用。"
        "调用 flights 工具时，请将城市名称转换为 IATA 三字机场代码。例如 Boston → BOS，New York → JFK。"
        "如果无法确定，可直接使用城市名，后续系统将自动解析。"
        "最终输出结构应为 JSON：包括 `summary` 文本说明，以及 `structured` 字段，"
        "其中包含 events, flights, hotels, attractions 四个字段。"
        "如某项数据为空，也请以空数组返回，不要省略该字段。"
        "**如果用户没有说明出发城市，请默认从 Boston（BOS）出发。**"
        "**如果用户没有说明旅行日期，请默认使用“明天”的日期作为出发日期。**"
        "在调用景点工具时，请优先考虑城市最著名的地标（如 Statue of Liberty、Empire State Building），必要时使用关键词搜索。"
    )
)

agent = CodeAgent(
    tools=[es.search_ticketmaster_events, ats.get_popular_attractions, fs.search_flight_amadeus, hs.search_hotels_from_city],
    model=model,
    add_base_tools=False

)

def extract_metadata(prompt: str) -> dict:
    extraction_prompt = (
        "请从以下用户输入中提取旅行的目的地城市（city）和日期（date），返回 JSON 格式，例如："
        '{"city": "Chicago", "date": "2025-05-09"}。'
        "如果无法识别日期或城市，就返回空字符串对应的字段。\n\n"
        f"用户输入：{prompt}"
    )
    response = model(extraction_prompt).content
    try:
        return json.loads(response)
    except Exception:
        return {"city": "", "date": ""}

class PromptRequest(BaseModel):
    prompt: str

@app.post("/api/agent")
def run_agent(req: PromptRequest):
    try:
        for k in collected_results:
            collected_results[k] = []

        # ✅ Step 1: 从用户输入中提取地点和日期
        metadata = extract_metadata(req.prompt)
        collected_results["metadata"] = {
            "destination": metadata.get("city", "unknown"),
            "date": metadata.get("date", "unknown")
        }

        # ✅ Step 2: 调用工具
        _ = agent.run(req.prompt)

        # ✅ Step 3: 构造总结 prompt
        destination = collected_results["metadata"]["destination"]
        date = collected_results["metadata"]["date"]


        def summarize_collected(collected, max_items=2):
            def flight_summary(f):
                return f"{f.get('airline', 'Unknown')} · {f.get('from')}→{f.get('to')} · " \
                    f"{f.get('departure_time', '')} → {f.get('arrival_time', '')} · ${f.get('price', '?')}"

            def hotel_summary(h):
                return f"{h.get('name', 'Unnamed')} · {h.get('address', '')}"

            def event_summary(e):
                return f"{e.get('name', 'Unknown')} · {e.get('date', '')} @ {e.get('venue', '')}"

            def attraction_summary(a):
                return f"{a.get('name', 'Unnamed')} (⭐ {a.get('rating', '?')} · {a.get('reviews', '?')} reviews)"

            return {
                "metadata": collected.get("metadata", {}),
                "flights": [flight_summary(f) for f in collected.get("flights", [])[:max_items]],
                "hotels": [hotel_summary(h) for h in collected.get("hotels", [])[:max_items]],
                "events": [event_summary(e) for e in collected.get("events", [])[:max_items]],
                "attractions": [attraction_summary(a) for a in collected.get("attractions", [])[:max_items]],
            }
        def run_summary(collected, date, destination):
            compressed = summarize_collected(collected)

            content_lines = []
            for key in ["flights", "hotels", "attractions", "events"]:
                items = compressed.get(key, [])
                if items:
                    content_lines.append(f"{key.title()}:\n" + "\n".join(f"- {i}" for i in items))

            compact_text = "\n\n".join(content_lines)

            messages = [
                {"role": "system", "content": "你是一个旅行助手，请根据旅行数据，总结一段自然语言的行程建议（3~4句话）。"},
                {"role": "user", "content": f"""用户计划在 {date} 前往 {destination} 旅行。

        以下是旅行数据摘要：
        {compact_text}

        请用自然语言总结一次有趣的行程安排。不需要json
        """}
            ]

            return model(messages, use_system_prompt=False).content
        summary = run_summary(collected_results, date, destination)
        # print(summary)
        return {
            "result": summary,
            "structured": collected_results
        }

    except Exception as e:
        return {"error": str(e)}

