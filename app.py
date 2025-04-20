from flask import Flask, render_template, request, send_file
from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

def extraer_datos(url):
    os.makedirs("static", exist_ok=True)

    with sync_playwright() as p:
        navegador = p.firefox.launch(headless=True, args=["--no-sandbox"])
        pagina = navegador.new_page()

        # Bloqueamos imágenes, fuentes y estilos para mejorar rendimiento
        def filtrar_recursos(route, request):
            if request.resource_type in ["image", "font", "stylesheet"]:
                route.abort()
            else:
                route.continue_()

        pagina.route("**/*", filtrar_recursos)

        print("🌐 Visitando URL:", url)

        try:
            pagina.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            print("❌ Error al cargar la página:", e)
            navegador.close()
            raise Exception("Error al acceder a la URL proporcionada.")

        # Intentar captura para depuración
        try:
            pagina.screenshot(path="static/debug.png", timeout=5000)
            print("📸 Captura tomada correctamente")
        except Exception as e:
            print("⚠️ No se pudo tomar la captura:", e)

        # Intentar extraer el nombre del clan enemigo
        try:
            pagina.wait_for_selector(".clan2 .clan-name")
            nombre_clan = pagina.locator(".clan2 .clan-name").text_content().strip().replace(" ", "_")
        except Exception as e:
            print("⚠️ No se pudo extraer el nombre del clan enemigo:", e)
            nombre_clan = "Clan_Desconocido"

        print("👑 Clan enemigo detectado:", nombre_clan)

        # Simulación de datos (reemplaza con scraping real)
        plenos = [{"Jugador": "Ejemplo1"}, {"Jugador": "Ejemplo2"}]
        ataques = [{"Jugador": "Ejemplo1"}, {"Jugador": "Ejemplo2"}]

        # Crear nombre del archivo con fecha
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
