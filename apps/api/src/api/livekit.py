from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from livekit import api
import uuid
from ..core.config import settings
from ..core.logger import logger
from ..core.security import get_current_user
from ..models.user import User
from ..tasks import spawn_worker
from ..core.rate_limit import limiter

router = APIRouter()

class TokenResponse(BaseModel):
    token: str
    room_name: str

@router.post("/token", response_model=TokenResponse)
@limiter.limit("20/minute")
async def generate_token(request: Request, current_user: User = Depends(get_current_user)):
    try:
        # Generate a unique room for this session
        room_name = f"room-{current_user.id}-{uuid.uuid4().hex[:8]}"
        
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        ) \
        .with_identity(current_user.id) \
        .with_name(current_user.username) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
        ))

        jwt = token.to_jwt()

        # Dispatch a background Celery task to spawn the AI worker for this specific room
        spawn_worker.delay(room_name)

        await logger.ainfo("livekit_token_issued_and_worker_spawned", user_id=current_user.id, room_name=room_name)
        return TokenResponse(token=jwt, room_name=room_name)

    except Exception as e:
        await logger.aerror("livekit_token_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate token")
