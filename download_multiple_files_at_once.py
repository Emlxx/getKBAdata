import requests
import time
import pandas as pd

from pathlib import Path
from datetime import datetime

def download_data_since_2023():
    now = datetime.now()
    
    for y in range(2023, now.year + 1):
        for m in range(1, 13):
            if y == now.year and m == now.month:
                break

            year = str(y)
            month = str(m) if m >= 10 else "0" + str(m)
            url = f"https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ8/fz8_{year}{month}.xlsx?__blob=publicationFile&v=2"
            print(f"Checking URL: {url}")

            ziel_ordner = Path("./downloads")
            ziel_ordner.mkdir(parents=True, exist_ok=True)
            ziel_datei = ziel_ordner / f"fz8_{year}{month}.xlsx"

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(ziel_datei, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"File saved in: {ziel_datei.resolve()}")
            time.sleep(1)

def extract_data():
    ordner = Path("./downloads")
    ziel_csv = Path("./combined_data.csv")
    sheet_name = "FZ 8.6"

    rows = []
    for file in sorted(ordner.glob("*.xlsx")):
        print(f"Verarbeite: {file.name}")

        name_part = file.stem.split("_")[1]
        year, month = name_part[:4], name_part[4:]

        df = pd.read_excel(file, sheet_name=sheet_name, header=[7,8])
        region_col = ('Bundesland', 'Unnamed: 1_level_1')
        region_series = df[region_col].astype(str)

        row_hh = df[region_series.str.contains("Hamburg", case=False, na=False)].iloc[0]
        row_de = df[region_series.str.contains("Deutschland", case=False, na=False)].iloc[0]
        hh_plugin = int(row_hh[('Hybrid', 'darunter Plug-in')])
        hh_elektro = int(row_hh[('Elektro (BEV)', 'Unnamed: 12_level_1')])
        de_plugin = int(row_de[('Hybrid', 'darunter Plug-in')])
        de_elektro = int(row_de[('Elektro (BEV)', 'Unnamed: 12_level_1')])

        rows.append({
            "Jahr": year,
            "Monat": month,
            "Hamburg Plug-in Hybrid": hh_plugin,
            "Hamburg Elektro": hh_elektro,
            "Hamburg gesamt": hh_elektro + hh_plugin,
            "Deutschland Plug-in Hybrid": de_plugin,
            "Deutschland Elektro": de_elektro,
            "Deutschland gesamt": de_plugin + de_elektro
        })

    out_df = pd.DataFrame(rows)
    for col in [
        "Hamburg Plug-in Hybrid",
        "Hamburg Elektro",
        "Hamburg gesamt",
        "Deutschland Plug-in Hybrid",
        "Deutschland Elektro",
        "Deutschland gesamt"
    ]:
        out_df[f"{col} kumuliert"] = out_df[col].cumsum()

    out_df.to_csv(ziel_csv, index=False, sep=";")
    print(f"Saved file in: {ziel_csv.resolve()}")

download_data_since_2023()
extract_data()
