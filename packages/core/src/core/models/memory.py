from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ShortTermMemory(BaseModel):
    session_id: str
    recent_turns: List[Message] = Field(default_factory=list)
    active_goals: List[str] = Field(default_factory=list)

class SessionMemory(BaseModel):
    session_id: str
    summary: str = ""
    unresolved_tasks: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)

class LongTermMemory(BaseModel):
    user_id: str
    preferences: dict = Field(default_factory=dict)
    facts: List[str] = Field(default_factory=list)
