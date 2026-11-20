#!/usr/bin/env python3
"""Importador seguro de URLs de imagen verificadas para Renove Particular.
Lee un CSV de id,imagen_url; no cambia precios ni otras columnas.
"""
import os,sys,csv,sqlite3
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from django.conf import settings
from django.db import transaction
from crm.models import Dispositivo
manifest=root/'fotos_renove_verificadas.csv'
if not manifest.is_file():sys.exit('SIN CAMBIOS: falta fotos_renove_verificadas.csv con columnas id,imagen_url')
with manifest.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f)
 if not {'id','imagen_url'}.issubset(reader.fieldnames or []):sys.exit('ABORTADO: encabezados requeridos id,imagen_url')
 rows=list(reader)
if not rows:sys.exit('SIN CAMBIOS: manifiesto vacio')
ids=set();changes=[]
for r in rows:
 try:pk=int(r['id'])
 except:sys.exit('ABORTADO: ID invalido')
 if pk in ids:sys.exit('ABORTADO: ID duplicado')
 ids.add(pk)
 url=r['imagen_url'].strip()
 parsed=urlparse(url)
 if parsed.scheme!='https' or not parsed.netloc or parsed.username or parsed.password or len(url)>500:sys.exit('ABORTADO: URL no valida para ID '+str(pk))
 try:d=Dispositivo.objects.get(pk=pk)
 except Dispositivo.DoesNotExist:sys.exit('ABORTADO: dispositivo inexistente '+str(pk))
 if d.imagen_url and d.imagen_url!=url:sys.exit('ABORTADO: imagen previa diferente en ID '+str(pk))
 if d.imagen_url!=url:changes.append((pk,url))
if not changes:sys.exit('YA INSTALADAS: no hay cambios')
if settings.DATABASES['default']['ENGINE']!='django.db.backends.sqlite3':sys.exit('ABORTADO: base de datos no SQLite')
db=Path(settings.DATABASES['default']['NAME'])
backup=db.with_name(db.name+'.bak_fotos_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
src=sqlite3.connect(f'file:{db}?mode=ro',uri=True);dst=sqlite3.connect(str(backup))
try:src.backup(dst)
finally:src.close();dst.close()
with transaction.atomic():
 for pk,url in changes:Dispositivo.objects.filter(pk=pk).update(imagen_url=url)
print('CORRECTO: URLs de fotos instaladas:',len(changes))
print('BACKUP:',backup)
print('Precios, accesorios y plantilla: sin cambios.')
