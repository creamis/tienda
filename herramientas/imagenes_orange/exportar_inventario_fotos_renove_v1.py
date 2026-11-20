#!/usr/bin/env python3
"""Exporta inventario visual completo Renove sin modificar la base de datos."""
import os,sys,csv,json,re
from pathlib import Path
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo
p=root/'crm/templates/crm/renove_particular.html'
html=p.read_text(encoding='utf-8')
out=root/'inventario_fotos_renove.csv'
rows=[]
for d in Dispositivo.objects.order_by('marca','modelo','capacidad'):
 rows.append({'tipo':'dispositivo','id':d.pk,'marca':d.marca,'modelo':d.modelo,'capacidad':d.capacidad,'categoria':d.categoria,'nombre':str(d),'imagen_url':d.imagen_url or '','activo':int(d.activo)})
m=re.search(r'<script[^>]*id=["\']renove-segunda-venta["\'][^>]*>(.*?)</script>',html,re.S|re.I)
if m:
 try:
  data=json.loads(m.group(1))
  for i,a in enumerate(data):
   rows.append({'tipo':'accesorio','id':i,'marca':'','modelo':'','capacidad':'','categoria':a.get('tipo',''),'nombre':a.get('nombre',''),'imagen_url':a.get('imagen_url',''),'activo':1})
 except Exception as e:print('AVISO: no se pudo leer JSON de accesorios:',str(e)[:200])
else:print('AVISO: JSON de accesorios no localizado')
with out.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['tipo','id','marca','modelo','capacidad','categoria','nombre','imagen_url','activo']);w.writeheader();w.writerows(rows)
print('INVENTARIO GENERADO:',out)
print('Dispositivos:',sum(r['tipo']=='dispositivo' for r in rows),'con imagen:',sum(r['tipo']=='dispositivo' and bool(r['imagen_url']) for r in rows))
print('Accesorios:',sum(r['tipo']=='accesorio' for r in rows),'con imagen:',sum(r['tipo']=='accesorio' and bool(r['imagen_url']) for r in rows))
print('Sin cambios en precios, base de datos ni plantilla.')
