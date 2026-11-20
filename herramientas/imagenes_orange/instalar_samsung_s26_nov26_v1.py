#!/usr/bin/env python3
"""Instala cuotas Samsung S26 y S26+ noviembre 2026; valida antes de escribir y respalda SQLite."""
import os,sys,sqlite3
from pathlib import Path
from datetime import datetime
from decimal import Decimal
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from django.conf import settings
from django.db import transaction
from crm.models import Dispositivo,PrecioRenove
tarifas=[24,25,5,6,3,20,21,22,9,26,27,28,29,14,30,31]
promos=[1,2,4,5]
# Excel oficial: hoja VaP renove (NUEVAS TARIFAS).
# Filas base 487-494, otras promociones 1199-1206, 1912-1919, 2625-2632.
precios={85:('36.50','18.25'),86:('46.00','23.00'),87:('52.00','26.00'),88:('61.00','30.50')}
if settings.DATABASES['default']['ENGINE']!='django.db.backends.sqlite3':sys.exit('ABORTADO: se requiere SQLite para copia de seguridad')
if len(tarifas)!=len(set(tarifas)) or len(promos)!=len(set(promos)):sys.exit('ABORTADO: IDs repetidos')
Promo=PrecioRenove._meta.get_field('promocion').remote_field.model
Tarifa=PrecioRenove._meta.get_field('tarifa').remote_field.model
if set(Promo.objects.filter(pk__in=promos).values_list('pk',flat=True))!=set(promos):sys.exit('ABORTADO: falta una promocion')
if set(Tarifa.objects.filter(pk__in=tarifas).values_list('pk',flat=True))!=set(tarifas):sys.exit('ABORTADO: falta una tarifa')
for pk in precios:
 try:d=Dispositivo.objects.get(pk=pk)
 except Dispositivo.DoesNotExist:sys.exit(f'ABORTADO: dispositivo {pk} no existe')
 model=d.modelo.upper()
 if d.marca.upper()!='SAMSUNG' or 'S26' not in model or d.categoria!='Smartphone' or not d.activo:
  sys.exit(f'ABORTADO: dispositivo {pk} no coincide: {d.marca} {d.modelo}')
 if pk in (85,86) and ('S26+' in model or 'ULTRA' in model or 'FE' in model):sys.exit(f'ABORTADO: variante incorrecta {pk}')
 if pk in (87,88) and 'S26+' not in model:sys.exit(f'ABORTADO: variante incorrecta {pk}')
 if ('256' if pk in (85,87) else '512') not in str(d.capacidad):sys.exit(f'ABORTADO: capacidad incorrecta {pk}')
 if PrecioRenove.objects.filter(dispositivo_id=pk).exists():sys.exit(f'ABORTADO: {pk} ya tiene precios, no se sobrescribe')
# La estructura de PrecioRenove se verifica ANTES del backup.
fieldnames={f.name for f in PrecioRenove._meta.fields}
if not {'dispositivo','promocion','tarifa','meses','pago_inicial','cuota_mensual','activo'}.issubset(fieldnames):
 sys.exit('ABORTADO: estructura PrecioRenove inesperada')
dbpath=Path(settings.DATABASES['default']['NAME'])
if not dbpath.is_file():sys.exit('ABORTADO: no se encuentra SQLite')
backup=dbpath.with_name(dbpath.name+'.bak_s26_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
src=sqlite3.connect(f'file:{dbpath}?mode=ro',uri=True);dst=sqlite3.connect(str(backup))
try:src.backup(dst)
finally:src.close();dst.close()
with transaction.atomic():
 for device,(p24,p48) in precios.items():
  for promo in promos:
   for tarifa in tarifas:
    for meses,cuota in ((24,p24),(48,p48)):
     PrecioRenove.objects.create(dispositivo_id=device,promocion_id=promo,tarifa_id=tarifa,meses=meses,pago_inicial=Decimal('0'),cuota_mensual=Decimal(cuota),activo=True)
print('CORRECTO: 512 precios de cuatro Samsung S26 incorporados (4 dispositivos x 4 promociones x 16 tarifas x 2 plazos).')
print('Backup:',backup)
print('Otros dispositivos y precios anteriores: sin modificaciones.')
