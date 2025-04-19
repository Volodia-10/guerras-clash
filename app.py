import os
import datetime
import pandas as pd
from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import subprocess

# Asegura que los navegadores estén instalados al iniciar
subprocess.run(["playwright", "install", "--with-deps"], check=True)

app = Flask(__name__)

def extraer_datos(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Extraer nombre del clan enemigo
        clan_enemigo = page.query_selector("div.clan.clan2 .clan-name").inner_text().strip()

        # Extraer fecha de la guerra
        fecha = page.query_selector("p.date-end span.param-value").inner_text().split(",")[0].strip().replace("/", "-")

        nombres = []
        ataque_1 = []
        ataque_2 = []

        filas = page.query_selector_all("table.members tbody tr")
        for fila in filas:
            celdas = fila.query_selector_all("td")
            if len(celdas) >= 3:
                nombres.append(celdas[0].inner_text().strip())
                ataque_1.append(celdas[1].inner_text().strip())
                ataque_2.append(celdas[2].inner_text().strip())

        browser.close()

        # Crear DataFrames
        df_ataques = pd.DataFrame({
            "Name": nombres,
            "Attack 1 Stars": ataque_1,
            "Attack 2 Stars": ataque_2
        })

        plenos = df_ataques[
            (df_ataques["Attack 1 Stars"] == "3") & (df_ataques["Attack 2 Stars"] == "3")
        ][["Name"]].copy()

        # Crear archivo Excel
        nombre_archivo = f"Guerra_{clan_enemigo}_{fecha}.xlsx"
        ruta_archivo = os.path.join("static", nombre_archivo)

        with pd.ExcelWriter(ruta_archivo) as writer:
            df_ataques.to_excel(writer, sheet_name="Ataques", index=False)
            plenos.to_excel(writer, sheet_name="Plenos", index=False)

        return ruta_archivo

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        archivo = extraer_datos(url)
        return send_file(archivo, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
