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

# Crear directorio de salida
mkdir -p dist/conda

# Construir el paquete
echo "📦 Construyendo paquete..."
conda build conda-recipe --output-folder ./dist/conda

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
