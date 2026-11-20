#!/usr/bin/env python3
"""Auditoria de imagenes Renove, solo lectura. Usa campos reales del modelo."""
import os,sys,json,re
from pathlib import Path
from collections import Counter
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo
qs=Dispositivo.objects.all()
total=qs.count()
with_url=qs.exclude(imagen_url__isnull=True).exclude(imagen_url='').count()
print('=== FOTOS DE SMARTPHONES ===')
print('Dispositivos:',total,'con imagen_url:',with_url,'sin imagen_url:',total-with_url)
for key in ['HONOR 600 LITE','IPHONE 16','SAMSUNG GALAXY']:
 matches=[]
 for d in qs:
  name=' '.join(str(getattr(d,k,'') or '') for k in ('marca','modelo','capacidad'))
  if key.casefold() in name.casefold():
   matches.append((d.pk,name,str(d.imagen_url or '')[:160]))
 print(key,'coincidencias:',len(matches))
 for x in matches[:6]:print(' ',x)
p=root/'crm/templates/crm/renove_particular.html'
s=p.read_text(encoding='utf-8')
m=re.search(r'<script id="renove-segunda-venta" type="application/json">(.*?)</script>',s,re.S)
if m:
 a=json.loads(m.group(1))
 print('=== FOTOS DE ACCESORIOS ===')
 print('Accesorios:',len(a),'con imagen_url:',sum(bool(x.get('imagen_url')) for x in a))
 for name in ['APPLE AIRPODS PRO 3','AURICULARES HONOR CHOICE S10','HONOR BAND 10']:
  print(name,next(((x.get('imagen_url') or '(sin imagen)') for x in a if x.get('nombre')==name),'no encontrado'))
print('=== PLANTILLA ===')
print('Función fotoRenove:', 'fotoRenove' in s)
print('FIN: SOLO LECTURA; NO SE MODIFICÓ NADA')
