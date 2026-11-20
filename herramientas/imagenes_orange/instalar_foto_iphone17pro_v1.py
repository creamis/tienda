#!/usr/bin/env python3
"""Renove: instala imagen Apple iPhone 17 Pro tras validar descarga real.
No toca precios, accesorios, ni plantilla. No asigna Pro Max ni modelos diferentes.
"""
import os,sys,sqlite3,urllib.request
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
matches=[]
for d in Dispositivo.objects.all():
 name=' '.join((d.marca,d.modelo,d.capacidad)).upper().replace('-',' ')
 if 'IPHONE 17 PRO' in name and 'PRO MAX' not in name and 'IPHONE 17 PRO ' in name:
  matches.append(d)
print('Coincidencias iPhone 17 Pro:',[(d.pk,str(d)) for d in matches])
if not matches:sys.exit('SIN CAMBIOS: no se ha localizado iPhone 17 Pro')
if any(d.imagen_url and d.imagen_url!=url for d in matches):sys.exit('SIN CAMBIOS: hay imagenes existentes que requieren revision')
try:
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.apple.com/'})
 with urllib.request.urlopen(req,timeout=20) as response:
  mime=response.headers.get('Content-Type','').lower();data=response.read(1_500_001)
 if not mime.startswith('image/') or len(data)<3000 or len(data)>1_500_000:raise ValueError('respuesta no es imagen valida o tamano inusual: '+mime)
 if not (data.startswith(b'\x89PNG') or data.startswith(b'\xff\xd8') or data.startswith(b'RIFF')):raise ValueError('formato de imagen inesperado')
except Exception as e:sys.exit('SIN CAMBIOS: no se pudo validar la imagen oficial: '+str(e))
if settings.DATABASES['default']['ENGINE']!='django.db.backends.sqlite3':sys.exit('SIN CAMBIOS: DB no SQLite')
db=Path(settings.DATABASES['default']['NAME'])
backup=db.with_name(db.name+'.bak_iphone17pro_foto_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
src=sqlite3.connect(f'file:{db}?mode=ro',uri=True);dst=sqlite3.connect(str(backup))
try:src.backup(dst)
finally:src.close();dst.close()
with transaction.atomic():
 n=Dispositivo.objects.filter(pk__in=[d.pk for d in matches],imagen_url='').update(imagen_url=url)
print('CORRECTO: imagen oficial Apple verificada, asignada a',n,'variantes iPhone 17 Pro')
print('BACKUP:',backup)
print('Sin cambios en otros dispositivos, precios o accesorios.')
