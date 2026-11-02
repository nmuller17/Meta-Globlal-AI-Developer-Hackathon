"""Meta Model API client (Muse Spark), through its OpenAI-compatible Chat Completions endpoint.

Every LLM caller (gateway, ingestion, buyer agent) builds its client here. MODEL_API_BASE_URL can point
at another OpenAI-compatible host serving Meta's open-weights models instead.
"""

from __future__ import annotations

import os

import openai

DEFAULT_BASE_URL = "https://api.meta.ai/v1"


def api_key() -> str:
    return os.getenv("MODEL_API_KEY", "").strip()


def _settings() -> dict:
    # api_key is always passed: left to None, the SDK would send OPENAI_API_KEY to this host.
    return {"base_url": os.getenv("MODEL_API_BASE_URL", "").strip() or DEFAULT_BASE_URL, "api_key": api_key()}


def client(**kwargs) -> openai.OpenAI:
    return openai.OpenAI(**_settings(), **kwargs)


def async_client(**kwargs) -> openai.AsyncOpenAI:
    return openai.AsyncOpenAI(**_settings(), **kwargs)
