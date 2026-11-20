#!/usr/bin/env python3
"""Diagnostico de rutas y conectividad para fotos Renove. Solo lectura."""
import os,sys,re,urllib.request,urllib.error,json
from pathlib import Path
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo
print('=== RUTAS ===')
for p in [root/'crm/templates/crm/renove_particular.html',root/'crm/templates',root/'templates',root/'herramientas/imagenes_orange/resultado_fotos/estado_fuentes.csv']:
 print(str(p), 'EXISTE' if p.exists() else 'NO EXISTE')
print('=== BUSQUEDA DE CATALOGO ACCESORIOS ===')
found=[]
for base in [root/'crm',root/'templates']:
 if not base.exists():continue
 for p in base.rglob('*.html'):
  try:
   s=p.read_text(encoding='utf-8')
   if 'renove-segunda-venta' in s or 'AIRPODS PRO 3' in s:
    found.append((p,s))
  except Exception:pass
for p,s in found[:10]:
 print('Archivo:',p)
 for term in ['renove-segunda-venta','AIRPODS PRO 3']:
  at=s.find(term)
  if at>=0:print(' Fragmento:',repr(s[max(0,at-110):at+160]))
print('Archivos candidatos:',len(found))
print('=== ERRORES REALES DE CONEXION (PRIMEROS 4) ===')
p=root/'herramientas/imagenes_orange/resultado_fotos/estado_fuentes.csv'
if p.exists():
 import csv
 with p.open(encoding='utf-8-sig') as f:
  for row in list(csv.DictReader(f))[:4]:
   print(row['marca'],row['estado'],row['detalle'])
print('=== COMPROBACION BREVE DE RED ===')
for u in ['https://revista.orange.es/','https://www.google.com/']:
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=6) as r:print(u,'HTTP',r.status)
 except Exception as e:print(u,type(e).__name__,str(e)[:220])
print('FIN: SOLO LECTURA')
