import asyncio
import sys
import structlog
import os
import aiohttp
import argparse

from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.livekit.transport import LiveKitTransport, LiveKitParams
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.cartesia.tts import CartesiaTTSService

from src.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

async def main(room_name: str):
    if not settings.DEEPGRAM_API_KEY or not settings.GROQ_API_KEY or not settings.CARTESIA_API_KEY:
        await logger.aerror("missing_api_keys", error="DEEPGRAM_API_KEY, GROQ_API_KEY, or CARTESIA_API_KEY is not set.")
        sys.exit(1)

    from livekit import api
    token = api.AccessToken(
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET
    ).with_identity("assistant").with_name("Voice Assistant").with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
    )).to_jwt()

    transport = LiveKitTransport(
        room_name=room_name,
        token=token,
        url=settings.LIVEKIT_URL,
        params=LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True
        )
    )

    # Factory: STT Provider
    if settings.STT_PROVIDER == "deepgram":
        stt = DeepgramSTTService(api_key=settings.DEEPGRAM_API_KEY)
    else:
        raise ValueError(f"Unsupported STT provider: {settings.STT_PROVIDER}")

    # Factory: LLM Provider
    if settings.LLM_PROVIDER == "groq":
        llm = GroqLLMService(
            api_key=settings.GROQ_API_KEY,
            settings=GroqLLMService.Settings(model="llama-3.1-8b-instant")
        )
    elif settings.LLM_PROVIDER == "openai":
        from pipecat.services.openai.llm import OpenAILLMService
        llm = OpenAILLMService(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini"
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")

    # Factory: TTS Provider
    if settings.TTS_PROVIDER == "cartesia":
        tts = CartesiaTTSService(
            api_key=settings.CARTESIA_API_KEY,
            settings=CartesiaTTSService.Settings(voice="79a125e8-cd45-4c13-8a67-188112f4dd22")
        )
    elif settings.TTS_PROVIDER == "elevenlabs":
        from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
        tts = ElevenLabsTTSService(
            api_key=settings.ELEVENLABS_API_KEY,
            voice_id="EXAVITQu4vr4xnSDxMaL"
        )
    else:
        raise ValueError(f"Unsupported TTS provider: {settings.TTS_PROVIDER}")

    from pipecat.audio.vad.silero import SileroVADAnalyzer
    from pipecat.processors.audio.vad_processor import VADProcessor
    from pipecat.frames.frames import LLMMessagesUpdateFrame
    from pipecat.processors.aggregators.llm_context import LLMContext
    from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair

    from pipecat.adapters.schemas.tools_schema import ToolsSchema

    # Parse user_id reliably from the room name (e.g., room-user_xyz-1234)
    room_parts = room_name.split("-")
    if len(room_parts) >= 2:
        current_user_id = room_parts[1]
    else:
        current_user_id = "unknown"

    # Worker authentication headers
    worker_headers = {"X-Worker-Key": settings.WORKER_API_KEY}

    async def fetch_core_memory(user_id: str) -> str:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{settings.API_URL}/memory/core/{user_id}", headers=worker_headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("persona", "")
            except Exception as e:
                await logger.aerror(f"Error fetching core memory: {e}")
        return ""

    async def save_session_memory(user_id: str, transcript: list):
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(f"{settings.API_URL}/memory/session", json={"user_id": user_id, "transcript": transcript}, headers=worker_headers)
            except Exception as e:
                await logger.aerror(f"Error saving session memory: {e}")

    async def search_memory(params, query: str):
        """Use this tool ONLY to search for the user's personal past memories, preferences, and previous conversations. DO NOT use this tool for general knowledge, definitions, or world facts."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{settings.API_URL}/memory/search", json={"user_id": current_user_id, "query": query}, headers=worker_headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        if results:
                            await params.result_callback({"results": "\\n".join(results)})
                            return
            except Exception as e:
                await logger.aerror(f"Error searching memory: {e}")
        await params.result_callback({"results": "No relevant past memories found."})

    llm.register_direct_function(search_memory)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful voice assistant in a realtime voice chat. Keep your responses extremely concise and conversational. Do not use markdown, emojis, or symbols as your response will be read aloud by a text to speech system. Listen to the user and assist them. Be polite and professional. ONLY use the search_memory tool if the user explicitly asks about their past conversations, personal facts, or preferences. Do NOT use tools for general knowledge questions.",
        }
    ]

    context = LLMContext(messages=messages, tools=ToolsSchema(standard_tools=[search_memory]))
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(context)
    
    vad = VADProcessor(vad_analyzer=SileroVADAnalyzer())

    pipeline = Pipeline([
        transport.input(),   # WebRTC Audio from user
        vad,                 # Voice Activity Detection
        stt,                 # Deepgram Speech-to-Text
        user_aggregator,     # Add user input to context
        llm,                 # Groq LLM
        tts,                 # Cartesia Text-to-Speech
        transport.output(),  # WebRTC Audio to user
        assistant_aggregator # Add assistant output to context
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
        )
    )

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        await logger.ainfo("participant_connected_identity", participant=current_user_id)
        
        # Fetch Core Memory and inject it
        persona = await fetch_core_memory(current_user_id)
        if persona:
            context.add_message({"role": "system", "content": f"Core Memory about this user: {persona}"})
            
        context.add_message({"role": "system", "content": "The user has joined the room. Say hello!"})
        await task.queue_frames([LLMMessagesUpdateFrame(messages=context.get_messages(), run_llm=True)])

    @transport.event_handler("on_participant_disconnected")
    async def on_participant_disconnected(transport, participant):
        await logger.ainfo("participant_disconnected", participant=str(participant))
        
        # Save memory
        await save_session_memory(current_user_id, context.get_messages())
        
        # Shut down worker gracefully for this session
        await task.queue_frames([EndFrame()])
        await logger.ainfo("worker_shutting_down", room=room_name)

    runner = PipelineRunner()

    await logger.ainfo("starting_voice_pipeline")
    await runner.run(task)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Assistant Worker")
    parser.add_argument("--room", type=str, required=True, help="LiveKit Room Name")
    args = parser.parse_args()
    
    asyncio.run(main(args.room))
