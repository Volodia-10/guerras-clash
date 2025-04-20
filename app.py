from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

def extraer_datos(url):
    # Asegura que la carpeta 'static' exista
    os.makedirs("static", exist_ok=True)

    with sync_playwright() as p:
        # Soluciona crashes con --no-sandbox
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox"])
        pagina = navegador.new_page()

        print("🌐 Visitando URL:", url)
        pagina.goto(url, wait_until="networkidle")

        # Captura de pantalla para depurar visualmente en Render
        pagina.screenshot(path="static/debug.png")
        print("📸 Captura tomada en static/debug.png")

        # Esperar a que cargue el clan enemigo
        pagina.wait_for_selector(".clan2 .clan-name")
        nombre_clan = pagina.locator(".clan2 .clan-name").text_content().strip().replace(" ", "_")
        print("👑 Clan enemigo detectado:", nombre_clan)

        # Simulación de extracción de datos (aquí debes colocar tu lógica real)
        plenos = [{"Jugador": "Ejemplo1"}, {"Jugador": "Ejemplo2"}]
        ataques = [{"Jugador": "Ejemplo1"}, {"Jugador": "Ejemplo2"}]

        # Guardar archivo Excel en carpeta 'static'
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"Guerra_{nombre_clan}_{fecha_actual}.xlsx"
        ruta_archivo = os.path.join("static", nombre_archivo)

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
