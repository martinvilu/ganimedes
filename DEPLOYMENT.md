# Guía de Despliegue de Ganimedes

Esta guía explica cómo desplegar Ganimedes en producción para monitorear una instancia de JupyterLite.

## 📋 Arquitectura

```
┌─────────────────────────────────────┐
│  Usuarios (Navegador)               │
│  ├─ JupyterLite                     │
│  │  └─ ganimedes-monitor.js         │
│  └─ Dashboard de monitoreo          │
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│  Servidor Ganimedes                 │
│  ├─ FastAPI Backend                 │
│  ├─ Variables de entorno (.env)     │
│  └─ Archivos estáticos              │
└──────────────┬──────────────────────┘
               │ API
               ▼
┌─────────────────────────────────────┐
│  Supabase                           │
│  ├─ Autenticación                   │
│  └─ Base de datos                   │
└─────────────────────────────────────┘
```

## 🚀 Instalación en Servidor

### Paso 1: Instalar el paquete

```bash
# Opción A: Desde wheel local
pip install ganimedes-0.1.0-py3-none-any.whl

# Opción B: Desde PyPI (cuando esté publicado)
pip install ganimedes

# Opción C: Desde el repositorio
pip install git+https://github.com/martinvilu/ganimedes.git
```

### Paso 2: Configurar credenciales de Supabase

```bash
# Usar el script de configuración interactivo
./scripts/configure.sh

# O crear manualmente el archivo .env
cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-supabase-anon-key

# Application Configuration
SECRET_KEY=una-clave-secreta-muy-larga-y-aleatoria
ENVIRONMENT=production

# Server Configuration
HOST=0.0.0.0
PORT=8000
EOF
```

### Paso 3: Crear la base de datos en Supabase

1. Ve a https://supabase.com y crea un proyecto
2. En el SQL Editor, ejecuta el contenido de `supabase-schema.sql`
3. Copia la URL y API Key (anon, public) a tu archivo `.env`

### Paso 4: Iniciar el servidor

```bash
# Desarrollo (con auto-reload)
ganimedes

# Producción (con Gunicorn)
gunicorn ganimedes.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 🌐 Despliegue en JupyterLite

### Opción 1: JupyterLite Standalone

Si tienes JupyterLite en un servidor separado:

1. **Descarga el script de monitoreo:**
   ```bash
   wget https://tu-servidor-ganimedes.com/static/monitor.js -O ganimedes-monitor.js
   ```

2. **Edita el script y configura la URL del backend:**
   ```javascript
   // Al inicio del archivo ganimedes-monitor.js
   const API_BASE = 'https://tu-servidor-ganimedes.com/api';
   ```

3. **Inyecta el script en JupyterLite:**
   
   Edita `index.html` de JupyterLite y agrega antes de `</body>`:
   ```html
   <!-- Ganimedes Monitoring -->
   <script src="ganimedes-monitor.js"></script>
   ```

### Opción 2: JupyterLite integrado con Ganimedes

Si quieres servir JupyterLite desde el mismo servidor Ganimedes:

1. **Instala JupyterLite:**
   ```bash
   pip install jupyterlite-core
   jupyter lite build --output-dir jupyterlite
   ```

2. **Copia el script de monitoreo:**
   ```bash
   cp frontend/monitor.js jupyterlite/ganimedes-monitor.js
   ```

3. **Edita jupyterlite/index.html:**
   ```html
   <script src="ganimedes-monitor.js"></script>
   ```

4. **Modifica server.py para servir JupyterLite:**
   ```python
   # Agregar en server.py después de montar /static
   import os
   if os.path.exists("jupyterlite"):
       app.mount("/jupyter", StaticFiles(directory="jupyterlite", html=True), name="jupyter")
   ```

5. **Reinicia el servidor y accede a:**
   - JupyterLite: `http://tu-servidor:8000/jupyter`
   - Dashboard: `http://tu-servidor:8000/static/index.html`

## 🔐 Configuración de Seguridad

### Tokens y Credenciales

**⚠️ IMPORTANTE**: Los tokens de Supabase **NUNCA** van en el código JavaScript:

- ✅ Backend (Python) lee tokens de `.env`
- ✅ Frontend (JavaScript) solo necesita la URL del backend
- ✅ Usuarios se autentican vía login y obtienen token de sesión
- ❌ NUNCA expongas `SUPABASE_KEY` en archivos JS

### Flujo de Autenticación

1. Usuario abre JupyterLite
2. Script `ganimedes-monitor.js` verifica si hay token de sesión en `localStorage`
3. Si no hay token, muestra modal de login
4. Al hacer login:
   - JS envía credenciales a `POST /api/auth/signin`
   - Backend valida con Supabase usando el `SUPABASE_KEY` del .env
   - Backend retorna token de sesión al usuario
   - JS guarda token en `localStorage`
5. Todas las peticiones futuras usan el token de sesión

### HTTPS en Producción

```bash
# Usar reverse proxy con Nginx
# /etc/nginx/sites-available/ganimedes
server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 Monitoreo y Mantenimiento

### Ver logs

```bash
# Si usas systemd
journalctl -u ganimedes -f

# Si usas Docker
docker logs -f ganimedes
```

### Health check

```bash
curl http://localhost:8000/api/health
```

### Backups de Supabase

Supabase hace backups automáticos, pero puedes exportar manualmente:

```bash
# Desde Supabase Dashboard > Database > Backups
```

## 🐳 Despliegue con Docker (Opcional)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY ganimedes-0.1.0-py3-none-any.whl .
RUN pip install ganimedes-0.1.0-py3-none-any.whl gunicorn

# No copiar .env - usar variables de entorno de Docker
EXPOSE 8000

CMD ["gunicorn", "ganimedes.server:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

```bash
# Build
docker build -t ganimedes:latest .

# Run con variables de entorno
docker run -d \
  -p 8000:8000 \
  -e SUPABASE_URL="https://..." \
  -e SUPABASE_KEY="..." \
  -e SECRET_KEY="..." \
  --name ganimedes \
  ganimedes:latest
```

## ✅ Checklist de Despliegue

- [ ] Paquete wheel instalado
- [ ] Archivo `.env` creado con credenciales
- [ ] Schema de Supabase ejecutado
- [ ] Servidor iniciado correctamente
- [ ] Health check responde OK
- [ ] HTTPS configurado (producción)
- [ ] Script de monitoreo inyectado en JupyterLite
- [ ] Usuario de prueba puede hacer login
- [ ] Eventos se registran correctamente
- [ ] Backups configurados

## 🆘 Troubleshooting

### El servidor no inicia

```bash
# Verificar instalación
pip show ganimedes

# Verificar .env
cat .env

# Probar en modo desarrollo
python -m ganimedes.server
```

### Error de autenticación

```bash
# Verificar credenciales de Supabase
curl -X POST https://SUPABASE_URL/auth/v1/signup \
  -H "apikey: SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Eventos no se registran

1. Verificar que el script JS se carga correctamente
2. Ver la consola del navegador para errores
3. Verificar que el token de sesión es válido
4. Revisar logs del servidor

## 📚 Referencias

- [Documentación de Supabase](https://supabase.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [JupyterLite Documentation](https://jupyterlite.readthedocs.io/)
