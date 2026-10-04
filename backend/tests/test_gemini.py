"""GeminiClient retry behavior, using a stub SDK client (no network)."""

import pytest
from google.genai import errors

from app.gemini import GeminiClient, GeminiFailed, GeminiUnavailable


class StubModels:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0
        self.models_used = []

    def generate_content(self, **kwargs):
        self.calls += 1
        self.models_used.append(kwargs["model"])
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class StubResponse:
    def __init__(self, parsed):
        self.parsed = parsed


def api_error(code):
    return errors.APIError(code, {"error": {"code": code, "message": "nope", "status": "X"}})


def make_client(outcomes, fallback=None):
    sdk = type("Client", (), {})()
    sdk.models = StubModels(outcomes)
    client = GeminiClient(api_key="test", model="main", fallback_model=fallback,
                          client=sdk, retry_delays=(0, 0))
    return client, sdk.models


def test_returns_parsed_value():
    client, models = make_client([StubResponse(["eggs"])])
    assert client.generate_json(["hi"], list[str]) == ["eggs"]
    assert models.calls == 1


def test_retries_transient_errors_then_succeeds():
    client, models = make_client([api_error(503), api_error(429), StubResponse(["eggs"])])
    assert client.generate_json(["hi"], list[str]) == ["eggs"]
    assert models.calls == 3


def test_gives_up_after_retries_with_friendly_message():
    client, models = make_client([api_error(429)] * 3)
    with pytest.raises(GeminiFailed, match="busy"):
        client.generate_json(["hi"], list[str])
    assert models.calls == 3


def test_switches_to_fallback_model_when_main_stays_overloaded():
    client, models = make_client([api_error(503)] * 3 + [StubResponse(["eggs"])], fallback="lite")
    assert client.generate_json(["hi"], list[str]) == ["eggs"]
    assert models.models_used == ["main", "main", "main", "lite"]


def test_overloaded_everywhere_gives_friendly_message():
    client, models = make_client([api_error(503)] * 6, fallback="lite")
    with pytest.raises(GeminiFailed, match="overloaded"):
        client.generate_json(["hi"], list[str])
    assert models.calls == 6


def test_does_not_retry_client_errors():
    client, models = make_client([api_error(400)], fallback="lite")
    with pytest.raises(GeminiFailed):
        client.generate_json(["hi"], list[str])
    assert models.calls == 1


def test_unparseable_response_fails():
    client, _ = make_client([StubResponse(None)])
    with pytest.raises(GeminiFailed):
        client.generate_json(["hi"], list[str])


def test_missing_key_is_unavailable():
    with pytest.raises(GeminiUnavailable):
        GeminiClient(api_key=None).generate_json(["hi"], list[str])
