from typing import Protocol, AsyncGenerator

class STTProvider(Protocol):
    async def connect(self) -> None:
        """Connect to the STT provider."""
        ...

    async def stream_audio(self, audio_chunk: bytes) -> None:
        """Stream raw audio chunk to the STT provider."""
        ...

    async def receive_transcript(self) -> AsyncGenerator[dict, None]:
        """Receive partial and final transcripts from the provider.
        Yields a dict with at least:
        - text: str
        - is_final: bool
        """
        ...

    async def close(self) -> None:
        """Close the connection to the STT provider."""
        ...
