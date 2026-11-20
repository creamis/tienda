#!/usr/bin/env python3
"""Corrige exportacion de relaciones PrecioRenove; SOLO LECTURA."""
import os,sys,csv
from pathlib import Path
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo,PrecioRenove
p=root/'auditoria_renove_noviembre_2026_corregida.csv'
cols=['TIPO','id','marca','modelo','capacidad','categoria','activo','promocion_id','tarifa_id','dispositivo_id','meses','pago_unico','pago_inicial','cuota_mensual','precio_activo']
with p.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols,delimiter=';')
 w.writeheader()
 for d in Dispositivo.objects.all().order_by('id'):
  w.writerow({'TIPO':'DISPOSITIVO','id':d.pk,'marca':d.marca,'modelo':d.modelo,'capacidad':d.capacidad,'categoria':d.categoria,'activo':d.activo})
 for x in PrecioRenove.objects.all().order_by('id'):
  w.writerow({'TIPO':'PRECIO','id':x.pk,'promocion_id':x.promocion_id,'tarifa_id':x.tarifa_id,'dispositivo_id':x.dispositivo_id,'meses':x.meses,'pago_unico':x.pago_unico,'pago_inicial':x.pago_inicial,'cuota_mensual':x.cuota_mensual,'precio_activo':x.activo})
print('EXPORTACION CORREGIDA, SOLO LECTURA')
print('Archivo:',p)
print('Dispositivos:',Dispositivo.objects.count(),'Precios:',PrecioRenove.objects.count())
print('Adjunta el CSV corregido a ChatGPT.')
