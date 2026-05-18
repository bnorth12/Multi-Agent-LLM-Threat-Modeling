"""Custom exception for LLM provider errors, including retryable classification."""

class LlmProviderError(Exception):
    def __init__(self, message: str, code: int | None = None, retryable: bool = False, wait_seconds: int | None = None):
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.wait_seconds = wait_seconds
