#!/bin/bash
# Script para construir el paquete wheel de Python

set -e

echo "🔨 Construyendo paquete wheel para Ganimedes..."

# Activar conda desde miniconda3
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    conda activate base
else
    echo "⚠️  No se encontró conda en ~/miniconda3, usando Python del sistema"
fi

# Verificar que estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ No se encontró pyproject.toml"
    echo "Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Crear directorio de salida
mkdir -p dist

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build/ dist/*.whl dist/*.tar.gz *.egg-info/

# Construir el paquete
echo "📦 Construyendo paquete con setuptools..."
python setup.py bdist_wheel sdist

echo ""
echo "✅ Paquete construido exitosamente!"
echo ""
echo "📍 Paquetes generados:"
ls -lh dist/

echo ""
echo "🚀 Para instalar localmente con pip:"
echo "   pip install dist/ganimedes-*.whl"
echo ""
echo "🚀 Para instalar localmente con conda:"
echo "   pip install dist/ganimedes-*.whl"
echo ""
echo "📤 Para subir a PyPI:"
echo "   twine upload dist/*"
