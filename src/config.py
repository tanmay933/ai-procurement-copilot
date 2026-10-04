from __future__ import annotations

import os
from datetime import date

from dotenv import load_dotenv

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)

POLICY_REFERENCE_DATE = date(2026, 9, 30)
VENDOR_REVIEW_MAX_DAYS = 365

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8501")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "AI Procurement Request Copilot")
