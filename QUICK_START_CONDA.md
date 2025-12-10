# Guía Rápida: Construcción de Paquete Conda

## TL;DR

```bash
# 1. Instalar herramientas
conda install conda-build anaconda-client

# 2. Construir paquete
./scripts/build-conda.sh

# 3. Probar
./scripts/test-conda-package.sh

# 4. Subir a Anaconda.org
anaconda login
./scripts/upload-conda.sh
```

## Construcción Paso a Paso

### 1. Instalar Requisitos

```bash
# Asegúrate de tener conda instalado
conda --version

# Instalar herramientas de construcción
conda install -n base conda-build anaconda-client -y
```

### 2. Construir el Paquete

```bash
# Opción A: Usar el script (recomendado)
cd /home/mrtin/dev/jupyter/ganimedes
./scripts/build-conda.sh

# Opción B: Manual (usando directorio local)
conda build conda-recipe \
    --output-folder ./dist/conda \
    --croot ./build/conda-bld \
    --no-anaconda-upload
```

El paquete se creará en: `./dist/conda/noarch/ganimedes-0.1.0-py_0.conda`

**Nota**: El script usa `--croot ./build/conda-bld` para construir en un directorio
local y evitar problemas de permisos en directorios del sistema como `/usr/pkgs`.

### 3. Probar el Paquete Localmente

```bash
# Opción A: Usar el script (recomendado)
./scripts/test-conda-package.sh

# Opción B: Manual
conda create -n test-ganimedes python=3.11 -y
conda activate test-ganimedes
conda install ./dist/conda/noarch/ganimedes-*.conda
python -c "import ganimedes; print('✅ OK')"
conda deactivate
conda env remove -n test-ganimedes -y
```

### 4. Subir a Anaconda.org

```bash
# Crear cuenta en https://anaconda.org (si no tienes)

# Autenticarse
anaconda login
# Ingresa tu usuario y contraseña

# Opción A: Usar el script (recomendado)
./scripts/upload-conda.sh

# Opción B: Manual
anaconda upload ./dist/conda/noarch/ganimedes-*.conda
```

### 5. Verificar la Publicación

Tu paquete estará disponible en:
```
https://anaconda.org/martinvilu/ganimedes
```

Los usuarios pueden instalarlo con:
```bash
conda install -c martinvilu ganimedes
```

## Estructura de Archivos Conda

```
ganimedes/
├── conda-recipe/           # Receta de construcción
│   ├── meta.yaml          # Metadatos y dependencias
│   ├── build.sh           # Script Linux/macOS
│   └── bld.bat            # Script Windows
├── environment.yml         # Ambiente conda base
├── environment-dev.yml     # Ambiente de desarrollo
├── scripts/
│   ├── build-conda.sh     # Construir paquete
│   ├── test-conda-package.sh  # Probar paquete
│   └── upload-conda.sh    # Subir a Anaconda.org
└── dist/conda/            # Paquetes construidos (git-ignored)
    └── noarch/
        └── ganimedes-*.conda
```

## Actualizar Versión

Para publicar una nueva versión:

1. **Actualizar versión en `pyproject.toml`:**
   ```toml
   version = "0.2.0"
   ```

2. **Actualizar versión en `conda-recipe/meta.yaml`:**
   ```yaml
   {% set version = "0.2.0" %}
   ```

3. **Actualizar `CHANGELOG.md`:**
   ```markdown
   ## [0.2.0] - 2024-12-XX
   ### Added
   - Nueva funcionalidad...
   ```

4. **Reconstruir y subir:**
   ```bash
   ./scripts/build-conda.sh
   ./scripts/test-conda-package.sh
   ./scripts/upload-conda.sh
   ```

5. **Crear tag en git:**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

## Troubleshooting Común

### Error: "Permission denied" en /usr/pkgs
Este es el error más común al construir.

**Solución**: El script `build-conda.sh` ya incluye la solución usando `--croot`
```bash
./scripts/build-conda.sh
```

Si construyes manualmente, usa:
```bash
conda build conda-recipe --croot ./build/conda-bld --output-folder ./dist/conda
```

### Error: "conda-build no encontrado"
```bash
conda install -n base conda-build -y
```

### Error: "anaconda command not found"
```bash
conda install -n base anaconda-client -y
```

### Error: "Authentication required"
```bash
anaconda login
# Ingresa credenciales de anaconda.org
```

### Error: "Package already exists"
```bash
# Forzar sobrescritura
anaconda upload --force ./dist/conda/noarch/ganimedes-*.conda
```

### Error al construir: "Dependency not found"
Verifica que la dependencia esté disponible:
```bash
conda search -c conda-forge nombre-paquete
```

Si solo está en PyPI, agrégala a la sección pip en `meta.yaml`.

## Instalación para Usuarios

Una vez publicado, los usuarios pueden instalar de varias formas:

### Instalación Simple
```bash
conda install -c martinvilu ganimedes
```

### Con Ambiente Nuevo
```bash
conda create -n mi-ganimedes python=3.11 -c martinvilu ganimedes
conda activate mi-ganimedes
```

### Desde environment.yml
```bash
# Los usuarios clonan el repo
git clone https://github.com/martinvilu/ganimedes.git
cd ganimedes

# Crean el ambiente
conda env create -f environment.yml
conda activate ganimedes
```

## Verificar Instalación

```bash
# Verificar que está instalado
conda list ganimedes

# Probar el comando CLI
ganimedes --help

# Probar imports
python -c "import ganimedes; print(ganimedes.__version__)"
```

## Recursos

- **Documentación completa:** [CONDA_BUILD.md](CONDA_BUILD.md)
- **Conda Build Docs:** https://docs.conda.io/projects/conda-build/
- **Anaconda.org:** https://anaconda.org/
- **Conda-forge:** https://conda-forge.org/

## Soporte

- **Issues:** https://github.com/martinvilu/ganimedes/issues
- **Discusiones:** https://github.com/martinvilu/ganimedes/discussions
