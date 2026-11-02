"""Single entry point for structured LLM calls (Meta Model API, Muse Spark, JSON output only)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TypeVar

import openai
from pydantic import BaseModel, ValidationError

from shared import config, model_api

log = logging.getLogger("llm")

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """The model could not produce a usable structured answer."""


@lru_cache(maxsize=1)
def _client() -> openai.OpenAI:
    return model_api.client(timeout=60.0, max_retries=2)


def structured_call(system: str, user: str, output_model: type[T], effort: str = "medium") -> T:
    """One request, validated against `output_model`. Raises LLMError on failure."""
    if not model_api.api_key():
        raise LLMError("MODEL_API_KEY is not set")
    try:
        response = _client().chat.completions.parse(
            model=config.LLM_MODEL,
            max_completion_tokens=4000,
            reasoning_effort=effort,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format=output_model,
        )
    except openai.APIConnectionError as e:
        raise LLMError(f"LLM unreachable: {e}") from e
    except openai.RateLimitError as e:
        raise LLMError("LLM rate limited") from e
    except openai.APIStatusError as e:
        raise LLMError(f"LLM error {e.status_code}: {e.message}") from e
    except (openai.LengthFinishReasonError, openai.ContentFilterFinishReasonError, ValidationError) as e:
        # The SDK raises these while parsing: a cut-off or filtered answer, or JSON that misses the schema.
        raise LLMError(f"LLM returned no valid structured output ({type(e).__name__})") from e

    choice = response.choices[0]
    if choice.message.refusal:
        raise LLMError("LLM refused the request")
    if choice.message.parsed is None:
        raise LLMError(f"LLM returned no valid structured output (finish_reason={choice.finish_reason})")
    return choice.message.parsed
