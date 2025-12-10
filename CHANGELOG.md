# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planeado
- WebSocket para eventos en tiempo real
- Dashboard para profesores/administradores
- Análisis de patrones de código
- Alertas automáticas por comportamiento sospechoso
- Integración con LMS (Moodle, Canvas)

## [0.1.0] - 2024-12-10

### Añadido
- Sistema completo de monitoreo de eventos (paste, focus, blur, activity)
- Autenticación con Supabase y JWT
- API REST con FastAPI
- Frontend interactivo con dashboard en tiempo real
- Base de datos con Row Level Security en PostgreSQL/Supabase
- Sistema de gestión de sesiones de foco
- Documentación completa (README, SETUP, JUPYTERLITE_INTEGRATION)
- Scripts de desarrollo automatizados
- Tests básicos con pytest
- Soporte para empaquetado con Conda
- Receta conda para distribución en Anaconda.org
- Archivos environment.yml para instalación con conda
- Scripts automatizados para construcción y upload de paquetes conda
- GitHub Actions para CI/CD
- Gestión de dependencias con uv

### Características Iniciales

#### Backend
- FastAPI server con endpoints REST completos
- Autenticación JWT con Supabase
- Sistema de monitoreo de eventos
- Modelos de datos con Pydantic
- Gestión de sesiones de proctorización

#### Frontend
- Interfaz de login/registro
- Dashboard de monitoreo en tiempo real
- Visualización de estadísticas de sesión
- Editor de código simulado para testing
- Log de eventos en tiempo real
- Diseño responsivo y moderno

#### Base de Datos
- Esquema completo con tablas `monitor_events` y `focus_sessions`
- Row Level Security policies
- Índices optimizados
- Funciones SQL para estadísticas
- Triggers automáticos

#### Documentación
- README con guía de inicio rápido
- SETUP.md con configuración detallada
- JUPYTERLITE_INTEGRATION.md para integración real
- CONDA_BUILD.md para empaquetado
- GITHUB_SETUP.md para configuración de repositorio

#### Desarrollo
- Gestión de paquetes con uv
- Scripts bash para desarrollo y testing
- Configuración de linters (black, ruff)
- Tests automatizados con pytest
- GitHub Actions workflows

### Tecnologías
- Python 3.11+
- FastAPI 0.104+
- Supabase 2.0+
- PostgreSQL (vía Supabase)
- Vanilla JavaScript
- HTML5/CSS3
- uv (package manager)
- Conda (packaging)

[Unreleased]: https://github.com/martinvilu/ganimedes/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/martinvilu/ganimedes/releases/tag/v0.1.0
