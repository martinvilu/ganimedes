# Ganimedes 🛰️

Sistema de monitoreo y proctorización para instancias JupyterLite.

## Características

- 🔐 **Autenticación con Supabase**: Login seguro con JWT
- 📊 **Monitoreo de eventos de pegado**: Detecta cuando se pega código
- ⏱️ **Seguimiento de tiempo de foco**: Registra cuánto tiempo el usuario está activo
- 🎯 **Proctorización de exámenes**: Ideal para supervisar evaluaciones remotas
- 🚀 **Desarrollo con uv**: Gestión moderna de dependencias
- 🔒 **Row Level Security**: Políticas de seguridad a nivel de base de datos

## Inicio Rápido

### 1. Instalar uv (si no lo tienes)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clonar y configurar

```bash
# Clonar repositorio
git clone https://github.com/martinvilu/ganimedes.git
cd ganimedes

# Instalar dependencias
uv sync

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase
```

### 3. Configurar Supabase

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Ejecuta el contenido de `supabase-schema.sql` en SQL Editor
3. Copia la URL y API Key a tu archivo `.env`

### 4. Ejecutar

```bash
# Usar el script de desarrollo
./scripts/dev.sh

# O manualmente
uv run python -m ganimedes.server
```

Abre `http://localhost:8000/static/index.html` en tu navegador.

## Requisitos

- Python >= 3.11
- uv (gestor de paquetes)
- Cuenta en Supabase (gratuita)

## Desarrollo

### Con uv

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows

# Ejecutar servidor de desarrollo
uv run python -m ganimedes.server

# Ejecutar tests
./scripts/test.sh
```

### Con Conda

```bash
# Crear ambiente de desarrollo
conda env create -f environment-dev.yml
conda activate ganimedes-dev

# Ejecutar servidor
ganimedes
# O
python -m ganimedes.server
```

## Construcción de Paquetes

### Paquete Wheel (Recomendado)

```bash
# Construir paquete wheel (.whl) y tarball (.tar.gz)
./scripts/build-wheel.sh

# Los paquetes se generan en dist/
# - ganimedes-0.1.0-py3-none-any.whl
# - ganimedes-0.1.0.tar.gz

# Instalar localmente
pip install dist/ganimedes-0.1.0-py3-none-any.whl
```

### Paquete Conda (Experimental)

Ver [CONDA_BUILD.md](CONDA_BUILD.md) para instrucciones detalladas.

**Nota**: Actualmente hay problemas con conda-build en sistemas con conda 
instalado como paquete del sistema. Se recomienda usar el paquete wheel.

```bash
# Construir paquete .conda (puede fallar en algunas configuraciones)
./scripts/build-conda.sh

# Probar paquete
./scripts/test-conda-package.sh

# Subir a Anaconda.org
./scripts/upload-conda.sh
```

## Estructura del Proyecto

```
ganimedes/
├── ganimedes/          # Código fuente
│   ├── __init__.py
│   ├── server.py       # Servidor FastAPI
│   ├── auth.py         # Autenticación Supabase
│   ├── monitor.py      # Sistema de monitoreo
│   └── database.py     # Modelos y conexión DB
├── frontend/           # Frontend con JupyterLite
│   ├── index.html
│   ├── monitor.js      # Script de monitoreo
│   └── styles.css
├── scripts/            # Scripts de utilidad
│   ├── dev.sh          # Servidor de desarrollo
│   └── test.sh         # Ejecutar tests
├── tests/              # Tests
├── .env.example        # Ejemplo de variables de entorno
├── pyproject.toml      # Configuración del proyecto
├── SETUP.md            # Guía de configuración detallada
├── JUPYTERLITE_INTEGRATION.md  # Guía de integración con JupyterLite
└── README.md
```

## Variables de Entorno

- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_KEY`: API Key de Supabase
- `SECRET_KEY`: Clave secreta para JWT
- `ENVIRONMENT`: development/production
- `HOST`: Host del servidor (default: 0.0.0.0)
- `PORT`: Puerto del servidor (default: 8000)

## Documentación

- [SETUP.md](SETUP.md): Guía completa de configuración
- [JUPYTERLITE_INTEGRATION.md](JUPYTERLITE_INTEGRATION.md): Cómo integrar con JupyterLite real

## API Endpoints

### Autenticación

- `POST /api/auth/signup`: Registrar nuevo usuario
- `POST /api/auth/signin`: Iniciar sesión
- `GET /api/auth/me`: Obtener usuario actual

### Monitoreo

- `POST /api/monitor/event`: Registrar evento
- `GET /api/monitor/events`: Obtener eventos
- `POST /api/monitor/session/start`: Iniciar sesión de foco
- `PUT /api/monitor/session/end`: Finalizar sesión de foco
- `GET /api/monitor/session/{session_id}/stats`: Obtener estadísticas

### Utilidades

- `GET /api/health`: Health check

## Tecnologías

- **Backend**: FastAPI, Python 3.11+
- **Base de datos**: Supabase (PostgreSQL)
- **Autenticación**: Supabase Auth (JWT)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Gestión de paquetes**: uv
- **Servidor web**: Uvicorn

## Eventos Monitoreados

| Evento | Descripción |
|--------|-------------|
| `paste` | Usuario pega texto en el editor |
| `focus` | Ventana recibe el foco |
| `blur` | Ventana pierde el foco |
| `activity` | Actividad de mouse o teclado |
| `session_start` | Inicio de sesión de monitoreo |
| `session_end` | Fin de sesión de monitoreo |

## Seguridad

- ✅ Autenticación JWT con Supabase
- ✅ Row Level Security en base de datos
- ✅ CORS configurado
- ✅ Variables de entorno para secretos
- ✅ Validación de datos con Pydantic

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'feat: add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Convenciones de Commits

Este proyecto usa [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `style:` Cambios de formato (sin afectar código)
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Mantenimiento

## Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## Contacto

- Repositorio: [GitHub](https://github.com/martinvilu/ganimedes)
- Issues: [GitHub Issues](https://github.com/martinvilu/ganimedes/issues)

## Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/)
- [Supabase](https://supabase.com/)
- [uv](https://github.com/astral-sh/uv)
- [JupyterLite](https://jupyterlite.readthedocs.io/)
