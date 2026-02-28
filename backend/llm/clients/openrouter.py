import json
import socket
import time
import urllib.error
import urllib.request
from typing import Any

from django.conf import settings

from llm.errors import LLMProviderError, LLMRateLimitError, LLMTimeoutError
from llm.interfaces import LLMClient


class OpenRouterClient(LLMClient):
    """OpenRouter adapter implementing the provider-agnostic LLM interface."""

    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str | None = None,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.default_model = default_model or settings.LLM_DEFAULT_MODEL
        self.timeout_seconds = timeout_seconds or settings.LLM_REQUEST_TIMEOUT_SECONDS
        self.max_retries = max_retries if max_retries is not None else settings.LLM_MAX_RETRIES

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouterClient")

    def chat_completion(
        self,
        *,
        messages: list[dict[str, str]],
        system_message: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        request_messages = self._compose_messages(messages, system_message)
        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": request_messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        if tools:
            payload["tools"] = tools

        return self._post_with_retries(payload)

    def supports_tools(self) -> bool:
        return True

    def _compose_messages(
        self, messages: list[dict[str, str]], system_message: str | None
    ) -> list[dict[str, str]]:
        composed_messages: list[dict[str, str]] = []
        if system_message:
            composed_messages.append({"role": "system", "content": system_message})
        composed_messages.extend(messages)
        return composed_messages

    def _post_with_retries(self, payload: dict[str, Any]) -> dict[str, Any]:
        encoded_payload = json.dumps(payload).encode("utf-8")

        for attempt in range(self.max_retries + 1):
            try:
                request = urllib.request.Request(
                    self.endpoint,
                    data=encoded_payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout_seconds,
                ) as response:
                    raw_body = response.read().decode("utf-8")
                    parsed = json.loads(raw_body)
                    return parsed
            except urllib.error.HTTPError as error:
                if error.code == 429:
                    if attempt < self.max_retries:
                        time.sleep(2**attempt)
                        continue
                    raise LLMRateLimitError("OpenRouter rate limit exceeded") from error

                error_body = error.read().decode("utf-8", errors="replace")
                raise LLMProviderError(
                    f"OpenRouter request failed: {error_body}",
                    status_code=error.code,
                ) from error
            except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
                if attempt < self.max_retries:
                    time.sleep(2**attempt)
                    continue
                raise LLMTimeoutError("OpenRouter request timed out") from error
            except json.JSONDecodeError as error:
                raise LLMProviderError("Failed to decode OpenRouter response") from error
