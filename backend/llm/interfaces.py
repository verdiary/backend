from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any


class LLMClient(ABC):
    """Provider-agnostic interface for chat completion clients."""

    @abstractmethod
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
        """Send a chat completion request and return raw provider response."""

    def stream_chat_completion(
        self,
        *,
        messages: list[dict[str, str]],
        system_message: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Optional streaming API; implementations may override this method."""
        raise NotImplementedError("Streaming is not supported by this client")

    def supports_tools(self) -> bool:
        """Optional capability flag for tool-calling requests."""
        return False
