from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
import os

app = Flask(__name__)


def extraer_datos(url):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox"])  # necesario para Render
        pagina = navegador.new_page()

        # Evitar cargar recursos innecesarios
        pagina.route("**/*", lambda route, req: route.abort() if req.resource_type in ["image", "font", "stylesheet"] else route.continue_())

        pagina.goto(url, wait_until="domcontentloaded")

        # Tomar captura por si falla algo
        os.makedirs("static", exist_ok=True)
        pagina.screenshot(path="static/debug.png")

        # Extraer datos
        ataques = []
        for fila in pagina.locator(".members-list .member-row").all():
            try:
                jugador = fila.locator(".name").text_content().strip()
                estrellas = fila.locator(".stars .star").count()
                ataques.append({"Jugador": jugador, "Estrellas": estrellas})
            except:
                continue

        navegador.close()

        df = pd.DataFrame(ataques)
        ruta_archivo = "static/datos_guerra.xlsx"
        df.to_excel(ruta_archivo, index=False)
        return ruta_archivo


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generar', methods=['POST'])
def generar():
    url = request.form['url']
    archivo = extraer_datos(url)
    return send_file(archivo, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
