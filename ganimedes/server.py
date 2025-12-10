"""Servidor FastAPI para Ganimedes."""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

from .auth import get_current_user, sign_up, sign_in, SUPABASE_CONFIGURED, MOCK_MODE
from .database import MonitorEvent, FocusSession
from .monitor import monitoring_service

load_dotenv()

app = FastAPI(
    title="Ganimedes",
    description="Sistema de monitoreo y proctorización para JupyterLite",
    version="0.1.0"
)

# Estado de la aplicación
APP_STATUS = {
    "supabase_configured": SUPABASE_CONFIGURED,
    "mock_mode": MOCK_MODE
}

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
    
    # Manejar tanto respuestas de Supabase (objeto) como Mock (dict)
    if isinstance(response, dict):
        return {
            "message": "Usuario registrado exitosamente",
            "user": response.get("user"),
            "session": response.get("session")
        }
    else:
        return {
            "message": "Usuario registrado exitosamente",
            "user": response.user,
            "session": response.session
        }


@app.post("/api/auth/signin")
async def signin(request: SignInRequest):
    """Inicia sesión de usuario."""
    response = sign_in(request.email, request.password)
    
    # Manejar tanto respuestas de Supabase (objeto) como Mock (dict)
    if isinstance(response, dict):
        return {
            "message": "Sesión iniciada exitosamente",
            "user": response.get("user"),
            "session": response.get("session")
        }
    else:
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
    if MOCK_MODE:
        status_msg = "🧪 Modo MOCK - autenticación en memoria para testing"
        status = "testing"
    elif SUPABASE_CONFIGURED:
        status_msg = "OK - Supabase configurado"
        status = "healthy"
    else:
        status_msg = "⚠️ Supabase no configurado - endpoints de autenticación no disponibles"
        status = "degraded"
    
    return {
        "status": status,
        "supabase_configured": SUPABASE_CONFIGURED,
        "mock_mode": MOCK_MODE,
        "timestamp": datetime.utcnow().isoformat(),
        "message": status_msg
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    """Página de inicio con información del estado."""
    if MOCK_MODE:
        status_icon = "🧪"
        status_text = "Modo MOCK (Testing)"
        status_color = "blue"
    elif SUPABASE_CONFIGURED:
        status_icon = "✅"
        status_text = "Configurado correctamente"
        status_color = "green"
    else:
        status_icon = "⚠️"
        status_text = "No configurado"
        status_color = "orange"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ganimedes - Sistema de Monitoreo</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2563eb;
                margin-bottom: 10px;
            }}
            .status {{
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                background: #fff3cd;
                border-left: 4px solid {status_color};
            }}
            .status.ok {{
                background: #d4edda;
                border-color: green;
            }}
            .links {{
                margin-top: 30px;
            }}
            .links a {{
                display: inline-block;
                margin: 10px 10px 10px 0;
                padding: 10px 20px;
                background: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .links a:hover {{
                background: #1e40af;
            }}
            code {{
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            .warning {{
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid orange;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛰️ Ganimedes</h1>
            <p>Sistema de Monitoreo y Proctorización para JupyterLite</p>
            
            <div class="status {'ok' if SUPABASE_CONFIGURED else ''}">
                <strong>{status_icon} Estado de Supabase:</strong> {status_text}
            </div>
            
            {'<div class="warning" style="background: #e3f2fd; border-color: blue;"><strong>🧪 Modo MOCK Activado</strong><br>El servidor está usando autenticación simulada en memoria para testing. Los datos no persisten.<br><br>Para usar Supabase real, configura en <code>.env</code>:<br><code>SUPABASE_URL=...</code><br><code>SUPABASE_KEY=...</code><br>y elimina <code>MOCK_AUTH=true</code></div>' if MOCK_MODE else '<div class="warning"><strong>⚠️ Configuración Requerida</strong><br>Para usar Ganimedes, configura en <code>.env</code>:<br><br><code>SUPABASE_URL=https://tu-proyecto.supabase.co</code><br><code>SUPABASE_KEY=tu-clave-anon</code><br><br>O usa modo MOCK para testing:<br><code>MOCK_AUTH=true</code><br><br>Luego reinicia el servidor.</div>' if not SUPABASE_CONFIGURED else ''}
            
            <h2>Recursos</h2>
            <div class="links">
                <a href="/docs">📚 Documentación API</a>
                <a href="/static/index.html">🎯 Dashboard</a>
                <a href="/api/health">❤️ Health Check</a>
                <a href="https://github.com/martinvilu/ganimedes">💻 GitHub</a>
            </div>
            
            <h2>Endpoints Disponibles</h2>
            <ul>
                <li><code>GET /api/health</code> - Estado del servidor</li>
                <li><code>POST /api/auth/signup</code> - Registro de usuario {'❌' if not SUPABASE_CONFIGURED else '✅'}</li>
                <li><code>POST /api/auth/signin</code> - Inicio de sesión {'❌' if not SUPABASE_CONFIGURED else '✅'}</li>
                <li><code>POST /api/monitor/event</code> - Registrar evento {'❌' if not SUPABASE_CONFIGURED else '✅'}</li>
            </ul>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #666; font-size: 14px;">
                Versión 0.1.0 | 
                <a href="https://github.com/martinvilu/ganimedes" style="color: #2563eb;">GitHub</a> |
                <a href="/docs" style="color: #2563eb;">API Docs</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html_content


def main():
    """Entry point for the CLI."""
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "ganimedes.server:app",
        host=host,
        port=port,
        reload=True
    )


if __name__ == "__main__":
    main()
