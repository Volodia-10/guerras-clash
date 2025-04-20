# Imagen base oficial de Python con Playwright
FROM mcr.microsoft.com/playwright/python:v1.41.1-jammy

# Establecer directorio de trabajo
WORKDIR /app

# Copiar todos los archivos del proyecto
COPY . .

# Instalar dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores de Playwright
RUN playwright install --with-deps

# Exponer el puerto que usará Flask (Render usará este)
EXPOSE 10000

# Comando para ejecutar la app
CMD ["python", "app.py"]