#!/usr/bin/env python3
"""Añade SOLO los 64 precios OPPO A6x 256 GB a 24 meses del Excel noviembre 2026."""
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
Promocion=PrecioRenove._meta.get_field('promocion').remote_field.model
Tarifa=PrecioRenove._meta.get_field('tarifa').remote_field.model
# Fuente: VaP renove (NUEVAS TARIFAS), filas 406,1118,1831,2544;
# cuotas CON IVA columnas F,H,J,L,N,P,R,T,V,X,Z,AB,AD,AF,AH,AJ.
tarifas=[24,25,5,6,3,20,21,22,9,26,27,28,29,14,30,31]
matriz={
 2:['3.25','3.25','3.25','3.25','3.25','3.25','2','2','2.25','2.25','2.25','2','2','3.25','2.25','2'],
 1:['5.75','5.75','5.75','5.75','5.75','5.75','4.5','4.5','4.75','4.75','4.75','4.5','4.5','5.75','4.75','4.5'],
 5:['6.75','6.75','6.75','6.75','6.75','6.75','5.5','5.5','5.75','5.75','5.75','5.5','5.5','6.75','5.75','5.5'],
 4:['9.5']*16,
}
qs=Dispositivo.objects.filter(pk=29,marca__iexact='OPPO',modelo__iexact='A6x',capacidad__icontains='256',categoria='Smartphone',activo=True)
if qs.count()!=1:sys.exit('ABORTADO: OPPO A6x 256 GB no coincide con la auditoria')
d=qs.get()
if set(Promocion.objects.filter(pk__in=matriz).values_list('pk',flat=True))!=set(matriz):sys.exit('ABORTADO: promociones no coinciden')
if Tarifa.objects.filter(pk__in=tarifas).count()!=16:sys.exit('ABORTADO: faltan tarifas')
if any(len(v)!=16 for v in matriz.values()):sys.exit('ABORTADO: matriz incompleta')
for promo,values in matriz.items():
 for tarifa,cuota in zip(tarifas,values):
  if PrecioRenove.objects.filter(dispositivo=d,promocion_id=promo,tarifa_id=tarifa,meses=24).exists():
   sys.exit(f'ABORTADO: precio 24 meses preexistente en promo {promo} tarifa {tarifa}')
  if PrecioRenove.objects.filter(dispositivo=d,promocion_id=promo,tarifa_id=tarifa,meses=48,activo=True).count()!=1:
   sys.exit(f'ABORTADO: falta precio 48 meses de referencia promo {promo} tarifa {tarifa}')
if settings.DATABASES['default']['ENGINE']!='django.db.backends.sqlite3':sys.exit('ABORTADO: base no SQLite')
path=Path(settings.DATABASES['default']['NAME'])
backup=path.with_name(path.name+'.bak_oppo24_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
source=sqlite3.connect(f'file:{path}?mode=ro',uri=True);dest=sqlite3.connect(str(backup))
try:source.backup(dest)
finally:source.close();dest.close()
with transaction.atomic():
 for promo,values in matriz.items():
  for tarifa,cuota in zip(tarifas,values):
   PrecioRenove.objects.create(dispositivo=d,promocion_id=promo,tarifa_id=tarifa,meses=24,pago_inicial=Decimal('0'),cuota_mensual=Decimal(cuota),activo=True)
print('CORRECTO: 64 precios oficiales OPPO A6x 256 GB a 24 meses instalados.')
print('Backup:',backup)
print('MAX DTO + GO FLEX: 3.25 EUR/mes solo smartphone.')
print('Sin cambios en otros dispositivos, precios existentes ni accesorios.')
