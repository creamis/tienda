#!/usr/bin/env python3
"""Auditoria de promociones y tarifas Renove: exportacion SOLO LECTURA."""
import os,sys,csv
from pathlib import Path
from collections import Counter
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import PrecioRenove
out=root/'auditoria_promociones_tarifas_nov26.csv'
promo_field=PrecioRenove._meta.get_field('promocion')
tarifa_field=PrecioRenove._meta.get_field('tarifa')
def label(o):
 if o is None:return ''
 parts=[]
 for f in o._meta.fields:
  if f.is_relation:continue
  v=getattr(o,f.name,None)
  if v is not None:parts.append(f'{f.name}={str(v)[:180]}')
 return ' | '.join(parts)
rows=[]
for kind,f in [('PROMOCION',promo_field),('TARIFA',tarifa_field)]:
 model=f.related_model
 counts=Counter(PrecioRenove.objects.values_list(f.attname,flat=True))
 for o in model.objects.all().order_by('pk'):
  rows.append([kind,o.pk,str(o),label(o),counts.get(o.pk,0)])
 for missing,n in counts.items():
  if missing is None:rows.append([kind,'','SIN ASIGNAR','',n])
with out.open('w',encoding='utf-8-sig',newline='') as fh:
 w=csv.writer(fh,delimiter=';')
 w.writerow(['tipo','id','nombre','campos','registros_precios'])
 w.writerows(rows)
print('EXPORTACION SOLO LECTURA CORRECTA')
print('Archivo:',out)
for r in rows:print(' | '.join(map(str,r)))
print('No se ha modificado la base de datos.')
