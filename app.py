from flask import Flask, render_template, request, send_file
import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime
import os

app = Flask(__name__)

def extraer_datos(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        # Esperar a que cargue el contenido
        page.wait_for_selector('.war-members')

        # Fecha
        fecha = page.locator('.date-end .param-value').inner_text().split(',')[0].replace('/', '-')

        # Nombre del clan enemigo
        clan_enemigo = page.locator('.clan2 .clan-name').inner_text().strip()

        # Inicializar listas
        nombres = []
        ataque1 = []
        ataque2 = []
        plenos = []

        miembros = page.locator('.war-members .member')

        for i in range(miembros.count()):
            jugador = miembros.nth(i)
            nombre = jugador.locator('.player-name').inner_text()
            estrellas = jugador.locator('.attack-star').all_inner_texts()

            # Añadir a la tabla de ataques
            nombres.append(nombre)
            ataque1.append(int(estrellas[0]) if len(estrellas) > 0 else '')
            ataque2.append(int(estrellas[1]) if len(estrellas) > 1 else '')

            # Verificar si hizo 2 plenos
            if estrellas.count('3') == 2:
                plenos.append(nombre)

        # Crear dataframes
        df_ataques = pd.DataFrame({
            'Name': nombres,
            'Attack 1 Stars': ataque1,
            'Attack 2 Stars': ataque2
        })

        df_plenos = pd.DataFrame({'Plenos': plenos})

        # Nombre del archivo con el clan enemigo y fecha
        nombre_archivo = f'Guerra_{clan_enemigo}_{fecha}.xlsx'

        with pd.ExcelWriter(nombre_archivo) as writer:
            df_ataques.to_excel(writer, sheet_name='Ataques', index=False)
            df_plenos.to_excel(writer, sheet_name='Plenos', index=False)

        browser.close()
        return nombre_archivo

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            archivo_generado = extraer_datos(url)
            return send_file(archivo_generado, as_attachment=True)
        except Exception as e:
            return f"<h1>❌ Error al procesar la URL:</h1><pre>{e}</pre>"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
