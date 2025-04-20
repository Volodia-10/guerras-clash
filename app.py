from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
import os

app = Flask(__name__)

def extraer_datos(url):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox"])
        contexto = navegador.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        pagina = contexto.new_page()

        # Bloquear recursos innecesarios
        pagina.route("**/*", lambda route, request: route.abort() if request.resource_type in ["image", "font", "stylesheet"] else route.continue_())

        # Intentar ir a la URL
        try:
            pagina.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            pagina.screenshot(path="static/error_goto.png")
            raise Exception(f"Error al cargar la página: {str(e)}")

        # Captura de depuración
        pagina.screenshot(path="static/debug.png")

        # Esperar selector principal
        try:
            pagina.wait_for_selector(".clan2 .clan-name", timeout=10000)
        except Exception as e:
            raise Exception("No se encontró el selector del nombre del clan")

        nombre_clan = pagina.locator(".clan2 .clan-name").text_content().strip().replace(" ", "_")

        plenos = []
        ataques = []

        for fila in pagina.locator(".attacks-table tbody tr").all():
            columnas = fila.locator("td").all()
            jugador = columnas[0].text_content().strip()
            estrellas = columnas[1].text_content().strip()
            porcentaje = columnas[2].text_content().strip()

            if estrellas == "3":
                plenos.append({"Jugador": jugador, "Porcentaje": porcentaje})

            ataques.append({"Jugador": jugador, "Estrellas": estrellas, "Porcentaje": porcentaje})

        df_plenos = pd.DataFrame(plenos)
        df_ataques = pd.DataFrame(ataques)

        os.makedirs("static", exist_ok=True)
        ruta_archivo = f"static/{nombre_clan}.xlsx"
        with pd.ExcelWriter(ruta_archivo) as writer:
            df_plenos.to_excel(writer, sheet_name="Plenos", index=False)
            df_ataques.to_excel(writer, sheet_name="Ataques", index=False)

        navegador.close()
        return ruta_archivo

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generar", methods=["POST"])
def generar():
    url = request.form['url']
    archivo = extraer_datos(url)
    return send_file(archivo, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
