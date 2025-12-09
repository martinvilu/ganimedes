# Configuración del Repositorio en GitHub

## Opción 1: Usar GitHub CLI (gh)

```bash
# Autenticarse en GitHub (si no lo has hecho)
gh auth login

# Crear el repositorio en GitHub
gh repo create ganimedes --public --source=. --description="Sistema de monitoreo y proctorización para JupyterLite"

# Push del código
git push -u origin main
```

## Opción 2: Manualmente desde la web

### Paso 1: Crear el Repositorio

1. Ve a [GitHub](https://github.com/new)
2. Nombre: `ganimedes`
3. Descripción: "Sistema de monitoreo y proctorización para JupyterLite"
4. Visibilidad: Public o Private
5. **NO** inicialices con README, .gitignore o LICENSE (ya los tenemos)
6. Click en "Create repository"

### Paso 2: Conectar el Repositorio Local

```bash
cd /home/mrtin/dev/jupyter/ganimedes

# Agregar el remote
git remote add origin https://github.com/TU-USUARIO/ganimedes.git

# O si usas SSH
git remote add origin git@github.com:TU-USUARIO/ganimedes.git

# Push del código
git push -u origin main
```

## Configurar el Repositorio

### 1. Agregar Topics

En GitHub, ve a tu repositorio y agrega estos topics:
- `jupyterlite`
- `proctoring`
- `monitoring`
- `supabase`
- `fastapi`
- `python`
- `education`
- `exam-proctoring`

### 2. Configurar About

En la sección "About" del repositorio:
- Website: URL de tu instancia desplegada (si tienes una)
- Description: "🛰️ Sistema de monitoreo y proctorización para JupyterLite con autenticación Supabase"

### 3. Crear Issues/Milestones (Opcional)

Puedes crear issues para futuras mejoras:

#### Issues Sugeridos

1. **WebSocket Support**
   - Título: "feat: implement WebSocket for real-time monitoring"
   - Label: enhancement

2. **Admin Dashboard**
   - Título: "feat: create admin dashboard for teachers"
   - Label: enhancement

3. **Analytics**
   - Título: "feat: add analytics and reporting"
   - Label: enhancement

4. **Docker Support**
   - Título: "chore: add Dockerfile and docker-compose"
   - Label: enhancement

### 4. Configurar Branch Protection

Settings → Branches → Add rule:
- Branch name pattern: `main`
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging

### 5. Agregar Badges al README (Opcional)

Agrega estos badges al inicio del README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![uv](https://img.shields.io/badge/uv-latest-blue.svg)
```

## Verificar la Configuración

```bash
# Ver los remotes configurados
git remote -v

# Ver el estado
git status

# Ver el log
git log --oneline
```

## Próximos Pasos

1. **Configurar GitHub Actions** (CI/CD)
2. **Agregar tests automáticos**
3. **Configurar deploy automático** (Railway, Fly.io, etc.)
4. **Crear releases** cuando hagas versiones estables

## Comandos Útiles para Colaboración

```bash
# Crear una nueva rama para un feature
git checkout -b feature/nueva-funcionalidad

# Hacer commits semánticos
git commit -m "feat: descripción del cambio"

# Push de la rama
git push origin feature/nueva-funcionalidad

# Crear PR desde GitHub CLI
gh pr create --title "feat: Nueva funcionalidad" --body "Descripción detallada"
```

## Mantener el Repositorio

```bash
# Actualizar desde el remote
git pull origin main

# Ver ramas
git branch -a

# Eliminar ramas merged
git branch --merged | grep -v "main" | xargs git branch -d
```

## Tags y Releases

```bash
# Crear un tag para una release
git tag -a v0.1.0 -m "Release v0.1.0: Initial release"

# Push del tag
git push origin v0.1.0

# O push de todos los tags
git push --tags

# Crear release desde CLI
gh release create v0.1.0 --title "v0.1.0" --notes "Primera versión de Ganimedes"
```

## Ejemplo de Flujo de Trabajo

```bash
# 1. Crear feature branch
git checkout -b feature/websocket-support

# 2. Hacer cambios y commits
git add .
git commit -m "feat(websocket): add real-time event streaming"

# 3. Push del branch
git push origin feature/websocket-support

# 4. Crear Pull Request
gh pr create --base main --head feature/websocket-support

# 5. Después del merge, actualizar local
git checkout main
git pull origin main

# 6. Eliminar branch local
git branch -d feature/websocket-support
```
