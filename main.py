from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
import openpyxl

app = Flask(__name__)

def extraer_datos(url):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.goto(url, wait_until="networkidle")

        datos = []
        miembros = pagina.query_selector_all(".member-row")

        for miembro in miembros:
            nombre = miembro.query_selector(".name") or miembro.query_selector("a")
            estrellas = miembro.query_selector(".stars")

            if nombre and estrellas:
                datos.append({
                    "Jugador": nombre.inner_text().strip(),
                    "Estrellas": estrellas.inner_text().strip()
                })

        navegador.close()

        df = pd.DataFrame(datos)
        ruta = "resultado.xlsx"
        df.to_excel(ruta, index=False, sheet_name="Estrellas")
        return ruta

@app.route("/", methods=["GET"])
def formulario():
    return render_template("index.html")

@app.route("/generar", methods=["POST"])
def generar():
    url = request.form["url"]
    archivo = extraer_datos(url)
    return send_file(archivo, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
