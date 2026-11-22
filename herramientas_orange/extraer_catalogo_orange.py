#!/usr/bin/env python3
"""Diagnóstico de imágenes externas de Revista Orange. No modifica el CRM."""
import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

ROOT = "https://revista.orange.es"
CATEGORIES = [
    "Audio y Fotografía", "Gaming", "Hogar", "Imagen y Sonido",
    "Informática", "Movilidad", "Relojes y Wearables", "Smartphones",
]
OUT = Path("salida_catalogo_orange")
OUT.mkdir(exist_ok=True)
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0 (compatible; OrangeCatalogValidation/1.0)",
                        "Accept": "text/html,application/xhtml+xml"})
TIMEOUT = 20
ROWS = OrderedDict()
REPORT = []
IMAGE_KEYS = ("data-src", "data-original", "data-lazy-src", "src", "srcset", "data-srcset")

def image_candidates(img):
    for key in IMAGE_KEYS:
        value = (img.get(key) or "").strip()
        if not value:
            continue
        if key.endswith("srcset"):
            value = value.split(",")[0].strip().split(" ")[0]
        if value.startswith("data:"):
            continue
        yield urljoin(ROOT, value)

def image_from_card(anchor):
    # Prefer an image inside the same product link, then the closest product container.
    candidates = [anchor]
    parent = anchor.parent
    for _ in range(3):
        if parent is None:
            break
        candidates.append(parent)
        parent = parent.parent
    for container in candidates:
        for img in container.find_all("img"):
            for url in image_candidates(img):
                if "/uploads/dispositivos/" in urlparse(url).path:
                    return url
    return ""

for category in CATEGORIES:
    url = ROOT + "/dispositivos/filtrar?" + urlencode({"filtro_tipo[]": category})
    found = 0
    try:
        response = SESSION.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.select('a[href*="/dispositivos/ficha/"]'):
            href = urljoin(response.url, a.get("href", ""))
            match = re.search(r"/dispositivos/ficha/([^/?#]+)", urlparse(href).path)
            if not match:
                continue
            device_id = match.group(1)
            h = a.find(["h3", "h2", "h4"])
            if h is None:
                # Some cards place the title next to the image link.
                for parent in [a.parent, a.parent.parent if a.parent else None]:
                    if parent:
                        h = parent.find(["h3", "h2", "h4"])
                        if h:
                            break
            if h is None:
                continue
            name = h.get_text(" ", strip=True)
            if not name:
                continue
            image_url = image_from_card(a)
            key = device_id
            if key not in ROWS:
                ROWS[key] = {"categoria": category, "id": device_id,
                             "nombre": name, "imagen_url": image_url, "ficha_url": href,
                             "estado_imagen": "pendiente"}
                found += 1
            elif image_url and not ROWS[key]["imagen_url"]:
                ROWS[key]["imagen_url"] = image_url
        REPORT.append({"categoria": category, "http": response.status_code,
                       "encontrados_nuevos": found, "error": ""})
        print(f"{category}: HTTP {response.status_code}, nuevos {found}")
    except requests.RequestException as exc:
        REPORT.append({"categoria": category, "http": "", "encontrados_nuevos": 0,
                       "error": str(exc)[:250]})
        print(f"{category}: ERROR {exc}")
    time.sleep(0.5)

# Validate all URLs concurrently. Read only HTTP headers; never save image bytes.
def check_image(row):
    if not row["imagen_url"]:
        return row["id"], "sin_url"
    try:
        response = requests.get(row["imagen_url"], timeout=12, stream=True,
                                headers={"Range": "bytes=0-1023",
                                         "User-Agent": "Mozilla/5.0"})
        mime = response.headers.get("Content-Type", "").split(";")[0].lower()
        status = response.status_code
        response.close()
        if status in (200, 206) and mime.startswith("image/"):
            return row["id"], "ok"
        return row["id"], f"no_valida_http_{status}_{mime}"
    except requests.RequestException as exc:
        return row["id"], "error_" + type(exc).__name__

with ThreadPoolExecutor(max_workers=12) as pool:
    futures = [pool.submit(check_image, row) for row in ROWS.values()]
    for future in as_completed(futures):
        device_id, status = future.result()
        ROWS[device_id]["estado_imagen"] = status
checked = sum(bool(row["imagen_url"]) for row in ROWS.values())
valid = sum(row["estado_imagen"] == "ok" for row in ROWS.values())
print(f"VALIDACION: {valid}/{checked} URLs HTTP imagen correctas")

columns = ["categoria", "id", "nombre", "imagen_url", "ficha_url", "estado_imagen"]
with (OUT / "catalogo_orange.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(ROWS.values())
with (OUT / "catalogo_orange.json").open("w", encoding="utf-8") as f:
    json.dump(list(ROWS.values()), f, ensure_ascii=False, indent=2)
with (OUT / "resumen_categorias.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["categoria", "http", "encontrados_nuevos", "error"])
    writer.writeheader()
    writer.writerows(REPORT)
print(f"TOTAL: {len(ROWS)} modelos | con URL: {sum(bool(x['imagen_url']) for x in ROWS.values())} | piloto comprobado: {checked}")
print("Los resultados son candidatos: revisar correspondencia visual antes de integrar.")
