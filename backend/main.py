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
        "Today is 2025. Please interpret any dates the user mentions (e.g., May 7, July 1) "
        "as referring to the year 2025 unless a different year is explicitly stated. "
        "Always use the exact date provided by the user for hotel and flight searches—do not shift the date. "
        "You have four tools: events, flights, hotels, and attractions. "
        "No matter which one the user emphasizes, always use **all four tools** each time. "
        "Even if one tool may return nothing, still attempt to call it. "
        "When calling the flights tool, convert city names to IATA 3-letter codes. For example, Boston → BOS, New York → JFK. "
        "If you’re not sure, just use the city name—downstream logic will handle it. "
        "The final output should be a JSON object containing a `summary` (natural language) and a `structured` field "
        "with events, flights, hotels, and attractions as subfields. "
        "If any are empty, return an empty list—do not omit any fields. "
        "**If the user does not specify a departure city, assume Boston (BOS).** "
        "**If the user does not specify a date, assume the departure date is tomorrow.** "
        "When calling the attractions tool, prioritize the city’s most famous landmarks (e.g., Statue of Liberty, Empire State Building); "
        "if needed, use keyword search."
    )
)

agent = CodeAgent(
    tools=[
        es.search_ticketmaster_events,
        ats.get_popular_attractions,
        fs.search_flight_amadeus,
        hs.search_hotels_from_city,
    ],
    model=model,
    add_base_tools=False
)

def extract_metadata(prompt: str) -> dict:
    extraction_prompt = (
        "Please extract the travel destination city (city) and date (date) from the user input below. "
        "Return it as a JSON object, e.g., {\"city\": \"Chicago\", \"date\": \"2025-05-09\"}. "
        "If either is unrecognizable, return an empty string for that field.\n\n"
        f"User input: {prompt}"
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

        # ✅ Step 1: Extract metadata from user input
        metadata = extract_metadata(req.prompt)
        collected_results["metadata"] = {
            "destination": metadata.get("city", "unknown"),
            "date": metadata.get("date", "unknown")
        }

        # ✅ Step 2: Run agent and collect tool outputs
        _ = agent.run(req.prompt)

        # ✅ Step 3: Summarize response

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
                {"role": "system", "content": "You are a travel assistant. Based on the data below, generate a 3–4 sentence natural language itinerary."},
                {"role": "user", "content": f"""The user is planning to travel to {destination} on {date}.

Here’s a summary of the available travel data:
{compact_text}

Please write a fun, natural itinerary suggestion. No JSON required.
"""}
            ]

            return model(messages, use_system_prompt=False).content

        summary = run_summary(collected_results, date, destination)

        return {
            "result": summary,
            "structured": collected_results
        }

    except Exception as e:
        return {"error": str(e)}
