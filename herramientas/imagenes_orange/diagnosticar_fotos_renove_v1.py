#!/usr/bin/env python3
"""Inventario seguro de fotos Renove, sin modificar archivos ni base de datos."""
import os,sys,json
from pathlib import Path
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo
p=root/'crm/templates/crm/renove_particular.html'
s=p.read_text(encoding='utf-8')
for term in ['function fotoRenove','fotoRenove(','renove-foto-mini','renove-foto','imagen','foto']:
 print('\n===',term,'ocurrencias:',s.count(term),'===')
 pos=0
 for i in range(min(3,s.count(term))):
  j=s.find(term,pos);print(s[max(0,j-150):min(len(s),j+900)].replace('\n',' '));pos=j+len(term)
print('\n=== CAMPOS DISPOSITIVO ===')
print([(f.name,f.get_internal_type()) for f in Dispositivo._meta.fields])
print('\n=== MUESTRA FOTOS (sin datos de clientes) ===')
for d in Dispositivo.objects.order_by('pk')[:12]:
 print(d.pk,repr(str(d)),[(f.name,str(getattr(d,f.name,''))[:150]) for f in Dispositivo._meta.fields if any(x in f.name.lower() for x in ['imagen','foto','url'])])
print('\n=== ARCHIVOS DE IMAGEN EXISTENTES ===')
for base in [root/'crm/static',root/'static',root/'media']:
 if base.exists():
  paths=[str(x.relative_to(root)) for x in base.rglob('*') if x.is_file() and x.suffix.lower() in ('.jpg','.jpeg','.png','.webp')]
  print(base,'total:',len(paths),'muestra:',paths[:35])
print('\nFIN: solo lectura')
