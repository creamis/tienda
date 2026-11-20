#!/usr/bin/env python3
"""Diagnóstico seguro de marcas y selección automática Renove. SOLO LECTURA."""
from pathlib import Path
import re,json,collections,os,sys
root=Path('/home/tienda/tienda')
p=root/'crm/templates/crm/renove_particular.html'
if not p.exists():sys.exit('ERROR: plantilla no encontrada')
s=p.read_text(encoding='utf-8')
m=re.search(r'<script id="renove-segunda-venta" type="application/json">(.*?)</script>',s,re.S)
if not m:sys.exit('ERROR: catálogo de accesorios no encontrado')
items=json.loads(m.group(1))
print('=== ACCESORIOS ACTUALES ===',len(items))
for kind in ('auriculares','reloj'):
 group=sorted((a for a in items if a.get('tipo')==kind),key=lambda a:(float(a.get('cuota') or 0)*24+float(a.get('inicial') or 0),a.get('nombre','')))
 print('\nCATEGORIA:',kind,'total:',len(group))
 for a in group[:12]:print(' ',a.get('nombre'), '24m:',a.get('cuota'),'48m:',a.get('cuota_48','-'))
 print('MARCAS POTENCIALES:')
 for brand in ('APPLE','SAMSUNG','HONOR','HUAWEI','XIAOMI','REDMI','OPPO','MOTOROLA','TCL','JBL'):
  matches=[a for a in group if brand in a.get('nombre','').upper()]
  if matches:
   cheapest=min(matches,key=lambda a:(float(a.get('cuota') or 0)*24+float(a.get('inicial') or 0),a.get('nombre','')))
   print(' ',brand,':',len(matches),'mas barato:',cheapest.get('nombre'),'cuota:',cheapest.get('cuota'))
print('\n=== LOGICA ACTUAL ===')
for needle in ('function extras(', 'function lineaNueva(', 'function pintar(', 'manual:', 'l.manual', 'Cambiar accesorios'):
 pos=s.find(needle)
 print('\n',needle,'ENCONTRADO' if pos>=0 else 'NO ENCONTRADO')
 if pos>=0:print(repr(s[max(0,pos-100):pos+650]))
print('\n=== MODELO DE DISPOSITIVOS ===')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
try:
 import django
 django.setup()
 from crm.models import Dispositivo
 counts=collections.Counter((d.marca or '').strip() for d in Dispositivo.objects.all())
 for marca,n in counts.most_common():print(' ',repr(marca),n)
except Exception as exc:print('ERROR consulta marcas:',type(exc).__name__,str(exc))
print('\nFIN SOLO LECTURA. NINGUN ARCHIVO O PRECIO MODIFICADO.')
