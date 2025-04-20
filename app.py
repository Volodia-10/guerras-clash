from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
import os

app = Flask(__name__)

def extraer_datos(url):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox"])
        pagina = navegador.new_page()

        # Bloquear recursos pesados
        pagina.route("**/*", lambda route, request: route.abort()
                     if request.resource_type in ["image", "font", "stylesheet"] else route.continue_())

        # Intentar cargar página
        pagina.goto(url, wait_until="domcontentloaded", timeout=15000)

        # Localizar el nombre del clan
        nombre_clan = pagina.locator(".clan2 .clan-name").text_content().strip().replace(" ", "_")

        # Crear carpetas si no existen
        os.makedirs("static", exist_ok=True)

        # Extraer datos de ataques
        ataques = []
        filas = pagina.locator(".war-table tbody tr")
        for i in range(filas.count()):
            columnas = filas.nth(i).locator("td")
            jugador = columnas.nth(1).text_content().strip()
            estrellas = columnas.nth(4).locator("svg").count()
            ataques.append({"Jugador": jugador, "Estrellas": estrellas})

        df = pd.DataFrame(ataques)
        ruta_archivo = f"static/{nombre_clan}_guerra.xlsx"
        df.to_excel(ruta_archivo, index=False)

        navegador.close()
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
