#!/usr/bin/env python3
"""Diagnostico de acceso comercial iPhone: sin filtros prematuros, solo lectura."""
import os,sys,json
from collections import Counter
from pathlib import Path
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root));os.chdir(root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo,PrecioRenove,PromocionRenove,TarifaComercialRenove,CorrespondenciaTarifaRenove
devices=list(Dispositivo.objects.filter(marca__iexact='Apple',modelo__icontains='iphone'))
promos=list(PromocionRenove.objects.all())
tarifas=list(TarifaComercialRenove.objects.all())
corr=list(CorrespondenciaTarifaRenove.objects.all())
print('=== DIAGNOSTICO REAL DE FILTROS ===')
for title,items in [('Promociones',promos),('Tarifas comerciales',tarifas)]:
 print(title,'total',len(items),'activas',sum(bool(x.activa) for x in items))
 print('Muestra:',json.dumps([{'id':x.id,'nombre':x.nombre,'activa':x.activa} for x in items[:30]],ensure_ascii=False))
print('Correspondencias totales:',len(corr))
byid={(c.tarifa_comercial_id,c.promocion_id):c.columna_precio_id for c in corr}
found=0;missing=0;examples=[];missing_examples=[];mapped=0
for d in devices:
 for p in promos:
  for t in tarifas:
   col=byid.get((t.id,p.id))
   if col is None:continue
   mapped+=1
   x=PrecioRenove.objects.filter(dispositivo_id=d.id,promocion_id=p.id,tarifa_id=col,meses=24,activo=True).first()
   if x:
    found+=1
    if len(examples)<10:examples.append({'modelo':d.modelo,'capacidad':d.capacidad,'promocion':p.nombre,'tarifa_comercial':t.nombre,'cuota':str(x.cuota_mensual),'inicial':str(x.pago_inicial)})
   else:
    missing+=1
    if len(missing_examples)<8:missing_examples.append([d.modelo,p.nombre,t.nombre])
print('Combinaciones con correspondencia:',mapped,'con precio:',found,'sin precio:',missing)
print('Ejemplos con precio:',json.dumps(examples,ensure_ascii=False,indent=2))
print('Ejemplos sin precio:',json.dumps(missing_examples,ensure_ascii=False))
print('FIN: SOLO LECTURA')
