from typing import Protocol, AsyncGenerator, Any

class LLMProvider(Protocol):
    async def generate_stream(self, messages: list[dict], **kwargs: Any) -> AsyncGenerator[dict, None]:
        """Generate a streaming response from the LLM.
        Yields a dict containing token, tool calls, etc.
        """
        ...

    async def cancel(self) -> None:
        """Cancel the current generation."""
        ...
