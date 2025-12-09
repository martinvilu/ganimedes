"""Servidor FastAPI para Ganimedes."""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

from .auth import get_current_user, sign_up, sign_in
from .database import MonitorEvent, FocusSession
from .monitor import monitoring_service

load_dotenv()

app = FastAPI(
    title="Ganimedes",
    description="Sistema de monitoreo y proctorización para JupyterLite",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# Modelos de request
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class EventRequest(BaseModel):
    session_id: str
    event_type: str
    data: Optional[dict] = None
    metadata: Optional[dict] = None


class FocusSessionRequest(BaseModel):
    session_id: str
    metadata: Optional[dict] = None


class UpdateSessionRequest(BaseModel):
    session_id: str
    total_focus_time: int
    paste_count: int


# Endpoints de autenticación
@app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest):
    """Registra un nuevo usuario."""
    response = sign_up(request.email, request.password, request.full_name)
    return {
        "message": "Usuario registrado exitosamente",
        "user": response.user,
        "session": response.session
    }


@app.post("/api/auth/signin")
async def signin(request: SignInRequest):
    """Inicia sesión de usuario."""
    response = sign_in(request.email, request.password)
    return {
        "message": "Sesión iniciada exitosamente",
        "user": response.user,
        "session": response.session
    }


@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Obtiene información del usuario actual."""
    return {"user": current_user}


# Endpoints de monitoreo
@app.post("/api/monitor/event")
async def record_event(
    request: EventRequest,
    current_user: dict = Depends(get_current_user)
):
    """Registra un evento de monitoreo."""
    event = MonitorEvent(
        user_id=current_user.id,
        session_id=request.session_id,
        event_type=request.event_type,
        data=request.data,
        metadata=request.metadata
    )
    
    result = await monitoring_service.record_event(event)
    return {"message": "Evento registrado", "event": result}


@app.get("/api/monitor/events")
async def get_events(
    session_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Obtiene eventos del usuario."""
    events = await monitoring_service.get_events(
        user_id=current_user.id,
        session_id=session_id,
        event_type=event_type,
        limit=limit
    )
    return {"events": events}


@app.post("/api/monitor/session/start")
async def start_focus_session(
    request: FocusSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Inicia una nueva sesión de foco."""
    session = FocusSession(
        user_id=current_user.id,
        session_id=request.session_id,
        start_time=datetime.utcnow(),
        metadata=request.metadata
    )
    
    result = await monitoring_service.create_focus_session(session)
    return {"message": "Sesión iniciada", "session": result}


@app.put("/api/monitor/session/end")
async def end_focus_session(
    request: UpdateSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Finaliza una sesión de foco."""
    result = await monitoring_service.update_focus_session(
        session_id=request.session_id,
        end_time=datetime.utcnow(),
        total_focus_time=request.total_focus_time,
        paste_count=request.paste_count
    )
    return {"message": "Sesión finalizada", "session": result}


@app.get("/api/monitor/session/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtiene estadísticas de una sesión."""
    stats = await monitoring_service.get_session_stats(
        user_id=current_user.id,
        session_id=session_id
    )
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    return stats


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "ganimedes.server:app",
        host=host,
        port=port,
        reload=True
    )
