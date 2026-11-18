#!/usr/bin/env python3
"""Auditoría de imágenes públicas Orange; no escribe en CRM ni descarga imágenes."""
import csv, json, time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

BASE = "https://revista.orange.es"
CATEGORIES = ["Smartphones", "Audio y Fotografía", "Relojes y Wearables"]
OUT = Path("informes_imagenes")
OUT.mkdir(exist_ok=True)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.title, self.in_title = [], [], "", False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self.in_title = True
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "img":
            src = a.get("data-src") or a.get("src") or a.get("data-original")
            if src: self.images.append((src, a.get("alt", "")))
        if tag == "meta" and a.get("property") in ("og:image", "twitter:image") and a.get("content"):
            self.images.append((a["content"], a["property"]))
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title += data

def fetch(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"})
    with urlopen(req, timeout=20) as response:
        raw = response.read(3000000)
        final, status = response.url, response.status
    page = Page()
    page.feed(raw.decode("utf-8", "replace"))
    return status, final, page

rows, errors, seen = [], [], set()
def add_images(category, url, page, source):
    for src, alt in page.images:
        img = urljoin(url, src)
        if urlparse(img).scheme not in ("http", "https"): continue
        rows.append(dict(categoria_origen=category, titulo_ficha=page.title.strip(),
                         url_ficha=url, imagen_url=img, alt=alt,
                         origen=source, estado="candidata_sin_verificar"))

for category in CATEGORIES:
    url = BASE + "/dispositivos/filtrar?" + urlencode({"filtro_tipo[]": category})
    try:
        status, final, page = fetch(url)
        print(category, "HTTP", status, "enlaces", len(page.links), "imágenes", len(page.images))
        add_images(category, final, page, "listado")
        links = []
        for href in page.links:
            link = urljoin(final, href).split("#")[0]
            parsed = urlparse(link)
            if parsed.netloc == urlparse(BASE).netloc and "/dispositivos/" in parsed.path and "/filtrar" not in parsed.path:
                links.append(link)
        for link in dict.fromkeys(links):
            if link in seen: continue
            seen.add(link)
            try:
                status, final2, detail = fetch(link)
                add_images(category, final2, detail, "ficha")
                time.sleep(.15)
            except Exception as e:
                errors.append({"url": link, "error": str(e)})
    except Exception as e:
        errors.append({"url": url, "error": str(e)})
        print("ERROR", category, str(e))
fields = ["categoria_origen","titulo_ficha","url_ficha","imagen_url","alt","origen","estado"]
with (OUT / "candidatas.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
(OUT / "errores.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "resumen.json").write_text(json.dumps({"fichas_exploradas":len(seen),
    "imagenes_candidatas":len(rows),"errores":len(errors),
    "advertencia":"No son coincidencias verificadas ni deben importarse al CRM"},ensure_ascii=False,indent=2),encoding="utf-8")
print("RESULTADO:", len(seen), "fichas,", len(rows), "imágenes candidatas,", len(errors), "errores")
