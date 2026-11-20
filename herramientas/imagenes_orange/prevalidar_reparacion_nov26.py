#!/usr/bin/env python3
"""Reconciliacion Renove noviembre: previsualizacion sin escrituras."""
import os,sys,csv
from pathlib import Path
from collections import Counter,defaultdict
root=Path('/home/tienda/tienda')
sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django
django.setup()
from crm.models import Dispositivo,PrecioRenove
from django.db.models import Count
print('=== PREVALIDACION DE CAMBIOS ===')
d=Dispositivo.objects.filter(marca__iexact='OPPO',modelo__icontains='A6x',capacidad__icontains='256').first()
if d:
 print('OPPO:',d.pk,d.marca,d.modelo,d.capacidad,'activo=',d.activo)
 for p in PrecioRenove.objects.filter(dispositivo=d).select_related('promocion','tarifa').order_by('promocion_id','meses','tarifa_id'):
  print('PRECIO',p.pk,'promo',p.promocion.nombre,'tarifa',str(p.tarifa),'meses',p.meses,'cuota',p.cuota_mensual,'activo',p.activo)
else:print('OPPO no encontrado')
print('\n=== SAMSUNG SIN PRECIOS ===')
for d in Dispositivo.objects.filter(marca__iexact='Samsung',modelo__icontains='S26').order_by('id'):
 print(d.pk,d.modelo,d.capacidad,'precios',PrecioRenove.objects.filter(dispositivo=d).count())
print('\n=== TARIFAS Y PROMOCIONES CON PRECIOS ===')
for p in PrecioRenove.objects.values('promocion__nombre','tarifa__nombre','meses','activo').annotate(n=Count('pk')).order_by('promocion__nombre','tarifa__nombre','meses','activo'):
 print(p)
print('\nSIN MODIFICACIONES')
