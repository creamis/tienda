#!/usr/bin/env python3
"""Auditoría Renove de solo lectura. Ejecutar: python manage.py shell < herramientas/imagenes_orange/auditar_renove.py"""
import json
from collections import Counter, defaultdict
from django.apps import apps
from django.db.models import Count

def model(name):
    found=[m for m in apps.get_models() if m.__name__==name]
    return found[0] if len(found)==1 else None
def fields(m):
    return {f.name for f in m._meta.fields}
def output(label, data):
    print("\n### "+label)
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
def sample(m, keys, n=3):
    f=fields(m);return list(m.objects.values(*[k for k in keys if k in f])[:n])
names=["Dispositivo","PrecioRenove","PromocionRenove","TarifaRenove","CorrespondenciaRenove"]
models={name:model(name) for name in names}
output("MODELOS", {name:{"existe":bool(m),"total":m.objects.count() if m else None,"campos":sorted(fields(m)) if m else []} for name,m in models.items()})
for name,m in models.items():
    if m:output("MUESTRA "+name, sample(m,["id","nombre","marca","modelo","capacidad","categoria","meses","cuota_mensual","pago_inicial","activo","activa","tarifa_comercial_id","columna_precio_id","promocion_id","tarifa_id","dispositivo_id"],4))
p=models["PrecioRenove"]
if p:
    f=fields(p)
    if "meses" in f:output("PRECIOS POR PLAZO",list(p.objects.values("meses").annotate(total=Count("id")).order_by("meses")))
    if "dispositivo" in f and "meses" in f:
        groups=defaultdict(set)
        for id,months in p.objects.values_list("dispositivo_id","meses").distinct().iterator():
            groups[id].add(months)
        output("COBERTURA DISPOSITIVOS",dict(Counter(",".join(map(str,sorted(v))) for v in groups.values())))
    d=models["Dispositivo"]
    if d and "dispositivo" in f:
        iphone_ids=list(d.objects.filter(modelo__icontains="iphone").values_list("id",flat=True))
        if iphone_ids:
            q=p.objects.filter(dispositivo_id__in=iphone_ids)
            output("IPHONE: PRECIOS",{"dispositivos":len(iphone_ids),"filas":q.count(),"por_plazo":list(q.values("meses").annotate(total=Count("id"))) if "meses" in f else []})
            output("IPHONE: MUESTRA PRECIOS",sample(q.model,[],0) if False else list(q.values(*[k for k in ["dispositivo_id","promocion_id","tarifa_id","meses","cuota_mensual","activo"] if k in f])[:12]))
c=models["CorrespondenciaRenove"]
if c:
    output("CORRESPONDENCIAS: TOTAL",c.objects.count())
    f=fields(c)
    if "promocion" in f:output("CORRESPONDENCIAS POR PROMOCION",list(c.objects.values("promocion_id").annotate(total=Count("id"))[:100]))
print("\nAUDITORIA SOLO LECTURA COMPLETADA. No se ha modificado la base de datos.")
