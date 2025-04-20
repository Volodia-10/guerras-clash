FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instalar los navegadores de Playwright
RUN python -m playwright install --with-deps

# Puerto para Render
ENV PORT 10000
EXPOSE 10000

CMD ["python", "app.py"]