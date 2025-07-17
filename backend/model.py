import os
import requests
from typing import Optional

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class OpenRouterModel:
    def __init__(self, model, api_key, system_prompt: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def __call__(self, messages, **kwargs):
        formatted_messages = []

        # Add system prompt as first message if provided
        if self.system_prompt:
            formatted_messages.append({"role": "system", "content": self.system_prompt})

        for msg in messages:
            if isinstance(msg, str):
                formatted_messages.append({"role": "user", "content": msg})
            elif isinstance(msg, dict):
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": 0.7,
            "max_tokens": 500,
            **kwargs
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            res_json = response.json()

            if "choices" in res_json:
                content = res_json["choices"][0]["message"]["content"]
                return ChatMessage(role="assistant", content=content)
            else:
                error_msg = res_json.get("error", {}).get("message", "Unknown model error.")
                return ChatMessage(role="assistant", content=f"[Error] {error_msg}")

        except Exception as e:
            return ChatMessage(role="assistant", content=f"[Exception] {str(e)}")
