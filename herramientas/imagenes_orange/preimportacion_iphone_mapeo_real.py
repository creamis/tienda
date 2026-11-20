#!/usr/bin/env python3
"""SIMULACION SOLO LECTURA: mapea iPhone a columnas YA USADAS por correspondencias."""
import ast,base64,zlib,json,re,unicodedata,os,sys
from collections import defaultdict,Counter
from decimal import Decimal
from pathlib import Path
root=Path('/home/tienda/tienda');sys.path.insert(0,str(root));os.chdir(root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo,PrecioRenove,PromocionRenove,CorrespondenciaTarifaRenove
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or ''))
 return re.sub(r'[^A-Z0-9]','', ''.join(c for c in s if not unicodedata.combining(c)).upper())
p=root/'importar_precios_renove_nov26.py'
tree=ast.parse(p.read_text(encoding='utf8'))
payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
rows=json.loads(zlib.decompress(base64.b85decode(payload)))
iphone={norm(' '.join([d.marca,d.modelo,d.capacidad])):d for d in Dispositivo.objects.filter(marca__iexact='Apple',modelo__icontains='iphone')}
promos={norm(x.nombre):x for x in PromocionRenove.objects.all()}
mapping=defaultdict(set)
for c in CorrespondenciaTarifaRenove.objects.select_related('columna_precio'):
 mapping[(c.promocion_id,norm(c.columna_precio.nombre))].add(c.columna_precio_id)
counts=Counter();errors=defaultdict(list);unique={}
for promo,name,tar,initial,quota,unico in rows:
 if 'IPHONE' not in norm(name):continue
 d=iphone.get(norm('APPLE '+name));pr=promos.get(norm(promo))
 if not d or not pr:counts['sin_dispositivo_o_promocion']+=1;continue
 ids=mapping.get((pr.id,norm(tar)),set())
 if len(ids)!=1:
  counts['columna_no_resuelta']+=1
  if len(errors['columna_no_resuelta'])<12:errors['columna_no_resuelta'].append([promo,tar,list(ids)])
  continue
 key=(d.id,pr.id,next(iter(ids)),24)
 try:values=(Decimal(str(initial)),Decimal(str(quota)),Decimal(str(unico)) if unico is not None else None)
 except Exception:
  counts['importe_invalido']+=1;continue
 if key in unique and unique[key]!=values:
  counts['conflicto_fuente']+=1
  if len(errors['conflicto_fuente'])<12:errors['conflicto_fuente'].append([key,str(values),str(unique[key])])
 else:unique[key]=values
for (device,promo,tar,months),values in unique.items():
 existing=list(PrecioRenove.objects.filter(dispositivo_id=device,promocion_id=promo,tarifa_id=tar,meses=months))
 if len(existing)>1:counts['duplicado_bd']+=1
 elif len(existing)==1:
  e=existing[0]
  if e.cuota_mensual==values[1] and e.pago_inicial==values[0]:counts['ya_existente_igual']+=1
  else:counts['conflicto_bd']+=1
 else:counts['nuevo_sin_sobrescritura']+=1
print('=== PREIMPORTACION IPHONE CON CORRESPONDENCIAS REALES: SOLO LECTURA ===')
print('Total filas fuente iPhone:',sum(1 for r in rows if 'IPHONE' in norm(r[1])))
print('Claves unicas resueltas:',len(unique))
print('Conteos:',json.dumps(counts,ensure_ascii=False,indent=2))
print('Ejemplos de incidencias:',json.dumps(errors,ensure_ascii=False,indent=2,default=str))
print('NO se ha importado ni modificado nada.')
