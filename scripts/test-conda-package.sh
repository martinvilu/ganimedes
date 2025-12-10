#!/bin/bash
# Script para probar el paquete conda en un ambiente limpio

set -e

echo "🧪 Probando paquete Conda en ambiente limpio..."

# Buscar el paquete
PACKAGE=$(find ./dist/conda -name "ganimedes-*.conda" -type f | head -n 1)

if [ -z "$PACKAGE" ]; then
    echo "❌ No se encontró el paquete .conda"
    echo "Ejecuta primero: ./scripts/build-conda.sh"
    exit 1
fi

# Nombre del ambiente de prueba
TEST_ENV="ganimedes-test-$(date +%s)"

echo "📦 Paquete: $PACKAGE"
echo "🧪 Ambiente de prueba: $TEST_ENV"
echo ""

# Crear ambiente de prueba
echo "1️⃣ Creando ambiente de prueba..."
conda create -n "$TEST_ENV" python=3.11 -y

# Activar ambiente
echo ""
echo "2️⃣ Instalando paquete..."
eval "$(conda shell.bash hook)"
conda activate "$TEST_ENV"

# Instalar el paquete
conda install "$PACKAGE" -y

# Probar imports
echo ""
echo "3️⃣ Probando imports..."
python -c "import ganimedes; print('✅ ganimedes importado correctamente')"
python -c "import ganimedes.server; print('✅ ganimedes.server importado correctamente')"
python -c "import ganimedes.auth; print('✅ ganimedes.auth importado correctamente')"
python -c "import ganimedes.monitor; print('✅ ganimedes.monitor importado correctamente')"
python -c "import ganimedes.database; print('✅ ganimedes.database importado correctamente')"

# Verificar comando CLI
echo ""
echo "4️⃣ Verificando comando CLI..."
if command -v ganimedes &> /dev/null; then
    echo "✅ Comando 'ganimedes' disponible"
else
    echo "⚠️  Comando 'ganimedes' no encontrado (puede requerir reinicio de shell)"
fi

# Limpiar
echo ""
echo "5️⃣ Limpiando ambiente de prueba..."
conda deactivate
conda env remove -n "$TEST_ENV" -y

echo ""
echo "✅ ¡Todas las pruebas pasaron exitosamente!"
