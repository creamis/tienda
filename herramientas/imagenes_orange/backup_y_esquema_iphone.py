#!/usr/bin/env python3
"""Copia de seguridad consistente de SQLite + esquema PrecioRenove. No modifica registros."""
import os,sys,sqlite3,datetime,json
from pathlib import Path
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root));os.chdir(root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from django.db import connection
from crm.models import PrecioRenove
db=connection.settings_dict
print('Motor:',db['ENGINE'])
print('Campos PrecioRenove:')
for f in PrecioRenove._meta.concrete_fields:
 print(' -',f.name,'|',f.get_internal_type(),'| null:',f.null,'| default:',str(f.default)[:60])
if 'sqlite3' not in db['ENGINE']:
 print('No se genera copia automatica: motor no SQLite. Detener aqui.')
 sys.exit(1)
source=Path(db['NAME']).resolve()
if not source.is_file():sys.exit('Base de datos no encontrada')
dest=root/'copias_seguridad';dest.mkdir(exist_ok=True)
name=dest/('crm_antes_iphone_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.sqlite3')
with sqlite3.connect(str(source)) as src,sqlite3.connect(str(name)) as dst:
 src.backup(dst)
 check=dst.execute('PRAGMA integrity_check').fetchone()[0]
if check!='ok':
 name.unlink(missing_ok=True)
 sys.exit('ERROR: copia no valida')
print('Copia verificada:',name,'bytes:',name.stat().st_size)
print('Precios existentes:',PrecioRenove.objects.count())
print('NO se han modificado los datos del CRM.')
