import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

DOWNLOAD_DIR = Path("./downloads")
CSV_PATH = Path("./combined_data.csv")
SHEET_NAME = "FZ 8.6"

COLS = [
    "Hamburg Plug-in Hybrid",
    "Hamburg Elektro",
    "Hamburg gesamt",
    "Deutschland Plug-in Hybrid",
    "Deutschland Elektro",
    "Deutschland gesamt",
]

def get_target_date() -> tuple[str, str]:
    """Liefert Jahr und Monat (1 Monat zurück)."""
    target_date = datetime.now().replace(day=1) - timedelta(days=60)
    return str(target_date.year), f"{target_date.month:02d}"


def download_file(year: str, month: str) -> Path:
    """Lädt die XLSX-Datei von der KBA-Website."""
    url = f"https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ8/fz8_{year}{month}.xlsx?__blob=publicationFile&v=2"
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DOWNLOAD_DIR / f"fz8_{year}{month}.xlsx"

    print(f"Get data from url: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Save file: {filepath.resolve()}")
    return filepath


def extract_values(filepath: Path) -> dict:
    """Extrahiert die relevanten Werte aus einer XLSX-Datei."""
    print(f"Process file: {filepath.name}")

    name_part = filepath.stem.split("_")[1]
    year, month = name_part[:4], name_part[4:]

    df = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=[7, 8])
    region_col = ("Bundesland", "Unnamed: 1_level_1")
    regions = df[region_col].astype(str)

    row_hh = df[regions.str.contains("Hamburg", case=False, na=False)].iloc[0]
    row_de = df[regions.str.contains("Deutschland", case=False, na=False)].iloc[0]
    hh_plugin = int(row_hh[("Hybrid", "darunter Plug-in")])
    hh_elektro = int(row_hh[("Elektro (BEV)", "Unnamed: 12_level_1")])
    de_plugin = int(row_de[("Hybrid", "darunter Plug-in")])
    de_elektro = int(row_de[("Elektro (BEV)", "Unnamed: 12_level_1")])

    return {
        "Jahr": year,
        "Monat": month,
        "Hamburg Plug-in Hybrid": hh_plugin,
        "Hamburg Elektro": hh_elektro,
        "Hamburg gesamt": hh_plugin + hh_elektro,
        "Deutschland Plug-in Hybrid": de_plugin,
        "Deutschland Elektro": de_elektro,
        "Deutschland gesamt": de_plugin + de_elektro,
    }


def update_csv(new_row: dict):
    """Hängt eine neue Zeile an die CSV an und berechnet kumulierte Spalten neu."""
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH, sep=";")
    else:
        df = pd.DataFrame()
    
    if not df.empty and ((df["Jahr"] == int(new_row["Jahr"])) & (df["Monat"] == int(new_row["Monat"]))).any():
        print(f"Row {new_row['Jahr']}-{new_row['Monat']} already exists. Skipping.")
        return

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    for col in COLS:
        df[f"{col} kumuliert"] = df[col].cumsum()

    df.to_csv(CSV_PATH, index=False, sep=";")
    print(f"Updated CSV: {CSV_PATH.resolve()}")


if __name__ == "__main__":
    year, month = get_target_date()
    filepath = download_file(year, month)
    row = extract_values(filepath)
    update_csv(row)
