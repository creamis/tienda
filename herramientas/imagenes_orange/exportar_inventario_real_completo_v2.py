#!/usr/bin/env python3
"""Exporta el inventario real Renove (120 dispositivos y accesorios) sin modificar nada."""
import os,sys,re,json,csv
from pathlib import Path
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo
out=root/'herramientas/imagenes_orange/resultado_fotos'
out.mkdir(exist_ok=True)
rows=[]
for d in Dispositivo.objects.all().order_by('marca','modelo','capacidad'):
 rows.append({'tipo':'dispositivo','id':str(d.pk),'nombre':' '.join(str(getattr(d,k,'') or '') for k in ('marca','modelo','capacidad')).strip(),'marca':str(d.marca or ''),'categoria':str(d.categoria or ''),'imagen_actual':str(d.imagen_url or '')})
n_devices=len(rows)
p=root/'crm/templates/crm/renove_particular.html'
s=p.read_text(encoding='utf-8')
start_tag='<script id="renove-segunda-venta" type="application/json">'
start=s.find(start_tag)
if start<0:sys.exit('ERROR: bloque de accesorios no encontrado; sin modificar nada')
start+=len(start_tag)
end=s.find('</script>',start)
if end<0:sys.exit('ERROR: cierre del bloque de accesorios no encontrado; sin modificar nada')
accessories=json.loads(s[start:end])
for i,x in enumerate(accessories):
 rows.append({'tipo':'accesorio','id':str(i),'nombre':str(x.get('nombre','')),'marca':str(x.get('marca','')),'categoria':str(x.get('tipo','')),'imagen_actual':str(x.get('imagen_url') or '')})
path=out/'inventario_real_completo.csv'
with path.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['tipo','id','nombre','marca','categoria','imagen_actual']);w.writeheader();w.writerows(rows)
print('DISPOSITIVOS:',n_devices,'ACCESORIOS:',len(accessories),'TOTAL:',len(rows))
print('CON FOTO:',sum(bool(x['imagen_actual']) for x in rows))
print('INVENTARIO:',path)
print('SOLO LECTURA. Sin cambios en CRM, precios o promociones.')
