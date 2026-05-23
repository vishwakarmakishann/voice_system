from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.db import get_db
from src.models.memory import CoreMemory
from src.services.memory_service import extract_memories, search_archival_memory

router = APIRouter()

class TranscriptRequest(BaseModel):
    user_id: str
    transcript: list[dict]

class SearchRequest(BaseModel):
    user_id: str
    query: str

@router.post("/session")
async def save_session_memory(
    request: TranscriptRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Kick off background task to process the transcript and update Core/Archival memory
    background_tasks.add_task(extract_memories, request.user_id, request.transcript, db)
    return {"status": "processing"}

@router.get("/core/{user_id}")
async def get_core_memory(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CoreMemory).where(CoreMemory.user_id == user_id))
    memory = result.scalars().first()
    return {"persona": memory.persona if memory else ""}

@router.post("/search")
async def search_memory(request: SearchRequest):
    results = await search_archival_memory(request.user_id, request.query)
    return {"results": results}
