#!/usr/bin/env python3
"""Reactivar exclusivamente OPPO A6x 256 GB tras verificar cobertura 48m. Backup SQLite."""
import os,sys,sqlite3,shutil
from pathlib import Path
from datetime import datetime
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from django.conf import settings
from django.db import transaction
from crm.models import Dispositivo,PrecioRenove
qs=Dispositivo.objects.filter(marca__iexact='OPPO',modelo__iexact='A6x',capacidad__icontains='256')
if qs.count()!=1:sys.exit(f'ABORTADO: encontrados {qs.count()} OPPO A6x 256 GB, se esperaba 1')
d=qs.get()
if d.pk!=29 or d.categoria!='Smartphone':sys.exit('ABORTADO: identidad/categoria inesperada')
prices=PrecioRenove.objects.filter(dispositivo=d,meses=48,activo=True)
promos=set(prices.values_list('promocion__nombre',flat=True))
expected={'MAX DTO','MEJOR CON DTO','MEJOR PRECIO','RENOVE'}
if promos!=expected or prices.count()!=64:sys.exit(f'ABORTADO: cobertura distinta a auditoria: {len(prices)} precios, promociones {promos}')
if PrecioRenove.objects.filter(dispositivo=d,meses=24,activo=True).exists():sys.exit('ABORTADO: existen 24 meses activos no auditados')
if d.activo:
 print('YA ESTABA ACTIVO. Sin cambios.')
 sys.exit(0)
db=settings.DATABASES['default']
if db['ENGINE']!='django.db.backends.sqlite3':sys.exit('ABORTADO: backup automatico solo compatible con SQLite')
dbpath=Path(db['NAME'])
if not dbpath.is_file():sys.exit('ABORTADO: no se encuentra SQLite')
backup=dbpath.with_name(dbpath.name+'.bak_oppo_a6x_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
src=sqlite3.connect(f'file:{dbpath}?mode=ro',uri=True)
dst=sqlite3.connect(str(backup))
try:src.backup(dst)
finally:dst.close();src.close()
with transaction.atomic():
 d.activo=True
 d.save(update_fields=['activo'])
print('OPPO A6x 256 GB ACTIVADO. ID:',d.pk)
print('BACKUP:',backup)
print('Precios 48 meses conservados:',prices.count())
print('Precios 24 meses NO alterados. Otros dispositivos NO alterados.')
