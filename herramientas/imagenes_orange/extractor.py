#!/usr/bin/env python3
"""Auditoría pública de imágenes de Revista Orange. No modifica el CRM."""
import csv, json, re, time
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen
from html.parser import HTMLParser

BASE="https://revista.orange.es"
CATEGORIES=["Smartphones","Audio y Fotografía","Relojes y Wearables"]
OUT=Path("informes_imagenes"); OUT.mkdir(exist_ok=True)
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.images=[]; self.title=""; self._title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="title": self._title=True
        if tag=="a" and a.get("href"): self.links.append(a["href"])
        if tag=="img":
            src=a.get("data-src") or a.get("src") or a.get("data-original")
            if src:self.images.append((src,a.get("alt","")))
        if tag=="meta" and a.get("property")=="og:image" and a.get("content"):
            self.images.append((a["content"],"og:image"))
    def handle_endtag(self,tag):
        if tag=="title": self._title=False
    def handle_data(self,data):
        if self._title:self.title+=data
def fetch(url):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; CatalogAudit/1.0)"})
    with urlopen(req,timeout=20) as r:
        data=r.read(2500000); final=r.url; status=r.status
    p=Page();p.feed(data.decode("utf-8","replace"))
    return status,final,p
rows=[]; errors=[]; seen=set()
for cat in CATEGORIES:
    url=BASE+"/dispositivos/filtrar?"+urlencode({"filtro_tipo[]":cat})
    try:
        status,final,page=fetch(url)
        print(cat,status,"links",len(page.links),"images",len(page.images))
        candidates=[]
        for href in page.links:
            link=urljoin(final,href)
            if urlparse(link).netloc==urlparse(BASE).netloc and "/dispositivos/ficha/" in link:
                candidates.append(link.split("#")[0])
        for link in dict.fromkeys(candidates):
            if link in seen:continue
            seen.add(link)
            try:
                s,final2,p=fetch(link)
                for img,alt in p.images:
                    img=urljoin(final2,img)
                    if img.startswith("https://"):
                        rows.append({"categoria_origen":cat,"titulo_ficha":p.title.strip(),"url_ficha":final2,"imagen_url":img,"alt":alt,"estado":"candidata_sin_verificar"})
                time.sleep(.2)
            except Exception as e:errors.append({"url":link,"error":str(e)})
    except Exception as e:
        print("ERROR",cat,str(e));errors.append({"url":url,"error":str(e)})
with (OUT/"candidatas.csv").open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=["categoria_origen","titulo_ficha","url_ficha","imagen_url","alt","estado"]);w.writeheader();w.writerows(rows)
(OUT/"errores.json").write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding="utf-8")
print("Fichas",len(seen),"imágenes candidatas",len(rows),"errores",len(errors))
print("IMPORTANTE: candidatas sin validar; NO importar directamente al CRM.")
