# Receta Conda para Ganimedes

Esta es la receta para construir el paquete Conda de Ganimedes.

## Estructura

```
conda-recipe/
├── meta.yaml       # Metadatos del paquete y dependencias
├── build.sh        # Script de construcción para Linux/macOS
├── bld.bat         # Script de construcción para Windows
└── README.md       # Este archivo
```

## Construcción

```bash
# Desde el directorio raíz del proyecto
conda build conda-recipe

# O con directorio de salida específico
conda build conda-recipe --output-folder ./dist/conda
```

## Configuración

### meta.yaml

- **Versión**: Debe coincidir con `pyproject.toml`
- **Dependencias**: Sincronizadas con `requirements` en `pyproject.toml`
- **Build number**: Incrementar para rebuilds con la misma versión

### Noarch Package

Este paquete está marcado como `noarch: python` porque:
- Es código Python puro
- No tiene dependencias específicas de plataforma
- Funciona en Linux, macOS y Windows

## Dependencias

### Host Dependencies
Se necesitan durante la construcción:
- python >=3.11
- pip
- setuptools

### Run Dependencies
Se necesitan para ejecutar:
- Todas las dependencias listadas en `pyproject.toml`

### Dependencias PyPI

Algunas dependencias (como `supabase`) solo están en PyPI. Esto está bien porque:
1. Se instalan automáticamente con pip durante `conda build`
2. conda puede resolver dependencias mixtas conda/pip

## Actualización

Para actualizar a una nueva versión:

1. Actualizar `version` en `pyproject.toml`
2. Actualizar `{% set version = "X.Y.Z" %}` en `meta.yaml`
3. Reconstruir: `conda build conda-recipe`

## Testing

El paquete incluye tests básicos:
- Import tests para todos los módulos
- `pip check` para verificar dependencias

Para tests más completos, usar:
```bash
./scripts/test-conda-package.sh
```

## Publicación

Ver [CONDA_BUILD.md](../CONDA_BUILD.md) para instrucciones completas de publicación en Anaconda.org.

## Troubleshooting

### Error: "Package missing"

Si una dependencia no se encuentra en conda:
1. Buscar en conda-forge: `conda search -c conda-forge paquete`
2. Si está solo en PyPI, agregar a la sección pip de `meta.yaml`

### Build number

El build number se incrementa cuando:
- Se corrige la receta sin cambiar la versión del software
- Se agregan parches
- Se actualizan dependencias sin cambiar el código

Resetear a 0 cuando se incrementa la versión del software.
