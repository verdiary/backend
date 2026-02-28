from llm.clients import OpenRouterClient
from llm.interfaces import LLMClient


class LLMProviderFactory:
    """Build LLM clients by provider name."""

    @staticmethod
    def create(provider: str = "openrouter") -> LLMClient:
        if provider == "openrouter":
            return OpenRouterClient()

        raise ValueError(f"Unsupported LLM provider: {provider}")
