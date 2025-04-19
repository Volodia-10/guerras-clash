from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

def extraer_datos(url):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(url, wait_until="domcontentloaded")

        # Nombre del clan enemigo
        nombre_clan = pagina.locator(".clan2 .clan-name").text_content().strip().replace(" ", "_")

        # Fecha actual para el nombre del archivo
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        # Obtener plenos
        elementos_plenos = pagina.locator('xpath=//div[text()="Plenos"]/following-sibling::div').all_inner_texts()
        plenos = [linea for linea in elementos_plenos if linea.strip() != ""]

        # Obtener ataques
        elementos_ataques = pagina.locator('xpath=//div[text()="Ataques"]/following-sibling::div').all_inner_texts()
        ataques = [linea for linea in elementos_ataques if linea.strip() != ""]

        # Crear DataFrames
        df_plenos = pd.DataFrame(plenos, columns=["Jugador"])
        df_ataques = pd.DataFrame(ataques, columns=["Jugador"])

        # Crear carpeta static si no existe
        os.makedirs("static", exist_ok=True)

        # Guardar en archivo Excel dentro de la carpeta static/
        nombre_archivo = f"Guerra_{nombre_clan}_{fecha_actual}.xlsx"
        ruta_archivo = os.path.join("static", nombre_archivo)

        with pd.ExcelWriter(ruta_archivo) as writer:
            df_plenos.to_excel(writer, sheet_name='Plenos', index=False)
            df_ataques.to_excel(writer, sheet_name='Ataques', index=False)

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
