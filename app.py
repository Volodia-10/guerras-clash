from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def extraer_datos(url):
    # Crear carpeta 'static' si no existe
    os.makedirs("static", exist_ok=True)

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()

        print("Visitando URL:", url)
        pagina.goto(url, wait_until="networkidle")

        # Captura para debug
        pagina.screenshot(path="static/debug.png")
        print("Captura tomada en static/debug.png")

        # Espera a que el clan cargue
        pagina.wait_for_selector(".clan2 .clan-name")
        nombre_clan = pagina.locator(".clan2 .clan-name").text_content().strip().replace(" ", "_")
        print("Clan enemigo:", nombre_clan)

        # Aquí iría tu lógica para recolectar datos de plenos y ataques
        # Simulamos algo sencillo para comprobar que funciona

        plenos = [{"Jugador": "Ejemplo1"}, {"Jugador": "Ejemplo2"}]
        ataques = [{"Jugador": "Ejemplo1"}, {"Jugador": "Ejemplo2"}]

        ruta_archivo = f"static/{nombre_clan}.xlsx"

        with pd.ExcelWriter(ruta_archivo) as writer:
            pd.DataFrame(plenos).to_excel(writer, sheet_name="Plenos", index=False)
            pd.DataFrame(ataques).to_excel(writer, sheet_name="Ataques", index=False)

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
    app.run(host="0.0.0.0", debug=True)
