import os
import subprocess
from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "voice_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task
def spawn_worker(room_name: str):
    """
    Spawns a new Pipecat worker process for the given room_name.
    It blocks the Celery worker until the Pipecat worker terminates (when the user leaves).
    """
    api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    import sys
    python_executable = sys.executable
    
    process = subprocess.Popen(
        [python_executable, "-m", "src.worker", "--room", room_name],
        cwd=api_dir,
        env=os.environ.copy()
    )
    
    # Wait for the worker to finish
    process.wait()
    
    return f"Worker for {room_name} finished."

@celery_app.task
def extract_and_store_memory_task(user_id: str, transcript: list):
    """
    Extracts core and archival memory from the session transcript in the background.
    """
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy.pool import NullPool
    from src.core.config import settings
    from src.services.memory_service import extract_memories
    
    async def _run():
        # Create a fresh engine for this specific event loop using NullPool for Celery workers
        engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
        session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        
        async with session_maker() as db:
            await extract_memories(user_id, transcript, db)
            
        await engine.dispose()
            
    asyncio.run(_run())
    return f"Memory extraction complete for user {user_id}"
