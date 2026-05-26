from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.db import get_db
from src.core.config import settings
from src.models.memory import CoreMemory
from src.services.memory_service import search_archival_memory
from src.tasks import extract_and_store_memory_task

router = APIRouter()

def verify_worker(x_worker_key: str = Header(...)):
    if x_worker_key != settings.WORKER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid Worker Key")
    return True

class TranscriptRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    transcript: list[dict] = Field(..., max_length=5000) # Limit history to prevent massive payload processing

class SearchRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    query: str = Field(..., max_length=1000) # Prevent massive vector searches

@router.post("/session", dependencies=[Depends(verify_worker)])
async def save_session_memory(request: TranscriptRequest):
    # Kick off Celery background task to process the transcript and update Core/Archival memory
    extract_and_store_memory_task.delay(request.user_id, request.transcript)
    return {"status": "processing"}

@router.get("/core/{user_id}", dependencies=[Depends(verify_worker)])
async def get_core_memory(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CoreMemory).where(CoreMemory.user_id == user_id))
    memory = result.scalars().first()
    return {"persona": memory.persona if memory else ""}

@router.post("/search", dependencies=[Depends(verify_worker)])
async def search_memory(request: SearchRequest):
    results = await search_archival_memory(request.user_id, request.query)
    return {"results": results}
