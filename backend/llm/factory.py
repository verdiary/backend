from llm.clients import OpenRouterClient
from llm.interfaces import LLMClient


class LLMProviderFactory:
    """Build LLM clients by provider name."""

    @staticmethod
    def create(provider: str = "openrouter") -> LLMClient:
        normalized_provider = provider.strip().lower()

        if normalized_provider == "openrouter":
            return OpenRouterClient()

        raise ValueError(f"Unsupported LLM provider: {provider}")
