/**
 * Sistema de monitoreo para Ganimedes
 * Registra eventos de pegado y tiempo de foco
 */

const API_BASE = window.location.origin + '/api';

class GanimedesMonitor {
    constructor() {
        this.token = null;
        this.user = null;
        this.sessionId = this.generateSessionId();
        this.focusStartTime = null;
        this.totalFocusTime = 0;
        this.pasteCount = 0;
        this.focusInterval = null;
        this.isActive = false;
        
        this.init();
    }
    
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    init() {
        // Verificar si hay sesión guardada
        this.token = localStorage.getItem('ganimedes_token');
        
        if (this.token) {
            this.verifyToken();
        } else {
            this.showAuthContainer();
        }
        
        this.setupEventListeners();
    }
    
    async verifyToken() {
        try {
            const response = await fetch(`${API_BASE}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.user = data.user;
                this.showMainContainer();
                this.startMonitoring();
            } else {
                this.logout();
            }
        } catch (error) {
            console.error('Error verificando token:', error);
            this.logout();
        }
    }
    
    setupEventListeners() {
        // Auth forms
        document.getElementById('signin-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.signin();
        });
        
        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.signup();
        });
        
        document.getElementById('show-signup').addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('signup-form').style.display = 'block';
        });
        
        document.getElementById('show-signin').addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('signup-form').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
        });
        
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });
        
        // Monitoring events
        document.getElementById('code-area').addEventListener('paste', (e) => {
            this.handlePaste(e);
        });
        
        window.addEventListener('focus', () => {
            this.handleFocus();
        });
        
        window.addEventListener('blur', () => {
            this.handleBlur();
        });
        
        // Detectar actividad
        document.addEventListener('mousemove', () => {
            this.recordActivity();
        });
        
        document.addEventListener('keydown', () => {
            this.recordActivity();
        });
    }
    
    async signin() {
        const email = document.getElementById('signin-email').value;
        const password = document.getElementById('signin-password').value;
        
        try {
            const response = await fetch(`${API_BASE}/auth/signin`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.token = data.session.access_token;
                this.user = data.user;
                localStorage.setItem('ganimedes_token', this.token);
                this.showMainContainer();
                this.startMonitoring();
            } else {
                this.showError(data.detail || 'Error al iniciar sesión');
            }
        } catch (error) {
            this.showError('Error de conexión');
            console.error(error);
        }
    }
    
    async signup() {
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const fullName = document.getElementById('signup-name').value;
        
        try {
            const response = await fetch(`${API_BASE}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    email, 
                    password,
                    full_name: fullName || null
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.token = data.session.access_token;
                this.user = data.user;
                localStorage.setItem('ganimedes_token', this.token);
                this.showMainContainer();
                this.startMonitoring();
            } else {
                this.showError(data.detail || 'Error al registrar');
            }
        } catch (error) {
            this.showError('Error de conexión');
            console.error(error);
        }
    }
    
    logout() {
        this.stopMonitoring();
        this.token = null;
        this.user = null;
        localStorage.removeItem('ganimedes_token');
        this.showAuthContainer();
    }
    
    showAuthContainer() {
        document.getElementById('auth-container').style.display = 'flex';
        document.getElementById('main-container').style.display = 'none';
    }
    
    showMainContainer() {
        document.getElementById('auth-container').style.display = 'none';
        document.getElementById('main-container').style.display = 'block';
        document.getElementById('user-email').textContent = this.user.email;
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
        setTimeout(() => {
            errorDiv.classList.remove('show');
        }, 5000);
    }
    
    async startMonitoring() {
        this.isActive = true;
        
        // Iniciar sesión de foco
        await this.sendRequest('/monitor/session/start', {
            session_id: this.sessionId
        });
        
        // Iniciar tracking de foco
        this.focusStartTime = Date.now();
        this.focusInterval = setInterval(() => {
            this.updateFocusTime();
        }, 1000);
        
        this.logEvent('Monitoreo iniciado', 'info');
    }
    
