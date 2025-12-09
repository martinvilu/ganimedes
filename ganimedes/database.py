"""Database models and Supabase connection."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MonitorEvent(BaseModel):
    """Modelo para eventos de monitoreo."""
    
    id: Optional[str] = None
    user_id: str
    session_id: str
    event_type: str  # 'paste', 'focus', 'blur', 'activity'
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[dict] = None
    metadata: Optional[dict] = None


class FocusSession(BaseModel):
    """Modelo para sesiones de foco."""
    
    id: Optional[str] = None
    user_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_focus_time: int = 0  # en segundos
    paste_count: int = 0
    metadata: Optional[dict] = None


class User(BaseModel):
    """Modelo para usuario."""
    
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
