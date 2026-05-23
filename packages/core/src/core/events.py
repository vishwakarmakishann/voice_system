from pydantic import BaseModel
from typing import Optional

class BaseEvent(BaseModel):
    session_id: str
    trace_id: Optional[str] = None

class UserStartedSpeaking(BaseEvent):
    pass

class UserStoppedSpeaking(BaseEvent):
    pass

class AssistantStartedSpeaking(BaseEvent):
    pass

class AssistantStoppedSpeaking(BaseEvent):
    pass

class InterruptionOccurred(BaseEvent):
    pass

class ToolExecutionRequested(BaseEvent):
    tool_name: str
    arguments: dict

class ToolExecutionCompleted(BaseEvent):
    tool_name: str
    result: dict
