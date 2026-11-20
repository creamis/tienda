#!/usr/bin/env python3
"""Diagnostico de la pantalla Renove, solo lectura."""
import os,sys,re
from pathlib import Path
root=Path('/home/tienda/tienda');os.chdir(root);sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from django.urls import get_resolver
print('=== ARCHIVOS RENOVE ===')
for p in sorted(root.rglob('*renove*')):
 if p.is_file() and p.suffix in ('.py','.html','.js'):
  print(p.relative_to(root))
print('=== FILTROS Y PRECIO EN CODIGO RENOVE ===')
terms=('TarifaComercialRenove','precioPrincipal','precio_principal','PrecioRenove','tarifas_comerciales','tarifas_renove')
for folder in ('crm','templates'):
 base=root/folder
 if not base.exists():continue
 for p in base.rglob('*'):
  if not p.is_file() or p.suffix not in ('.py','.html','.js'):continue
  try:lines=p.read_text(encoding='utf8').splitlines()
  except Exception:continue
  hits=[i for i,s in enumerate(lines) if any(t in s for t in terms)]
  if hits:
   print('\nARCHIVO',p.relative_to(root),'lineas relevantes',len(hits))
   for i in hits[:20]:
    print(str(i+1)+':',lines[i][:260])
print('=== FIN SOLO LECTURA ===')
