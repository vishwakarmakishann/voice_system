import asyncio
import sys
import structlog
import os
import aiohttp

from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.livekit.transport import LiveKitTransport, LiveKitParams
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.cartesia.tts import CartesiaTTSService

from src.config import settings
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

async def main():
    if not settings.DEEPGRAM_API_KEY or not settings.GROQ_API_KEY or not settings.CARTESIA_API_KEY:
        await logger.aerror("missing_api_keys", error="DEEPGRAM_API_KEY, GROQ_API_KEY, or CARTESIA_API_KEY is not set.")
        sys.exit(1)

    from livekit import api
    token = api.AccessToken(
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET
    ).with_identity("assistant").with_name("Voice Assistant").with_grants(api.VideoGrants(
        room_join=True,
        room="voice-room",
    )).to_jwt()

    transport = LiveKitTransport(
        room_name="voice-room",
        token=token,
        url=settings.LIVEKIT_URL,
        params=LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True
        )
    )

    stt = DeepgramSTTService(api_key=settings.DEEPGRAM_API_KEY)
    llm = GroqLLMService(
        api_key=settings.GROQ_API_KEY,
        settings=GroqLLMService.Settings(model="llama-3.1-8b-instant")
    )
    tts = CartesiaTTSService(
        api_key=settings.CARTESIA_API_KEY,
        settings=CartesiaTTSService.Settings(voice="79a125e8-cd45-4c13-8a67-188112f4dd22")
    )

    from pipecat.audio.vad.silero import SileroVADAnalyzer
    from pipecat.processors.audio.vad_processor import VADProcessor
    from pipecat.frames.frames import LLMMessagesUpdateFrame
    from pipecat.processors.aggregators.llm_context import LLMContext
    from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair

    from pipecat.adapters.schemas.tools_schema import ToolsSchema

    current_user_id = "unknown"

    async def fetch_core_memory(user_id: str) -> str:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"http://localhost:8000/memory/core/{user_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("persona", "")
            except Exception as e:
                await logger.aerror(f"Error fetching core memory: {e}")
        return ""

    async def save_session_memory(user_id: str, transcript: list):
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(f"http://localhost:8000/memory/session", json={"user_id": user_id, "transcript": transcript})
            except Exception as e:
                await logger.aerror(f"Error saving session memory: {e}")

    async def search_memory(params, query: str):
        """Search the user's archival memory for past facts or events."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"http://localhost:8000/memory/search", json={"user_id": current_user_id, "query": query}) as response:
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
            "content": "You are a helpful voice assistant in a realtime voice chat. Keep your responses extremely concise and conversational. Do not use markdown, emojis, or symbols as your response will be read aloud by a text to speech system. Listen to the user and assist them. Be polite and professional.",
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

    @transport.event_handler("on_participant_connected")
    async def on_participant_connected(transport, participant_sid):
        nonlocal current_user_id
        
        # pipecat passes the participant_sid (e.g. PA_...)
        # We need to get the actual identity from the room
        await asyncio.sleep(0.5) # Wait for LiveKit to update the participants dict
        
        participant_obj = transport._client.room.remote_participants.get(participant_sid)
        if participant_obj:
            current_user_id = participant_obj.identity
        else:
            # Fallback: get the first remote participant
            participants = list(transport._client.room.remote_participants.values())
            if participants:
                current_user_id = participants[0].identity
            else:
                current_user_id = str(participant_sid)
        
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
        
        # Reset the context so the next user starts fresh
        context.set_messages([
            {
                "role": "system",
                "content": "You are a helpful voice assistant in a realtime voice chat. Keep your responses extremely concise and conversational. Do not use markdown, emojis, or symbols as your response will be read aloud by a text to speech system. Listen to the user and assist them. Be polite and professional.",
            }
        ])
        await logger.ainfo("context_reset_for_next_user")
        # Notice we removed EndFrame() so the worker stays alive!

    runner = PipelineRunner()

    await logger.ainfo("starting_voice_pipeline")
    await runner.run(task)

if __name__ == "__main__":
    asyncio.run(main())
