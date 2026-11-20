#!/usr/bin/env python3
"""Auditoría de tarifas Renove, solo lectura; no modifica la BD."""
import os,sys,json,re,unicodedata
from collections import defaultdict,Counter
os.environ.setdefault("DJANGO_SETTINGS_MODULE","orange_project.settings")
import django;django.setup()
from crm.models import TarifaRenove,TarifaComercialRenove,CorrespondenciaTarifaRenove,PromocionRenove,PrecioRenove
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or ''))
 return re.sub('[^A-Z0-9]','', ''.join(c for c in s if not unicodedata.combining(c)).upper())
by=defaultdict(list)
for t in TarifaRenove.objects.all():by[norm(t.nombre)].append(t)
print("=== TARIFAS CON NOMBRE NORMALIZADO DUPLICADO ===")
for key,group in by.items():
 if len(group)>1:
  print(json.dumps({"ids":[t.id for t in group],"nombres":[t.nombre for t in group],"activa":[t.activa for t in group],"precios":[PrecioRenove.objects.filter(tarifa=t).count() for t in group]},ensure_ascii=False))
print("=== MAPEO ACTUAL COMERCIAL -> COLUMNA, POR PROMOCION ===")
for c in CorrespondenciaTarifaRenove.objects.select_related('tarifa_comercial','promocion','columna_precio').order_by('promocion__nombre','tarifa_comercial__nombre'):
 print(json.dumps({"comercial_id":c.tarifa_comercial_id,"comercial":c.tarifa_comercial.nombre,"promocion":c.promocion.nombre,"columna_id":c.columna_precio_id,"columna":c.columna_precio.nombre,"precios_en_columna_promocion":PrecioRenove.objects.filter(tarifa_id=c.columna_precio_id,promocion_id=c.promocion_id,activo=True).count()},ensure_ascii=False))
print("=== TARIFAS COMERCIALES SIN CORRESPONDENCIA EN ALGUNA PROMOCION ACTIVA ===")
cs=list(TarifaComercialRenove.objects.filter(activa=True))
ps=list(PromocionRenove.objects.filter(activa=True))
exists=set(CorrespondenciaTarifaRenove.objects.values_list('tarifa_comercial_id','promocion_id'))
for t in cs:
 missing=[p.nombre for p in ps if (t.id,p.id) not in exists]
 if missing:print(json.dumps({"id":t.id,"nombre":t.nombre,"sin_correspondencia":missing},ensure_ascii=False))
print("FIN. SOLO LECTURA.")
