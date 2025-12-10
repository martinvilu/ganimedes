#!/bin/bash
# Script para configurar Ganimedes en producción

set -e

echo "🔧 Configurador de Ganimedes"
echo ""

# Verificar si ya existe .env
if [ -f ".env" ]; then
    echo "⚠️  Ya existe un archivo .env"
    read -p "¿Deseas sobrescribirlo? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Configuración cancelada"
        exit 0
    fi
fi

echo "📝 Por favor ingresa los datos de configuración:"
echo ""

# Solicitar URL de Supabase
read -p "URL de Supabase (https://tu-proyecto.supabase.co): " SUPABASE_URL

# Solicitar clave de Supabase
read -p "Clave anon de Supabase: " SUPABASE_KEY

# Generar clave secreta aleatoria
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")

# Solicitar configuración del servidor
read -p "Host (default: 0.0.0.0): " HOST
HOST=${HOST:-0.0.0.0}

read -p "Puerto (default: 8000): " PORT
PORT=${PORT:-8000}

# Crear archivo .env
cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_KEY=$SUPABASE_KEY

# Application Configuration
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=production

# Server Configuration
HOST=$HOST
PORT=$PORT
EOF

echo ""
echo "✅ Archivo .env creado exitosamente"
echo ""
echo "📍 Ubicación: $(pwd)/.env"
echo ""
echo "🚀 Ahora puedes iniciar el servidor con:"
echo "   ganimedes"
echo ""
echo "🔒 Recuerda: NUNCA commits el archivo .env al repositorio"