    async stopMonitoring() {
        if (!this.isActive) return;
        
        this.isActive = false;
        clearInterval(this.focusInterval);
        
        // Finalizar sesión
        await this.sendRequest('/monitor/session/end', {
            session_id: this.sessionId,
            total_focus_time: Math.floor(this.totalFocusTime / 1000),
            paste_count: this.pasteCount
        }, 'PUT');
    }
    
    async handlePaste(event) {
        this.pasteCount++;
        document.getElementById('paste-count').textContent = this.pasteCount;
        
        const pastedText = event.clipboardData.getData('text');
        
        await this.sendEvent('paste', {
            text_length: pastedText.length,
            text_preview: pastedText.substring(0, 100)
        });
        
        this.logEvent('Texto pegado detectado', 'paste');
    }
    
    async handleFocus() {
        if (!this.isActive) return;
        
        this.focusStartTime = Date.now();
        document.getElementById('session-status').textContent = 'Activo';
        document.getElementById('session-status').className = 'stat-value status-active';
        
        await this.sendEvent('focus');
        this.logEvent('Ventana enfocada', 'focus');
    }
    
    async handleBlur() {
        if (!this.isActive) return;
        
        if (this.focusStartTime) {
            this.totalFocusTime += Date.now() - this.focusStartTime;
            this.focusStartTime = null;
        }
        
        document.getElementById('session-status').textContent = 'Inactivo';
        document.getElementById('session-status').className = 'stat-value status-inactive';
        
        await this.sendEvent('blur');
        this.logEvent('Ventana desenfocada', 'blur');
    }
    
    async recordActivity() {
        if (!this.isActive) return;
        
        // Throttle: solo registrar cada 10 segundos
        if (!this.lastActivityTime || Date.now() - this.lastActivityTime > 10000) {
            this.lastActivityTime = Date.now();
            await this.sendEvent('activity');
        }
    }
    
    updateFocusTime() {
        let totalTime = this.totalFocusTime;
        
        if (this.focusStartTime) {
            totalTime += Date.now() - this.focusStartTime;
        }
        
        const hours = Math.floor(totalTime / 3600000);
        const minutes = Math.floor((totalTime % 3600000) / 60000);
        const seconds = Math.floor((totalTime % 60000) / 1000);
        
        const timeStr = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        document.getElementById('focus-time').textContent = timeStr;
    }
    
    async sendEvent(eventType, data = null) {
        return this.sendRequest('/monitor/event', {
            session_id: this.sessionId,
            event_type: eventType,
            data,
            metadata: {
                user_agent: navigator.userAgent,
                screen_resolution: `${window.screen.width}x${window.screen.height}`
            }
        });
    }
    
    async sendRequest(endpoint, body, method = 'POST') {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(body)
            });
            
            if (!response.ok) {
                console.error('Error en request:', await response.text());
            }
            
            return response.ok;
        } catch (error) {
            console.error('Error de conexión:', error);
            return false;
        }
    }
    
    logEvent(message, type = 'info') {
        const eventsList = document.getElementById('events-list');
        const eventItem = document.createElement('div');
        eventItem.className = `event-item ${type}`;
        
        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        
        eventItem.innerHTML = `
            <strong>${message}</strong>
            <span class="event-timestamp">${timestamp}</span>
        `;
        
        eventsList.insertBefore(eventItem, eventsList.firstChild);
        
        // Limitar a 50 eventos en el log
        while (eventsList.children.length > 50) {
            eventsList.removeChild(eventsList.lastChild);
        }
    }
}

// Inicializar el monitor cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.ganimedesMonitor = new GanimedesMonitor();
});

// Guardar estado antes de cerrar
window.addEventListener('beforeunload', () => {
    if (window.ganimedesMonitor && window.ganimedesMonitor.isActive) {
        window.ganimedesMonitor.stopMonitoring();
    }
});
