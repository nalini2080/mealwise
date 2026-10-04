"""Shared Gemini access: one client, structured JSON output, retries with backoff.

Used by photo scanning (vision.py) and recipe generation (recipe_ai.py).
"""

import logging
import time

from app.config import GEMINI_API_KEY, GEMINI_FALLBACK_MODEL, GEMINI_MODEL


class GeminiUnavailable(Exception):
    """No API key configured; the UI falls back to non-AI features."""


class GeminiFailed(Exception):
    """The model call failed or returned something unusable."""


# Free-tier Gemini occasionally answers 429 (rate limit) or 5xx (overloaded);
# those are worth retrying, anything else (bad key, bad request) is not.
# If the main model stays overloaded through every retry, we switch to a
# lighter fallback model, which usually has spare capacity.
RETRYABLE_CODES = {429, 500, 502, 503, 504}

log = logging.getLogger("mealwise.gemini")


class GeminiClient:
    def __init__(self, api_key: str | None = GEMINI_API_KEY, model: str = GEMINI_MODEL,
                 fallback_model: str | None = GEMINI_FALLBACK_MODEL,
                 client=None, retry_delays: tuple[float, ...] = (1.5, 4.0)):
        self.api_key = api_key
        self.models = [m for m in (model, fallback_model) if m]
        self._client = client
        self.retry_delays = retry_delays

    def _get_client(self):
        if not self.api_key:
            raise GeminiUnavailable("Set GEMINI_API_KEY in .env to enable AI features.")
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_json(self, contents: list, schema, temperature: float = 0.2):
        """Call Gemini with a response schema and return the parsed object(s)."""
        from google.genai import errors, types

        client = self._get_client()
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=temperature,
        )
        response = last_error = None
        for model in self.models:
            for delay in (*self.retry_delays, None):
                try:
                    response = client.models.generate_content(
                        model=model, contents=contents, config=config
                    )
                    break
                except errors.APIError as exc:
                    log.warning("Gemini %s error %s %s: %s", model, exc.code, exc.status, exc.message)
                    if exc.code not in RETRYABLE_CODES:
                        raise GeminiFailed(
                            f"Gemini request failed ({exc.code}). Please try again."
                        ) from exc
                    last_error = exc
                    if delay is not None:
                        time.sleep(delay)
            if response is not None:
                break

        if response is None:
            if last_error.code == 429:
                raise GeminiFailed(
                    "Gemini is busy (free-tier limit). Try again in a minute."
                ) from last_error
            raise GeminiFailed(
                "Gemini is overloaded right now (Google reports high demand). "
                "Try again in a minute."
            ) from last_error

        if response.parsed is None:
            candidate = (getattr(response, "candidates", None) or [None])[0]
            log.warning("Gemini returned unparseable output (finish_reason=%s)",
                        getattr(candidate, "finish_reason", None))
            raise GeminiFailed("Gemini returned a response we couldn't read. Please try again.")
        return response.parsed


gemini = GeminiClient()
