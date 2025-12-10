#!/bin/bash

set -ex

# Instalar el paquete usando pip
$PYTHON -m pip install . --no-deps --ignore-installed -vv
