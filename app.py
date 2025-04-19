from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from datetime import datetime
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def scrap_guerra(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)

        page.wait_for_selector('.clan1')
        members = page.query_selector_all('.clan1')

        data = []
        plenos = []

        # Extraer fecha real de la guerra
        try:
            fecha_str = page.query_selector('.date-end .param-value').inner_text().strip()
            guerra_date = datetime.strptime(fecha_str, '%m/%d/%y, %I:%M %p').strftime('%Y-%m-%d')
        except:
            guerra_date = 'fecha-desconocida'

        # Extraer nombre del clan enemigo (clan2)
        try:
            nombre_clan_enemigo = page.query_selector('.clan2 .clan-name').inner_text().strip().replace(" ", "_")
        except:
            nombre_clan_enemigo = 'clan_enemigo_desconocido'

        for member in members:
            try:
                name = member.query_selector('.player-name').inner_text().strip()
                attack_stars = member.query_selector_all('.attack-stars')
                stars = []

                for atk in attack_stars:
                    classes = atk.get_attribute('class')
                    for n in range(4):
                        if f'stars-{n}' in classes:
                            stars.append(n)
                            break

                if stars:
                    data.append({
                        'Name': name,
                        'Attack 1 Stars': stars[0] if len(stars) > 0 else '-',
                        'Attack 2 Stars': stars[1] if len(stars) > 1 else '-'
                    })

                    if len(stars) > 1 and stars[0] == 3 and stars[1] == 3:
                        plenos.extend([name] * 3)
                    elif 3 in stars:
                        plenos.append(name)

            except:
                continue

        browser.close()

        # Guardar Excel con nombre personalizado
        df = pd.DataFrame(data)
        df_plenos = pd.DataFrame({'Plenos': plenos})
        filename = f'Guerra_{nombre_clan_enemigo}_{guerra_date}.xlsx'

        with pd.ExcelWriter(filename) as writer:
            df.to_excel(writer, sheet_name='Ataques', index=False)
            df_plenos.to_excel(writer, sheet_name='Plenos', index=False)

        return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if url:
            filename = scrap_guerra(url)
            return send_file(filename, as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
