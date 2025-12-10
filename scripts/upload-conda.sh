#!/bin/bash
# Script para subir el paquete conda a Anaconda.org

set -e

echo "📤 Subiendo paquete Conda a Anaconda.org..."

# Verificar que anaconda-client está instalado
if ! command -v anaconda &> /dev/null; then
    echo "❌ anaconda-client no está instalado"
    echo "Instálalo con: conda install anaconda-client"
    exit 1
fi

# Buscar el paquete
PACKAGE=$(find ./dist/conda -name "ganimedes-*.conda" -type f | head -n 1)

if [ -z "$PACKAGE" ]; then
    echo "❌ No se encontró el paquete .conda"
    echo "Ejecuta primero: ./scripts/build-conda.sh"
    exit 1
fi

echo "📦 Paquete encontrado: $PACKAGE"
echo ""

# Verificar si está autenticado
if ! anaconda whoami &> /dev/null; then
    echo "🔑 No estás autenticado en Anaconda.org"
    echo "Ejecuta: anaconda login"
    exit 1
fi

echo "👤 Usuario: $(anaconda whoami)"
echo ""

# Preguntar antes de subir
read -p "¿Deseas subir el paquete? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelado"
    exit 1
fi

# Subir el paquete
echo "📤 Subiendo..."
anaconda upload "$PACKAGE"

echo ""
echo "✅ ¡Paquete subido exitosamente!"
echo ""
echo "🌐 Disponible en:"
echo "   https://anaconda.org/$(anaconda whoami)/ganimedes"
echo ""
echo "📥 Para instalar:"
echo "   conda install -c $(anaconda whoami) ganimedes"
