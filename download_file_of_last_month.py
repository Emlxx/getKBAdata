import requests
from pathlib import Path
from datetime import datetime

now = datetime.now()
year = str(now.year)
month = str(now.month - 2)
if len(month) == 1:
    month = "0" + month
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
