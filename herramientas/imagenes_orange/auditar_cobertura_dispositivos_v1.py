#!/usr/bin/env python3
"""Auditoría de cobertura del catálogo Renove. SOLO LECTURA."""
from pathlib import Path
from collections import Counter,defaultdict
import os,sys
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo,PrecioRenove
from django.db.models import Count
import re
all_devices=list(Dispositivo.objects.all().order_by('marca','modelo','capacidad'))
print('=== RESUMEN ===')
print('Dispositivos:',len(all_devices))
print('Categorias:',dict(Counter(str(d.categoria) for d in all_devices)))
print('Activos:',sum(bool(d.activo) for d in all_devices))
visible=lambda d: bool(d.activo) and bool(re.search(r'smartphone|m[oó]vil|telefono',str(d.categoria or ''),re.I))
print('Visibles segun filtro JS:',sum(visible(d) for d in all_devices))
print('No visibles:',sum(not visible(d) for d in all_devices))
print('\n=== OPPO A6X Y SIMILARES ===')
found=[d for d in all_devices if 'A6' in (' '.join([str(d.marca),str(d.modelo),str(d.capacidad)])).upper() or 'OPPO' in str(d.marca).upper()]
for d in found:
 print(f'id={d.pk} | {d.marca} {d.modelo} {d.capacidad} | categoria={d.categoria!r} | activo={d.activo} | visible={visible(d)}')
print('\n=== MARCAS Y VISIBILIDAD ===')
for brand in sorted({str(d.marca) for d in all_devices}):
 ds=[d for d in all_devices if str(d.marca)==brand]
 print(f'{brand}: total={len(ds)} visibles={sum(visible(d) for d in ds)} ocultos={sum(not visible(d) for d in ds)}')
print('\n=== DISPOSITIVOS NO VISIBLES ===')
for d in all_devices:
 if not visible(d):print(f'id={d.pk} {d.marca} {d.modelo} {d.capacidad} | categoria={d.categoria!r} activo={d.activo}')
print('\n=== COBERTURA PRECIOS POR DISPOSITIVO ===')
fields=[f.name for f in PrecioRenove._meta.fields]
print('Campos PrecioRenove:',fields)
fk=next((f for f in PrecioRenove._meta.fields if f.is_relation and f.related_model==Dispositivo),None)
if fk:
 rows=PrecioRenove.objects.values(fk.attname,'meses').annotate(n=Count('pk'))
 count=defaultdict(lambda:defaultdict(int))
 for r in rows:count[r[fk.attname]][r['meses']]+=r['n']
 for d in all_devices:
  c=count[d.pk]
  if not c or not visible(d):
   print(f'id={d.pk} {d.marca} {d.modelo} {d.capacidad} | 24={c.get(24,0)} 48={c.get(48,0)} visible={visible(d)}')
 print('Con precios 24:',sum(count[d.pk].get(24,0)>0 for d in all_devices))
 print('Con precios 48:',sum(count[d.pk].get(48,0)>0 for d in all_devices))
else:print('No se detecto FK directa; no se modifica nada')
print('\n=== POSIBLES ARCHIVOS ORIGEN EN PROYECTO ===')
for p in sorted(root.glob('**/*')):
 if p.is_file() and p.suffix.lower() in ('.xlsx','.xls','.csv') and not any(x in p.parts for x in ('venv','.venv','site-packages','node_modules')):
  print(str(p.relative_to(root)),p.stat().st_size,'bytes')
print('\nFIN SOLO LECTURA.')
