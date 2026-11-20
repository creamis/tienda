#!/usr/bin/env python3
"""Comprobación posterior a importación: iPhones y acceso a precios por tarifa. Solo lectura."""
import os,sys,json
from collections import Counter
from pathlib import Path
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root));os.chdir(root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo,PrecioRenove,PromocionRenove,TarifaComercialRenove,CorrespondenciaTarifaRenove
print('=== COMPROBACION POSTIMPORTACION IPHONE ===')
print('Total precios:',PrecioRenove.objects.count())
iphone=list(Dispositivo.objects.filter(marca__iexact='Apple',modelo__icontains='iphone'))
ids=[d.id for d in iphone]
prices=PrecioRenove.objects.filter(dispositivo_id__in=ids,meses=24,activo=True)
print('Modelos iPhone:',len(iphone),'| precios activos iPhone:',prices.count())
print('Promociones:',dict(Counter(prices.values_list('promocion__nombre',flat=True))))
print('=== PRUEBA DE RUTA COMERCIAL ===')
promos=list(PromocionRenove.objects.filter(activa=True).order_by('nombre'))
comerciales=list(TarifaComercialRenove.objects.filter(activa=True).order_by('nombre'))
mapping={(c.tarifa_comercial_id,c.promocion_id):c.columna_precio_id for c in CorrespondenciaTarifaRenove.objects.all()}
missing=[];found=0;examples=[]
for d in iphone:
 for p in promos:
  for t in comerciales:
   col=mapping.get((t.id,p.id))
   if col is None:continue
   result=PrecioRenove.objects.filter(dispositivo_id=d.id,promocion_id=p.id,tarifa_id=col,meses=24,activo=True)
   if result.exists():
    found+=1
    if len(examples)<8:
     x=result.first()
     examples.append({'modelo':d.modelo,'capacidad':d.capacidad,'promocion':p.nombre,'tarifa':t.nombre,'cuota':str(x.cuota_mensual),'inicial':str(x.pago_inicial)})
   else:missing.append((d.modelo,p.nombre,t.nombre))
print('Combinaciones iPhone/promocion/tarifa comercial con precio:',found)
print('Combinaciones sin precio:',len(missing))
print('Ejemplos:',json.dumps(examples,ensure_ascii=False,indent=2))
print('Primeras ausencias:',json.dumps(missing[:12],ensure_ascii=False))
print('FIN: SIN MODIFICACIONES')
