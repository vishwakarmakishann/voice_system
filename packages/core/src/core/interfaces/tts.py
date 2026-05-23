from typing import Protocol, AsyncGenerator

class TTSProvider(Protocol):
    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Synthesize text into a stream of audio bytes."""
        ...

    async def cancel(self) -> None:
        """Cancel the ongoing synthesis and stop streaming."""
        ...
