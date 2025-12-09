# Guía de Configuración - Ganimedes

## 1. Requisitos Previos

- Python 3.11 o superior
- [uv](https://github.com/astral-sh/uv) instalado
- Cuenta en [Supabase](https://supabase.com)

## 2. Configuración de Supabase

### 2.1 Crear un Proyecto

1. Ve a [https://app.supabase.com](https://app.supabase.com)
2. Crea un nuevo proyecto
3. Anota la URL y las API Keys

### 2.2 Configurar la Base de Datos

1. En tu proyecto de Supabase, ve a SQL Editor
2. Ejecuta el contenido del archivo `supabase-schema.sql`
3. Esto creará las tablas `monitor_events` y `focus_sessions` con sus índices y políticas de seguridad

### 2.3 Habilitar Autenticación por Email

1. Ve a Authentication → Settings
2. Habilita "Enable Email Signup"
3. Configura el template de emails si lo deseas

## 3. Configuración Local

### 3.1 Clonar el Repositorio

```bash
git clone <repository-url>
cd ganimedes
```

### 3.2 Instalar Dependencias

```bash
# Instalar dependencias con uv
uv sync

# Activar el entorno virtual
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows
```

### 3.3 Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o usa tu editor preferido
```

Configurar las siguientes variables:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anon-key
SECRET_KEY=una-clave-secreta-aleatoria
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
```

### 3.4 Generar una Clave Secreta

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Usa el resultado como `SECRET_KEY` en tu `.env`

## 4. Ejecutar el Servidor

### Modo Desarrollo

```bash
# Con uv
uv run python -m ganimedes.server

# O con Python directamente (con entorno activado)
python -m ganimedes.server
```

El servidor estará disponible en `http://localhost:8000`

### Modo Producción

```bash
uv run uvicorn ganimedes.server:app --host 0.0.0.0 --port 8000
```

## 5. Probar la Aplicación

1. Abre tu navegador en `http://localhost:8000/static/index.html`
2. Regístrate con un nuevo usuario
3. Inicia sesión
4. Prueba pegando texto en el editor de código
5. Observa los eventos registrados en tiempo real

## 6. Desarrollo con Dependencias Adicionales

### Instalar Herramientas de Desarrollo

```bash
uv sync --extra dev
```

Esto instalará:
- pytest (testing)
- black (formateo de código)
- ruff (linting)
- httpx (testing de HTTP)

### Ejecutar Tests

```bash
uv run pytest
```

### Formatear Código

```bash
uv run black .
```

### Linting

```bash
uv run ruff check .
```

## 7. Verificación de la Configuración

### Probar la Conexión a Supabase

```python
from ganimedes.auth import supabase

# Esto debería conectarse sin errores
response = supabase.table('monitor_events').select('*').limit(1).execute()
print("Conexión exitosa!")
```

### Probar el Health Check

```bash
curl http://localhost:8000/api/health
```

Deberías recibir:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-09T..."
}
```

## 8. Solución de Problemas

### Error: "SUPABASE_URL y SUPABASE_KEY deben estar configurados"

- Verifica que el archivo `.env` existe
- Verifica que las variables están correctamente definidas
- Reinicia el servidor

### Error de Autenticación

- Verifica que las credenciales de Supabase son correctas
- Verifica que el usuario está habilitado en Supabase
- Revisa los logs de Supabase Authentication

### Error al Crear Tablas

- Asegúrate de ejecutar `supabase-schema.sql` en el SQL Editor de Supabase
- Verifica que tienes permisos de administrador en el proyecto

### El Frontend no se Carga

- Verifica que la ruta sea `http://localhost:8000/static/index.html`
- Verifica que la carpeta `frontend/` existe
- Revisa los logs del servidor

## 9. Despliegue en Producción

### Recomendaciones

1. **Usar HTTPS**: Siempre usa HTTPS en producción
2. **Variables de Entorno**: Nunca commitas el archivo `.env`
3. **CORS**: Configura dominios específicos en `server.py`
4. **Rate Limiting**: Implementa rate limiting para las APIs
5. **Logging**: Configura logging apropiado
6. **Monitoring**: Usa herramientas como Sentry o DataDog

### Plataformas Recomendadas

- **Railway**: Deployment automático con Git
- **Fly.io**: Global deployment
- **DigitalOcean App Platform**: Fácil configuración
- **Heroku**: Con buildpack de Python

## 10. Recursos Adicionales

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Supabase](https://supabase.com/docs)
- [Documentación de uv](https://github.com/astral-sh/uv)
- [Guía de Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
