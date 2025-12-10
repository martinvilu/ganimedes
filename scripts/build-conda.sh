#!/bin/bash
# Script para construir el paquete conda

set -e

echo "🔨 Construyendo paquete Conda para Ganimedes..."

# Verificar que conda-build está instalado
if ! command -v conda-build &> /dev/null; then
    echo "❌ conda-build no está instalado"
    echo "Instálalo con: conda install conda-build"
    exit 1
fi

# Crear directorios de trabajo
mkdir -p dist/conda
mkdir -p build/conda-bld

# Construir el paquete usando directorio local para build
echo "📦 Construyendo paquete..."
echo "   (usando directorio local de build para evitar permisos)"
conda build conda-recipe \
    --output-folder ./dist/conda \
    --croot ./build/conda-bld \
    --no-anaconda-upload

echo ""
echo "✅ Paquete construido exitosamente!"
echo ""
echo "📍 Ubicación del paquete:"
find ./dist/conda -name "ganimedes-*.conda" -type f

echo ""
echo "🚀 Para instalar localmente:"
echo "   conda install ./dist/conda/noarch/ganimedes-*.conda"
echo ""
echo "📤 Para subir a Anaconda.org:"
echo "   anaconda upload ./dist/conda/noarch/ganimedes-*.conda"
