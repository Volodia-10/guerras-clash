#!/usr/bin/env bash

# Instala dependencias del proyecto
pip install -r requirements.txt

# Instala navegadores y dependencias necesarias para Playwright
playwright install --with-deps