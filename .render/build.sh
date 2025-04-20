#!/usr/bin/env bash

# Instala dependencias de Python
pip install -r requirements.txt

# Instala navegadores para Playwright
python -m playwright install --with-deps
