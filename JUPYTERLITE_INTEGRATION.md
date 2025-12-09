# Integración con JupyterLite

Esta guía explica cómo integrar el sistema de monitoreo Ganimedes con una instancia real de JupyterLite.

## Arquitectura

```
┌─────────────────────────────────────┐
│     JupyterLite (Frontend)          │
│  ┌──────────────────────────────┐   │
│  │   Jupyter Notebook Interface │   │
│  └────────────┬─────────────────┘   │
│               │                      │
│  ┌────────────▼─────────────────┐   │
│  │  Monitor Script (injected)   │   │
│  │  - Paste Detection           │   │
│  │  - Focus Tracking            │   │
│  │  - Activity Monitoring       │   │
│  └────────────┬─────────────────┘   │
└───────────────┼──────────────────────┘
                │ HTTP/WebSocket
┌───────────────▼──────────────────────┐
│    Ganimedes Backend (FastAPI)       │
│  ┌──────────────────────────────┐    │
│  │  Authentication (Supabase)   │    │
│  ├──────────────────────────────┤    │
│  │  Event Recording             │    │
│  ├──────────────────────────────┤    │
│  │  Session Management          │    │
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
```

## Paso 1: Instalar JupyterLite

### Opción A: Usar JupyterLite Precompilado

```bash
# Descargar JupyterLite
cd /home/mrtin/dev/jupyter/ganimedes
mkdir -p jupyterlite
cd jupyterlite

# Descargar desde GitHub releases
wget https://github.com/jupyterlite/jupyterlite/releases/latest/download/jupyterlite-demo.zip
unzip jupyterlite-demo.zip
```

### Opción B: Compilar JupyterLite

```bash
pip install jupyterlite-core
jupyter lite build --output-dir jupyterlite
```

## Paso 2: Integrar el Script de Monitoreo

Crea un archivo `jupyterlite/ganimedes-monitor.js`:

```javascript
/**
 * Script de integración de Ganimedes para JupyterLite
 * Inyecta el sistema de monitoreo en JupyterLite
 */

(function() {
    'use strict';
    
    const GANIMEDES_API = 'http://localhost:8000/api';
    let token = null;
    let sessionId = null;
    let focusStartTime = null;
    let pasteCount = 0;
    
    // Inicializar cuando JupyterLab esté listo
    if (typeof window.jupyterapp !== 'undefined') {
        window.jupyterapp.started.then(() => {
            initGanimedes();
        });
    } else {
        // Fallback si JupyterLab no está disponible inmediatamente
        window.addEventListener('load', () => {
            setTimeout(initGanimedes, 2000);
        });
    }
    
    function initGanimedes() {
        console.log('🔍 Ganimedes Monitor Iniciado');
        
        // Obtener token de autenticación
        token = localStorage.getItem('ganimedes_token');
        
        if (!token) {
            showAuthModal();
            return;
        }
        
        sessionId = generateSessionId();
        startMonitoring();
        monitorNotebookCells();
    }
    
    function generateSessionId() {
        return `jupyter_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    function startMonitoring() {
        // Registrar inicio de sesión
        sendEvent('session_start', {
            platform: 'jupyterlite',
            user_agent: navigator.userAgent
        });
        
        // Monitorear foco de ventana
        window.addEventListener('focus', () => {
            focusStartTime = Date.now();
            sendEvent('focus');
        });
        
        window.addEventListener('blur', () => {
            if (focusStartTime) {
                const focusTime = Date.now() - focusStartTime;
                sendEvent('blur', { focus_duration: focusTime });
                focusStartTime = null;
            }
        });
        
        // Monitorear actividad
        let lastActivity = Date.now();
        document.addEventListener('click', () => {
            if (Date.now() - lastActivity > 10000) {
                sendEvent('activity', { type: 'click' });
                lastActivity = Date.now();
            }
        });
        
        document.addEventListener('keydown', () => {
            if (Date.now() - lastActivity > 10000) {
                sendEvent('activity', { type: 'keyboard' });
                lastActivity = Date.now();
            }
        });
    }
    
    function monitorNotebookCells() {
        // Observar cambios en el DOM para detectar nuevas celdas
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList && node.classList.contains('jp-Cell')) {
                        attachCellMonitors(node);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Adjuntar monitores a celdas existentes
        document.querySelectorAll('.jp-Cell').forEach(attachCellMonitors);
    }
    
    function attachCellMonitors(cell) {
        // Buscar el área de código dentro de la celda
        const codeArea = cell.querySelector('.CodeMirror, textarea, [contenteditable="true"]');
        
        if (codeArea) {
            // Detectar pegado
            codeArea.addEventListener('paste', (e) => {
                pasteCount++;
                
                let pastedText = '';
                if (e.clipboardData) {
                    pastedText = e.clipboardData.getData('text');
                }
                
                sendEvent('paste', {
                    cell_id: cell.id || 'unknown',
                    text_length: pastedText.length,
                    text_preview: pastedText.substring(0, 100),
                    total_paste_count: pasteCount
                });
                
                console.warn('⚠️ Pegado detectado en celda:', cell.id);
            });
            
            // Detectar cambios de código (opcional, puede generar muchos eventos)
            let typingTimer;
            codeArea.addEventListener('input', () => {
                clearTimeout(typingTimer);
                typingTimer = setTimeout(() => {
                    sendEvent('code_change', {
                        cell_id: cell.id || 'unknown'
                    });
                }, 2000); // Esperar 2 segundos después de dejar de escribir
            });
        }
    }
    
    async function sendEvent(eventType, data = null) {
        if (!token || !sessionId) return;
        
        try {
            await fetch(`${GANIMEDES_API}/monitor/event`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    event_type: eventType,
                    data: data,
                    metadata: {
                        timestamp: new Date().toISOString(),
                        platform: 'jupyterlite'
                    }
                })
            });
        } catch (error) {
            console.error('Error enviando evento:', error);
        }
    }
    
    function showAuthModal() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;
        
        modal.innerHTML = `
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 400px;">
                <h2>Autenticación Requerida</h2>
                <p>Por favor inicia sesión en Ganimedes para continuar.</p>
                <input type="email" id="ganimedes-email" placeholder="Email" style="width: 100%; padding: 10px; margin: 10px 0;">
                <input type="password" id="ganimedes-password" placeholder="Contraseña" style="width: 100%; padding: 10px; margin: 10px 0;">
                <button id="ganimedes-login" style="width: 100%; padding: 10px; background: #2563eb; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Iniciar Sesión
                </button>
                <div id="ganimedes-error" style="color: red; margin-top: 10px;"></div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('ganimedes-login').addEventListener('click', async () => {
            const email = document.getElementById('ganimedes-email').value;
            const password = document.getElementById('ganimedes-password').value;
            
            try {
                const response = await fetch(`${GANIMEDES_API}/auth/signin`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    token = data.session.access_token;
                    localStorage.setItem('ganimedes_token', token);
                    modal.remove();
                    initGanimedes();
                } else {
                    document.getElementById('ganimedes-error').textContent = 'Error de autenticación';
                }
            } catch (error) {
                document.getElementById('ganimedes-error').textContent = 'Error de conexión';
            }
        });
    }
    
    // Guardar estado al salir
    window.addEventListener('beforeunload', () => {
        if (token && sessionId) {
            sendEvent('session_end', {
                total_paste_count: pasteCount
            });
        }
    });
})();
```

