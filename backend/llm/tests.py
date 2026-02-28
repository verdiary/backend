import json
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from llm.clients.openrouter import OpenRouterClient
from llm.errors import LLMRateLimitError


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@override_settings(
    OPENROUTER_API_KEY="test-key",
    LLM_DEFAULT_MODEL="openai/gpt-4o-mini",
    LLM_REQUEST_TIMEOUT_SECONDS=1,
    LLM_MAX_RETRIES=0,
)
class OpenRouterClientTests(SimpleTestCase):
    def test_chat_completion_sends_system_and_user_messages(self):
        with patch("urllib.request.urlopen", return_value=FakeResponse({"id": "ok"})) as mocked_urlopen:
            client = OpenRouterClient()
            result = client.chat_completion(
                messages=[{"role": "user", "content": "hi"}],
                system_message="be brief",
            )

        self.assertEqual(result["id"], "ok")
        request = mocked_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "openai/gpt-4o-mini")
        self.assertEqual(
            payload["messages"],
            [
                {"role": "system", "content": "be brief"},
                {"role": "user", "content": "hi"},
            ],
        )

    def test_rate_limit_maps_to_internal_error(self):
        from urllib.error import HTTPError
        from io import BytesIO

        error = HTTPError(
            url="https://example.com",
            code=429,
            msg="rate limit",
            hdrs=None,
            fp=BytesIO(b"{}"),
        )

        with patch("urllib.request.urlopen", side_effect=error):
            client = OpenRouterClient()
            with self.assertRaises(LLMRateLimitError):
                client.chat_completion(messages=[{"role": "user", "content": "hi"}])
