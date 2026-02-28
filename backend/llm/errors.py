class LLMClientError(Exception):
    """Base error class for all LLM client failures."""


class LLMTimeoutError(LLMClientError):
    """Raised when provider request times out."""


class LLMRateLimitError(LLMClientError):
    """Raised when provider rate limits a request."""


class LLMProviderError(LLMClientError):
    """Raised for provider-side errors or malformed responses."""

    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
