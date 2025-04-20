from flask import Flask, request, send_file, render_template
from playwright.sync_api import sync_playwright
import pandas as pd
import os

app = Flask(__name__)

def extraer_datos(url):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        contexto = navegador.new_context()
        pagina = contexto.new_page()

        # Bloquear imágenes, fuentes y hojas de estilo
        pagina.route("**/*", lambda route, request: route.abort()
                     if request.resource_type in ["image", "font", "stylesheet"]
                     else route.continue_())

        # Cargar la URL
        pagina.goto(url, wait_until="domcontentloaded")
        pagina.wait_for_timeout(5000)  # Espera adicional de 5 segundos

        # Crear carpeta 'static' si no existe
        os.makedirs("static", exist_ok=True)

        # Captura de pantalla para depuración
        pagina.screenshot(path="static/debug.png")

        # Esperar a que aparezcan los elementos clave
        pagina.wait_for_selector(".clan2 .clan-name")
        pagina.wait_for_selector(".clan1 .clan-name")

        # Nombre del clan enemigo
        nombre_clan = pagina.locator(".clan2 .clan-name").text_content().strip().replace(" ", "_")

        # Tablas
        filas_plenos = pagina.locator("#perfect .content .row").all()
        filas_ataques = pagina.locator("#attacks .content .row").all()

        datos_plenos = []
        for fila in filas_plenos:
            jugador = fila.locator(".title").text_content().strip()
            datos_plenos.append([jugador])

        datos_ataques = []
        for fila in filas_ataques:
            jugador = fila.locator(".title").text_content().strip()
            datos_ataques.append([jugador])

        # DataFrames
        df_plenos = pd.DataFrame(datos_plenos, columns=["Jugador"])
        df_ataques = pd.DataFrame(datos_ataques, columns=["Jugador"])

        # Guardar Excel
        ruta_archivo = f"static/{nombre_clan}_guerra.xlsx"
        with pd.ExcelWriter(ruta_archivo) as writer:
            df_plenos.to_excel(writer, sheet_name="Plenos", index=False)
            df_ataques.to_excel(writer, sheet_name="Ataques", index=False)

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
