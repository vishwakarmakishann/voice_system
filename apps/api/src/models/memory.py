from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime
from src.core.db import Base

class CoreMemory(Base):
    __tablename__ = "core_memory"
    
    user_id = Column(String, primary_key=True, index=True)
    persona = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
