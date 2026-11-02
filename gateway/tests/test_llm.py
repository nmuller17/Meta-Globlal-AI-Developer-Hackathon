"""The real OpenAI SDK against a fake Meta Model API: request shape, schema, parsing and errors."""

import json

import httpx
import pytest

from gateway import llm
from gateway.routers.rules import _ParsedRules
from shared import config, model_api
from shared.schemas import OfferDraft, SalesAgentOutput


def fake_api(monkeypatch, status=200, content=None, refusal=None, finish_reason="stop"):
    """Point the gateway LLM at a fake Meta Model API. Returns the requests it received."""
    requests = []

    def handler(request):
        requests.append(request)
        if status != 200:
            return httpx.Response(status, json={"error": {"message": "fake error"}})
        return httpx.Response(200, json={
            "id": "chatcmpl-test", "object": "chat.completion", "created": 0, "model": config.LLM_MODEL,
            "choices": [{"index": 0, "finish_reason": finish_reason,
                         "message": {"role": "assistant", "content": content, "refusal": refusal}}],
        })

    monkeypatch.delenv("MODEL_API_BASE_URL", raising=False)
    monkeypatch.setattr(llm, "_client", lambda: model_api.client(
        max_retries=0, http_client=httpx.Client(transport=httpx.MockTransport(handler))))
    return requests


def _nodes(schema):
    if isinstance(schema, dict):
        yield schema
        for value in schema.values():
            yield from _nodes(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from _nodes(value)


def assert_meta_strict(schema):
    """Meta's strict subset, else HTTP 400: plain object root, no allOf/oneOf, closed objects, every key required."""
    assert schema["type"] == "object" and not {"anyOf", "oneOf", "allOf", "enum", "not"} & schema.keys()
    for node in _nodes(schema):
        assert not {"allOf", "oneOf"} & node.keys()
        if "properties" in node:
            assert node.get("additionalProperties") is False
            assert set(node["required"]) == set(node["properties"])


@pytest.mark.parametrize("model", [SalesAgentOutput, _ParsedRules])
def test_request_is_a_strict_structured_output_call(monkeypatch, model):
    out = (SalesAgentOutput(action="propose_offer", message_to_buyer="Deal.", offer=OfferDraft(
        content_ids=["rpt_battery_2025#s2"], scope="Market share", tier="small_table", price_usdc=0.50))
        if model is SalesAgentOutput else _ParsedRules(tiers=[]))
    requests = fake_api(monkeypatch, content=out.model_dump_json())
    assert llm.structured_call("SYSTEM", "USER", model, effort="low") == out

    request = requests[0]
    assert str(request.url) == "https://api.meta.ai/v1/chat/completions"
    assert request.headers["authorization"] == "Bearer test-key"
    body = json.loads(request.content)
    assert body["model"] == config.LLM_MODEL and body["reasoning_effort"] == "low"
    assert body["messages"] == [{"role": "system", "content": "SYSTEM"}, {"role": "user", "content": "USER"}]
    assert body["response_format"]["type"] == "json_schema" and body["response_format"]["json_schema"]["strict"]
    assert_meta_strict(body["response_format"]["json_schema"]["schema"])


@pytest.mark.parametrize("answer", [
    {"status": 429}, {"status": 500}, {"status": 401},
    {"content": "not json"},
    {"content": '{"action": "propose_offer"}'},
    {"content": '{"action": "no_match", "message_to_buyer": "No."', "finish_reason": "length"},
    {"refusal": "I cannot help with that."},
])
def test_unusable_answers_raise_llm_error(monkeypatch, answer):
    fake_api(monkeypatch, **answer)
    with pytest.raises(llm.LLMError):
        llm.structured_call("SYSTEM", "USER", SalesAgentOutput)
