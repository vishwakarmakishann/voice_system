from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from livekit import api
from ..core.config import settings
from ..core.logger import logger

router = APIRouter()

class TokenRequest(BaseModel):
    user_id: str
    room_name: str

class TokenResponse(BaseModel):
    token: str

@router.post("/token", response_model=TokenResponse)
async def generate_token(request: TokenRequest):
    try:
        token = api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        ) \
        .with_identity(request.user_id) \
        .with_name(f"User {request.user_id}") \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=request.room_name,
        ))

        jwt = token.to_jwt()

        await logger.ainfo("livekit_token_issued", user_id=request.user_id, room_name=request.room_name)
        return TokenResponse(token=jwt)

    except Exception as e:
        await logger.aerror("livekit_token_error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate token")
