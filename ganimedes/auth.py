"""Autenticación con Supabase."""

import os
import warnings
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MOCK_MODE = os.getenv("MOCK_AUTH", "false").lower() == "true"

# Cliente de Supabase (se inicializa solo si está configurado)
supabase: Optional[object] = None
SUPABASE_CONFIGURED = False

# Almacenamiento en memoria para modo mock
if MOCK_MODE:
    MOCK_USERS = {}
    MOCK_TOKENS = {}
    warnings.warn(
        "🧪 Modo MOCK activado. Usando autenticación simulada en memoria.",
        UserWarning
    )
    SUPABASE_CONFIGURED = True  # Consideramos "configurado" en modo mock
else:
    try:
        if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "https://fake-url.supabase.co":
            from supabase import create_client, Client
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            SUPABASE_CONFIGURED = True
        else:
            warnings.warn(
                "⚠️  Supabase no está configurado. Los endpoints de autenticación no funcionarán. "
                "Configura SUPABASE_URL y SUPABASE_KEY en .env o usa MOCK_AUTH=true",
                UserWarning
            )
    except Exception as e:
        warnings.warn(
            f"⚠️  Error al conectar con Supabase: {e}. "
            "Los endpoints de autenticación no funcionarán. Puedes usar MOCK_AUTH=true para testing.",
            UserWarning
        )

security = HTTPBearer(auto_error=False)


def _mock_get_user(token: str) -> Optional[dict]:
    """Obtiene usuario desde almacenamiento mock."""
    if not MOCK_MODE:
        return None
    return MOCK_TOKENS.get(token)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> dict:
    """
    Valida el token JWT y retorna el usuario actual.
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        dict: Datos del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o Supabase no está configurado
    """
    if not SUPABASE_CONFIGURED and not MOCK_MODE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible. Supabase no está configurado.",
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación requeridas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Modo MOCK
    if MOCK_MODE:
        user = _mock_get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    
    # Modo Supabase real
    try:
        user = supabase.auth.get_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user.user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def sign_up(email: str, password: str, full_name: Optional[str] = None) -> dict:
    """Registra un nuevo usuario."""
    if not SUPABASE_CONFIGURED and not MOCK_MODE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible. Supabase no está configurado.",
        )
    
    # Modo MOCK
    if MOCK_MODE:
        import secrets
        if email in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya existe"
            )
        
        user_id = f"mock-user-{secrets.token_hex(8)}"
        token = f"mock-token-{secrets.token_hex(16)}"
        
        user_data = {
            "id": user_id,
            "email": email,
            "user_metadata": {"full_name": full_name} if full_name else {}
        }
        
        MOCK_USERS[email] = {
            "password": password,  # En producción se hashearía
            "user": user_data
        }
        MOCK_TOKENS[token] = user_data
        
        return {
            "user": user_data,
            "session": {
                "access_token": token,
                "token_type": "bearer"
            }
        }
    
    # Modo Supabase real
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"full_name": full_name} if full_name else {}
            }
        })
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar usuario: {str(e)}"
        )


def sign_in(email: str, password: str) -> dict:
    """Inicia sesión de usuario."""
    if not SUPABASE_CONFIGURED and not MOCK_MODE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible. Supabase no está configurado.",
        )
    
    # Modo MOCK
    if MOCK_MODE:
        import secrets
        user_entry = MOCK_USERS.get(email)
        
        if not user_entry or user_entry["password"] != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        token = f"mock-token-{secrets.token_hex(16)}"
        MOCK_TOKENS[token] = user_entry["user"]
        
        return {
            "user": user_entry["user"],
            "session": {
                "access_token": token,
                "token_type": "bearer"
            }
        }
    
    # Modo Supabase real
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credenciales inválidas: {str(e)}"
        )
