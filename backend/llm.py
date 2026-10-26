"""Thin wrapper around an OpenAI-compatible chat API (OpenRouter by default).

When no API key is configured, `available()` is False and every agent falls back
to its deterministic rule-based path, so the app and the evaluation still run.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "anthropic/claude-haiku-5.5")
BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")

_client = None


def available() -> bool:
    if os.getenv("ROAMEO_FORCE_DEMO") == "1":
        return False
    return bool(os.getenv("OPENROUTER_API_KEY"))


def client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(base_url=BASE_URL, api_key=os.getenv("OPENROUTER_API_KEY"))
    return _client


def chat(messages: list[dict[str, Any]], tools: Optional[list[dict]] = None,
         temperature: float = 0.2, max_tokens: int = 1200):
    kwargs: dict[str, Any] = dict(model=DEFAULT_MODEL, messages=messages,
                                  temperature=temperature, max_tokens=max_tokens)
    if tools:
        kwargs["tools"] = tools
    return client().chat.completions.create(**kwargs).choices[0].message


def chat_json(system: str, user: str, max_tokens: int = 1200) -> dict:
    """Ask for a JSON object and parse it, tolerating ```json fences."""
    msg = chat([{"role": "system", "content": system + "\nReply with a single JSON object only."},
                {"role": "user", "content": user}], temperature=0, max_tokens=max_tokens)
    text = msg.content or ""
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(f"LLM did not return JSON: {text[:200]}")
    return json.loads(match.group(0))