## Paso 3: Modificar index.html de JupyterLite

Edita `jupyterlite/index.html` y agrega antes del `</body>`:

```html
<!-- Ganimedes Monitoring -->
<script src="ganimedes-monitor.js"></script>
```

## Paso 4: Servir JupyterLite con Ganimedes

Actualiza `ganimedes/server.py` para servir JupyterLite:

```python
# Agregar después de montar /static
if os.path.exists("jupyterlite"):
    app.mount("/jupyter", StaticFiles(directory="jupyterlite", html=True), name="jupyter")
```

## Paso 5: Configurar CORS

En `server.py`, actualiza la configuración de CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Uso

1. **Iniciar el servidor:**
   ```bash
   ./scripts/dev.sh
   ```

2. **Acceder a JupyterLite:**
   - Dirígete a `http://localhost:8000/jupyter`
   - Se te pedirá autenticarte
   - Todos los eventos serán monitoreados automáticamente

3. **Ver eventos en tiempo real:**
   - API: `http://localhost:8000/api/monitor/events`
   - Dashboard: `http://localhost:8000/static/index.html`

## Eventos Monitoreados

- ✅ **paste**: Texto pegado en celdas
- ✅ **focus**: Ventana enfocada
- ✅ **blur**: Ventana desenfocada
- ✅ **activity**: Clicks y teclado
- ✅ **code_change**: Cambios en celdas
- ✅ **session_start**: Inicio de sesión
- ✅ **session_end**: Fin de sesión

## Consideraciones de Seguridad

1. **Privacidad**: El sistema NO captura el contenido completo del código, solo metadatos
2. **Consentimiento**: Informa a los usuarios que están siendo monitoreados
3. **HTTPS**: Usa HTTPS en producción
4. **Tokens**: Los tokens se almacenan localmente y deben ser manejados con cuidado

## Troubleshooting

### No se detectan eventos de pegado
- Verifica que el script se carga correctamente
- Revisa la consola del navegador para errores
- Asegúrate de que JupyterLite está completamente cargado

### Error de CORS
- Verifica la configuración de CORS en `server.py`
- Asegúrate de que las URLs coinciden exactamente

### Sesión no se guarda
- Verifica que el token sea válido
- Revisa los logs del servidor
- Comprueba la conexión con Supabase

## Personalización

Para personalizar qué eventos monitorear, edita la función `monitorNotebookCells()` en el script de integración.

## Próximos Pasos

- Implementar WebSocket para eventos en tiempo real
- Agregar análisis de patrones de código
- Crear dashboard de proctorización para profesores
- Implementar alertas automáticas por comportamiento sospechoso
