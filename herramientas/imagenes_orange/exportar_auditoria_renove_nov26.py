#!/usr/bin/env python3
"""Exporta inventario Renove para compararlo con Excel oficial. SOLO LECTURA."""
import os,sys,csv
from pathlib import Path
from datetime import datetime
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo,PrecioRenove
out=root/'auditoria_renove_noviembre_2026.csv'
def fields(obj):
 return {f.name:getattr(obj,f.attname) for f in obj._meta.fields}
with out.open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,delimiter=';')
 w.writerow(['TIPO','id','marca','modelo','capacidad','categoria','activo','promocion_id','tarifa_id','dispositivo_id','meses','pago_unico','pago_inicial','cuota_mensual'])
 for d in Dispositivo.objects.order_by('id'):
  x=fields(d)
  w.writerow(['DISPOSITIVO',x.get('id'),x.get('marca'),x.get('modelo'),x.get('capacidad'),x.get('categoria'),x.get('activo'),'','','','','','',''])
 for p in PrecioRenove.objects.order_by('id'):
  x=fields(p)
  w.writerow(['PRECIO',x.get('id'),'','','','','',x.get('promocion_id'),x.get('tarifa_id'),x.get('dispositivo_id'),x.get('meses'),x.get('pago_unico'),x.get('pago_inicial'),x.get('cuota_mensual')])
print('EXPORTACION SOLO LECTURA TERMINADA')
print('Archivo:',out)
print('Dispositivos:',Dispositivo.objects.count())
print('Precios:',PrecioRenove.objects.count())
print('Adjunta este CSV a ChatGPT para cruzarlo con el Excel oficial.')
