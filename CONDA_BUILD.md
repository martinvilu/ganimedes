# Construcción y Distribución de Paquetes Conda

Esta guía explica cómo construir y distribuir Ganimedes como un paquete Conda.

## Requisitos Previos

```bash
# Instalar conda-build y anaconda-client
conda install conda-build anaconda-client
```

## Opción 1: Construcción Local del Paquete .conda

### Paso 1: Construir el paquete

```bash
cd /home/mrtin/dev/jupyter/ganimedes

# Usar el script (recomendado - evita problemas de permisos)
./scripts/build-conda.sh

# O manual con directorio local de build
conda build conda-recipe \
    --output-folder ./dist/conda \
    --croot ./build/conda-bld \
    --no-anaconda-upload
```

El paquete `.conda` se generará en:
- `./dist/conda/noarch/ganimedes-0.1.0-py_0.conda`

**Importante**: Usamos `--croot ./build/conda-bld` para construir en un directorio
local y evitar problemas de permisos en directorios del sistema.

### Paso 2: Instalar localmente (para probar)

```bash
# Instalar desde el archivo local
conda install -c local ganimedes

# O desde el archivo específico
conda install ./dist/conda/noarch/ganimedes-0.1.0-py_0.conda
```

### Paso 3: Verificar la instalación

```bash
# Verificar que está instalado
conda list ganimedes

# Probar el comando
ganimedes --help
```

## Opción 2: Subir a Anaconda.org

### Paso 1: Crear una cuenta en Anaconda.org

1. Ve a https://anaconda.org/
2. Crea una cuenta gratuita
3. Obtén tu token de acceso

### Paso 2: Autenticarse

```bash
# Método 1: Login interactivo
anaconda login

# Método 2: Con token
anaconda login --username tu-usuario --password tu-token
```

### Paso 3: Subir el paquete

```bash
# Subir el paquete construido
anaconda upload ~/anaconda3/conda-bld/noarch/ganimedes-0.1.0-py_0.conda

# O con ruta específica
anaconda upload ./dist/conda/noarch/ganimedes-0.1.0-py_0.conda

# Con opciones adicionales
anaconda upload \
  --user tu-usuario \
  --label main \
  ~/anaconda3/conda-bld/noarch/ganimedes-0.1.0-py_0.conda
```

### Paso 4: Verificar en Anaconda.org

Tu paquete estará disponible en:
```
https://anaconda.org/tu-usuario/ganimedes
```

## Instalación desde Anaconda.org

Una vez subido, otros usuarios pueden instalar con:

```bash
# Instalar desde tu canal
conda install -c tu-usuario ganimedes

# O crear un ambiente específico
conda create -n ganimedes-env python=3.11 -c tu-usuario ganimedes
conda activate ganimedes-env
```

## Construcción Multiplataforma

Para construir para múltiples plataformas:

```bash
# Linux
conda build conda-recipe

# Si tienes acceso a otras plataformas
conda build conda-recipe --platform linux-64
conda build conda-recipe --platform osx-64
conda build conda-recipe --platform osx-arm64
conda build conda-recipe --platform win-64
```

**Nota:** Este paquete es `noarch: python`, por lo que funciona en todas las plataformas.

## Actualizar el Paquete

### 1. Actualizar la versión

Edita `pyproject.toml`:
```toml
version = "0.2.0"
```

Edita `conda-recipe/meta.yaml`:
```yaml
{% set version = "0.2.0" %}
```

### 2. Reconstruir y subir

```bash
# Construir nueva versión
conda build conda-recipe

# Subir a Anaconda.org
anaconda upload ~/anaconda3/conda-bld/noarch/ganimedes-0.2.0-py_0.conda
```

## Construcción Automatizada con GitHub Actions

Crea `.github/workflows/conda-build.yml`:

```yaml
name: Build Conda Package

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Miniconda
        uses: conda-incubator/setup-miniconda@v2
        with:
          auto-update-conda: true
          python-version: 3.11
          
      - name: Install conda-build
        run: conda install conda-build anaconda-client
        
      - name: Build package
        run: conda build conda-recipe
        
      - name: Upload to Anaconda
        env:
          ANACONDA_TOKEN: ${{ secrets.ANACONDA_TOKEN }}
        run: |
          anaconda -t $ANACONDA_TOKEN upload \
            ~/anaconda3/conda-bld/noarch/ganimedes-*.conda
```

## Mantenimiento del Canal

### Ver tus paquetes

```bash
anaconda show tu-usuario
```

### Eliminar una versión

```bash
anaconda remove tu-usuario/ganimedes/0.1.0
```

### Hacer el paquete privado

```bash
anaconda package --private tu-usuario/ganimedes
```

### Hacer el paquete público

```bash
anaconda package --public tu-usuario/ganimedes
```

## Crear un Ambiente desde environment.yml

Crea `environment.yml` para usuarios:

```yaml
name: ganimedes-env
channels:
  - tu-usuario
  - conda-forge
  - defaults
dependencies:
  - python>=3.11
  - ganimedes
```

Los usuarios pueden crear el ambiente con:
```bash
conda env create -f environment.yml
```

## Troubleshooting

### Error: "Permission denied" en /usr/pkgs

Este es el error más común. Ocurre cuando conda-build intenta escribir en directorios del sistema.

**Solución**: Usar directorio local de build
```bash
# Con el script (ya incluye la solución)
./scripts/build-conda.sh

# O manualmente
conda build conda-recipe \
    --output-folder ./dist/conda \
    --croot ./build/conda-bld \
    --no-anaconda-upload
```

### Error: "Package already exists"

```bash
# Forzar sobrescritura
anaconda upload --force paquete.conda
```

### Error: "Invalid token"

```bash
# Re-autenticarse
anaconda logout
anaconda login
```

### Error al construir: "Dependencies not found"

Verifica que todas las dependencias estén disponibles en conda-forge:
```bash
conda search -c conda-forge nombre-paquete
```

Si un paquete solo está en PyPI, puedes:
1. Usar `pip` en el script de instalación
2. O especificar `- pip` y luego `- pip: nombre-paquete` en requirements

### Verificar el contenido del paquete

```bash
# Listar contenido del paquete
conda inspect contents ./dist/conda/noarch/ganimedes-0.1.0-py_0.conda

# O extraer el paquete
tar -xjf ganimedes-0.1.0-py_0.conda
```

## Mejores Prácticas

1. **Versionado Semántico:** Usa MAJOR.MINOR.PATCH
2. **Testing:** Prueba el paquete en un ambiente limpio antes de subir
3. **Documentación:** Mantén actualizado el README y CHANGELOG
4. **Labels:** Usa labels para versiones de desarrollo (`--label dev`)
5. **CI/CD:** Automatiza la construcción con GitHub Actions

## Recursos Adicionales

- [Conda Build Documentation](https://docs.conda.io/projects/conda-build/)
- [Anaconda.org Documentation](https://docs.anaconda.com/anacondaorg/)
- [Conda-forge Guide](https://conda-forge.org/docs/)
- [Publishing Packages Tutorial](https://docs.anaconda.com/anacondaorg/user-guide/tutorials/publishing-packages/)

## Soporte

Para problemas con el paquete conda:
- Issues: https://github.com/martinvilu/ganimedes/issues
- Conda-forge: https://github.com/conda-forge/staged-recipes
