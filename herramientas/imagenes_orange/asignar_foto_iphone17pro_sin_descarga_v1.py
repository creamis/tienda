#!/usr/bin/env python3
"""Asigna URL de imagen Apple iPhone 17 Pro sin descargarla desde PythonAnywhere.
El navegador prueba la URL y muestra el icono existente si falla.
"""
import os,sys,sqlite3
from pathlib import Path
from datetime import datetime
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from django.conf import settings
from django.db import transaction
from crm.models import Dispositivo
url='https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-17-pro-finish-select-cosmicorange-202509?wid=600&hei=600&fmt=png-alpha'
targets=[]
for d in Dispositivo.objects.all():
 name=' '.join((d.marca,d.modelo,d.capacidad)).upper()
 if d.marca.upper()=='APPLE' and 'IPHONE 17 PRO' in name and 'PRO MAX' not in name:
  targets.append(d)
print('Modelos:',[(d.pk,str(d)) for d in targets])
if len(targets)!=2 or set(d.pk for d in targets)!={44,45}:sys.exit('ABORTADO: no coinciden los dos iPhone 17 Pro esperados')
if any(d.imagen_url and d.imagen_url!=url for d in targets):sys.exit('ABORTADO: hay fotografias diferentes asignadas')
if settings.DATABASES['default']['ENGINE']!='django.db.backends.sqlite3':sys.exit('ABORTADO: BD no SQLite')
db=Path(settings.DATABASES['default']['NAME'])
backup=db.with_name(db.name+'.bak_foto_apple_url_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
src=sqlite3.connect(f'file:{db}?mode=ro',uri=True);dst=sqlite3.connect(str(backup))
try:src.backup(dst)
finally:src.close();dst.close()
with transaction.atomic():
 n=Dispositivo.objects.filter(pk__in=[44,45],imagen_url='').update(imagen_url=url)
print('CORRECTO: URL de Apple asignada a',n,'dispositivos.')
print('No se ha comprobado que el navegador pueda cargarla. Si falla, se muestra el icono habitual.')
print('BACKUP:',backup)
print('Sin cambios en precios, accesorios o plantilla.')
