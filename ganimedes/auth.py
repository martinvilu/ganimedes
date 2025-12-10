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

# Cliente de Supabase (se inicializa solo si está configurado)
supabase: Optional[object] = None
SUPABASE_CONFIGURED = False

try:
    if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != "https://fake-url.supabase.co":
        from supabase import create_client, Client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        SUPABASE_CONFIGURED = True
    else:
        warnings.warn(
            "⚠️  Supabase no está configurado. Los endpoints de autenticación no funcionarán. "
            "Configura SUPABASE_URL y SUPABASE_KEY en .env",
            UserWarning
        )
except Exception as e:
    warnings.warn(
        f"⚠️  Error al conectar con Supabase: {e}. "
        "Los endpoints de autenticación no funcionarán.",
        UserWarning
    )

security = HTTPBearer(auto_error=False)


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
    if not SUPABASE_CONFIGURED or supabase is None:
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
    
    try:
        # Verificar token con Supabase
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
    if not SUPABASE_CONFIGURED or supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible. Supabase no está configurado.",
        )
    
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
    if not SUPABASE_CONFIGURED or supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticación no disponible. Supabase no está configurado.",
        )
    
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
