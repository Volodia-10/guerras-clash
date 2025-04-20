#!/usr/bin/env bash

# Instala las dependencias de Python
pip install -r requirements.txt

# Instala los navegadores de Playwright correctamente
python -m playwright install chromium --with-deps
