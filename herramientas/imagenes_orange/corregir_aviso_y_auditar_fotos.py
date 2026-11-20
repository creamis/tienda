#!/usr/bin/env python3
"""Corrige aviso Renove y audita fotos sin alterar calculos ni cuotas."""
from pathlib import Path
from datetime import datetime
import json,re,shutil,sys
root=Path('/home/tienda/tienda')
p=root/'crm/templates/crm/renove_particular.html'
if not p.exists():sys.exit('ERROR: plantilla no encontrada')
s=p.read_text(encoding='utf-8')
old='La financiación a 48 meses solo se ofrece en accesorios con precio publicado.'
new='La financiación a 48 meses se ofrece para smartphones y accesorios cuando existe un precio publicado para ese dispositivo y plazo.'
if old not in s:
 print('AVISO: texto exacto anterior no encontrado; no se modifica la plantilla.')
 for line in s.splitlines():
  if '48 meses solo' in line or 'La propuesta muestra' in line:print('Texto actual:',line[:700])
else:
 if s.count(old)!=1:sys.exit('ERROR: aviso duplicado, no se modifica')
 backup=p.with_name(p.name+'.bak_aviso_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 shutil.copy2(p,backup)
 p.write_text(s.replace(old,new),encoding='utf-8')
 print('AVISO CORREGIDO; backup:',backup)
print('=== AUDITORIA FOTOGRAFIAS ===')
try:
 import django
 sys.path.insert(0,str(root));import os
 os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
 django.setup()
 from crm.models import Dispositivo
 fields=[f.name for f in Dispositivo._meta.fields]
 print('Campos dispositivo:',fields)
 for name in ['HONOR 600 LITE','IPHONE 16','AIRPODS']:
  qs=Dispositivo.objects.filter(nombre__icontains=name)[:3]
  for d in qs:
   print('DISPOSITIVO',d.pk,repr(d.nombre),'imagen_url=',repr(getattr(d,'imagen_url',None)))
except Exception as e:print('No se pudo inspeccionar modelos:',type(e).__name__,str(e))
print('FIN: sin cambios de precios ni cálculos')
