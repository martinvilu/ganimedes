# Modo MOCK - Testing sin Supabase

Ganimedes incluye un modo MOCK que permite ejecutar y probar el servidor sin necesidad de configurar Supabase.

## ¿Qué es el Modo MOCK?

El modo MOCK simula toda la funcionalidad de autenticación y almacenamiento de datos en memoria, permitiéndote:
- ✅ Desarrollar y probar sin configurar Supabase
- ✅ Ejecutar tests automatizados
- ✅ Demostrar funcionalidad sin dependencias externas
- ✅ Desarrollo local rápido

## Activar Modo MOCK

### Opción 1: Variable de Entorno

```bash
export MOCK_AUTH=true
./scripts/dev.sh
```

### Opción 2: Archivo .env

```bash
# Crear o editar .env
echo "MOCK_AUTH=true" >> .env

# Iniciar servidor
./scripts/dev.sh
```

### Opción 3: Inline

```bash
MOCK_AUTH=true uv run python -m ganimedes.server
```

## Verificar Modo MOCK

### Health Check

```bash
curl http://localhost:8000/api/health
```

Respuesta esperada:
```json
{
  "status": "testing",
  "supabase_configured": true,
  "mock_mode": true,
  "timestamp": "2024-12-10T14:00:00.000Z",
  "message": "🧪 Modo MOCK - autenticación en memoria para testing"
}
```

### Página de Estado

Visita `http://localhost:8000/` y verás:

```
🛰️ Ganimedes
Estado de Supabase: 🧪 Modo MOCK (Testing)

🧪 Modo MOCK Activado
El servidor está usando autenticación simulada en memoria para testing.
Los datos no persisten.
```

## Funcionalidad en Modo MOCK

### Autenticación ✅

**Registro de Usuario**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Usuario de Prueba"
  }'
```

Respuesta:
```json
{
  "user": {
    "id": "mock-user-a1b2c3d4",
    "email": "test@example.com",
    "user_metadata": {
      "full_name": "Usuario de Prueba"
    }
  },
  "session": {
    "access_token": "mock-token-...",
    "token_type": "bearer"
  }
}
```

**Inicio de Sesión**
```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Usuario Actual**
```bash
# Usa el token de la respuesta anterior
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer mock-token-..."
```

### Monitoreo de Eventos ✅

**Registrar Evento**
```bash
curl -X POST http://localhost:8000/api/monitor/event \
  -H "Authorization: Bearer mock-token-..." \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "mock-user-a1b2c3d4",
    "session_id": "session-123",
    "event_type": "paste",
    "data": {
      "text_length": 100
    },
    "metadata": {
      "platform": "jupyterlite"
    }
  }'
```

**Obtener Eventos**
```bash
curl "http://localhost:8000/api/monitor/events?limit=10" \
  -H "Authorization: Bearer mock-token-..."
```

### Sesiones de Foco ✅

**Crear Sesión**
```bash
curl -X POST http://localhost:8000/api/monitor/session/start \
  -H "Authorization: Bearer mock-token-..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123"
  }'
```

**Finalizar Sesión**
```bash
curl -X PUT http://localhost:8000/api/monitor/session/end \
  -H "Authorization: Bearer mock-token-..." \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "focus_time": 3600
  }'
```

**Estadísticas**
```bash
curl http://localhost:8000/api/monitor/session/session-123/stats \
  -H "Authorization: Bearer mock-token-..."
```

## Limitaciones del Modo MOCK

⚠️ **Importante:** Los datos NO persisten

- ❌ **No hay persistencia**: Los datos se pierden al reiniciar el servidor
- ❌ **Sin encriptación real**: Las contraseñas no se hashean (solo para testing)
- ❌ **Tokens simples**: Los tokens no son JWT reales
- ❌ **Sin base de datos**: Todo está en memoria
- ❌ **Usuarios no sincronizados**: No hay validación real de email

✅ **Perfecto para:**
- Desarrollo local
- Tests automatizados
- Demostraciones
- CI/CD sin dependencias externas

## Ejemplo de Flujo Completo

```bash
# 1. Iniciar servidor en modo MOCK
export MOCK_AUTH=true
uv run python -m ganimedes.server &

# 2. Registrar usuario
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}')

# 3. Extraer token
TOKEN=$(echo $SIGNUP_RESPONSE | jq -r '.session.access_token')

# 4. Registrar evento
curl -X POST http://localhost:8000/api/monitor/event \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"'$(echo $SIGNUP_RESPONSE | jq -r '.user.id')'",
    "session_id":"test-session",
    "event_type":"paste",
    "data":{"test":true}
  }'

# 5. Ver eventos
curl http://localhost:8000/api/monitor/events \
  -H "Authorization: Bearer $TOKEN"

# 6. Detener servidor
pkill -f "python -m ganimedes.server"
```

## Switching entre Modos

### De MOCK a Supabase Real

1. Eliminar o comentar `MOCK_AUTH` del `.env`
2. Configurar credenciales reales de Supabase
3. Reiniciar el servidor

```bash
# .env
# MOCK_AUTH=true  ← Comentar esta línea
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-real
```

### De Supabase a MOCK

1. Agregar `MOCK_AUTH=true` al `.env`
2. Reiniciar el servidor

```bash
# .env
MOCK_AUTH=true  ← Agregar esta línea
```

⚠️ Nota: El modo MOCK tiene prioridad sobre Supabase si ambos están configurados.

## Tests Automatizados

Ejemplo de test con pytest:

```python
import os
import pytest
from fastapi.testclient import TestClient

# Activar modo MOCK
os.environ["MOCK_AUTH"] = "true"

from ganimedes.server import app

client = TestClient(app)

def test_signup_and_signin():
    # Registro
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "session" in data
    
    # Login
    response = client.post("/api/auth/signin", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    
def test_monitor_event():
    # Registrar usuario y obtener token
    response = client.post("/api/auth/signup", json={
        "email": "monitor@example.com",
        "password": "pass123"
    })
    token = response.json()["session"]["access_token"]
    user_id = response.json()["user"]["id"]
    
    # Registrar evento
    response = client.post("/api/monitor/event", 
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": user_id,
            "session_id": "test-session",
            "event_type": "paste",
            "data": {"test": True}
        }
    )
    assert response.status_code == 200
```

## Troubleshooting

### El servidor sigue pidiendo Supabase

```bash
# Verificar que MOCK_AUTH está configurado
echo $MOCK_AUTH  # Debe mostrar: true

# O verificar en el código
python -c "import os; print('MOCK_AUTH:', os.getenv('MOCK_AUTH'))"
```

### Los datos desaparecen

Esto es normal - el modo MOCK usa memoria RAM. Los datos se pierden al:
- Reiniciar el servidor
- Cerrar la terminal
- Cambiar de código (modo watch)

Para datos persistentes, usa Supabase real.

### ¿Puedo usar MOCK en producción?

❌ **NO**. El modo MOCK es SOLO para:
- Desarrollo local
- Testing
- CI/CD
- Demostraciones

Para producción, SIEMPRE configura Supabase real.

## Recursos

- [SETUP.md](SETUP.md) - Configuración de Supabase real
- [README.md](README.md) - Documentación principal
- [API Docs](http://localhost:8000/docs) - Documentación interactiva de la API

## Soporte

Si encuentras problemas con el modo MOCK:
- Issues: https://github.com/martinvilu/ganimedes/issues
- Documentación: https://github.com/martinvilu/ganimedes
