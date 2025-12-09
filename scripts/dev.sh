#!/bin/bash
# Script para iniciar el servidor de desarrollo

set -e

echo "🚀 Iniciando Ganimedes en modo desarrollo..."

# Verificar que existe .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Copiando .env.example..."
    cp .env.example .env
    echo "⚠️  Por favor configura tus credenciales en .env antes de continuar"
    exit 1
fi

# Activar entorno virtual con uv y ejecutar servidor
echo "📦 Sincronizando dependencias..."
uv sync

echo "🌐 Servidor disponible en http://localhost:8000/static/index.html"
echo "📚 API docs en http://localhost:8000/docs"
echo ""

uv run python -m ganimedes.server
