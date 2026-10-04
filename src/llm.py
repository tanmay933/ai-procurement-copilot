from __future__ import annotations

import json
from typing import Any

import requests

from src.config import GEMINI_API_KEY, LLM_MODEL, LLM_PROVIDER, OPENROUTER_API_KEY, OPENROUTER_APP_NAME, OPENROUTER_SITE_URL


class LLMClient:
    def __init__(self) -> None:
        self.provider = LLM_PROVIDER
        self.model = LLM_MODEL

    @property
    def available(self) -> bool:
        if self.provider == "gemini":
            return bool(GEMINI_API_KEY)
        if self.provider == "openrouter":
            return bool(OPENROUTER_API_KEY)
        return False

    def generate(self, system: str, user: str) -> dict[str, Any]:
        if not self.available:
            return {}
        if self.provider == "gemini":
            return self._gemini(system, user)
        if self.provider == "openrouter":
            return self._openrouter(system, user)
        return {}

    def _gemini(self, system: str, user: str) -> dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
        response = requests.post(url, params={"key": GEMINI_API_KEY}, json=payload, timeout=20)
        response.raise_for_status()
        body = response.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)

    def _openrouter(self, system: str, user: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": OPENROUTER_SITE_URL,
            "X-Title": OPENROUTER_APP_NAME,
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        body = response.json()
        text = body["choices"][0]["message"]["content"]
        return json.loads(text)
