#!/usr/bin/env python3
"""Fase 1 de fotos Renove: inventario real + comprobacion de fuentes. SOLO LECTURA.
Ejecutar desde /home/tienda/tienda: python herramientas/imagenes_orange/preparar_cruce_fotos_v1.py
No cambia base de datos, plantillas, precios ni promociones.
"""
import csv, json, os, re, sys, urllib.request, urllib.error
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path('/home/tienda/tienda')
sys.path.insert(0,str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'fuentes_revista_orange_46.csv'
OUT=HERE/'resultado_fotos'
OUT.mkdir(exist_ok=True)

def write_csv(path,fields,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

devices=[{'tipo':'dispositivo','id':str(d.pk),'nombre':' '.join(str(getattr(d,k,'') or '').strip() for k in ('marca','modelo','capacidad')).strip(),'marca':str(d.marca or ''),'categoria':str(d.categoria or ''),'imagen_actual':str(d.imagen_url or '')} for d in Dispositivo.objects.all().order_by('marca','modelo','capacidad')]
template=ROOT/'crm/templates/crm/renove_particular.html'
accessories=[]
if template.is_file():
    s=template.read_text(encoding='utf-8')
    m=re.search(r'<script\\s+id=["\\\']renove-segunda-venta["\\\']\\s+type=["\\\']application/json["\\\']\\s*>(.*?)</script>',s,re.S|re.I)
    if m:
        for i,x in enumerate(json.loads(m.group(1))):
            accessories.append({'tipo':'accesorio','id':str(x.get('id',i)),'nombre':str(x.get('nombre','')),'marca':str(x.get('marca','')),'categoria':str(x.get('categoria','')),'imagen_actual':str(x.get('imagen_url') or '')})
    else:print('AVISO: bloque renove-segunda-venta no encontrado')
fields=['tipo','id','nombre','marca','categoria','imagen_actual']
write_csv(OUT/'inventario_real.csv',fields,devices+accessories)

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__();self.images=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag in ('img','source'):
            src=d.get('data-src') or d.get('src') or d.get('srcset') or ''
            if src:self.images.append((d.get('alt',''),src[:500]))
        if tag=='a' and d.get('href'):
            self.links.append((d.get('title',''),d['href'][:500]))

results=[]
with SOURCE.open(encoding='utf-8',newline='') as f:
    sources=list(csv.DictReader(f))
for n,row in enumerate(sources,1):
    url=row['url']
    entry={'categoria':row['categoria'],'marca':row['marca'],'url':url,'estado':'','http':'','imagenes_html':'0','enlaces_html':'0','detalle':''}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; RenoveCatalogAudit/1.0)','Accept':'text/html'})
        with urllib.request.urlopen(req,timeout=12) as r:
            data=r.read(2_000_000);entry['http']=str(r.status);ctype=r.headers.get('Content-Type','')
        if 'html' not in ctype.lower():entry['estado']='NO_HTML';entry['detalle']=ctype
        else:
            p=PageParser();p.feed(data.decode('utf-8','replace'))
            entry['imagenes_html']=str(len(p.images));entry['enlaces_html']=str(len(p.links))
            entry['estado']='HTML_RECIBIDO' if p.images or p.links else 'HTML_SIN_ELEMENTOS'
    except urllib.error.HTTPError as e:entry['estado']='HTTP_ERROR';entry['http']=str(e.code);entry['detalle']=str(e.reason)[:160]
    except Exception as e:entry['estado']='ERROR_CONEXION';entry['detalle']=str(e)[:180]
    results.append(entry)
    print(f"[{n}/{len(sources)}] {row['categoria']} / {row['marca']}: {entry['estado']} ({entry['http']})",flush=True)
write_csv(OUT/'estado_fuentes.csv',['categoria','marca','url','estado','http','imagenes_html','enlaces_html','detalle'],results)
print('Inventario:',len(devices),'dispositivos,',len(accessories),'accesorios')
print('Fuentes:',len(sources),'| HTML accesible:',sum(x['estado']=='HTML_RECIBIDO' for x in results))
print('Archivos:',OUT/'inventario_real.csv',OUT/'estado_fuentes.csv')
print('SOLO LECTURA: ninguna fotografia asignada; ningun precio modificado.')
