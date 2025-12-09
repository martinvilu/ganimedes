#!/bin/bash
# Script para ejecutar tests

set -e

echo "🧪 Ejecutando tests de Ganimedes..."

# Sincronizar dependencias de desarrollo
uv sync --extra dev

# Ejecutar tests
uv run pytest -v --color=yes

echo "✅ Tests completados"
