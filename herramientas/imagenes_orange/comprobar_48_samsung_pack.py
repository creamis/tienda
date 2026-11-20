#!/usr/bin/env python3
"""Audita cuotas 24/48 de dos accesorios del pack, sin modificar archivos."""
from pathlib import Path
import re,json
p=Path('/home/tienda/tienda/crm/templates/crm/renove_particular.html')
s=p.read_text(encoding='utf-8')
m=re.search(r'<script id="renove-segunda-venta" type="application/json">(.*?)</script>',s,re.S)
if not m:raise SystemExit('ERROR: catálogo no localizado')
items=json.loads(m.group(1))
for query in ('SAMSUNG GALAXY BUDS 4','SAMSUNG GALAXY WATCH 8 40MM'):
 print('\n===',query,'===')
 matches=[a for a in items if query in a.get('nombre','').upper()]
 for a in matches:
  print('Nombre:',a.get('nombre'))
  for key in ('cuota','cuota_48','inicial','inicial_48','tipo'):
   print(' ',key,':',repr(a.get(key,'NO EXISTE')))
  print(' Financiación 48 disponible:',isinstance(a.get('cuota_48'),(int,float)))
 if not matches:print('NO ENCONTRADO EN CATÁLOGO')
print('\nOtros Samsung con 48 meses:')
for a in items:
 if 'SAMSUNG' in a.get('nombre','').upper() and isinstance(a.get('cuota_48'),(int,float)):
  print(a['nombre'],'24:',a.get('cuota'),'48:',a['cuota_48'])
print('\nSOLO LECTURA.')
