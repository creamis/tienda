#!/usr/bin/env python3
"""Valida importes y claves iPhone de Renove. SOLO LECTURA. No importa precios."""
import ast,base64,zlib,json,re,unicodedata,os,sys
from decimal import Decimal,InvalidOperation
from collections import defaultdict,Counter
from pathlib import Path
root=Path('/home/tienda/tienda');os.chdir(root);sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo,PrecioRenove,PromocionRenove,CorrespondenciaTarifaRenove
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or ''))
 return re.sub('[^A-Z0-9]','', ''.join(c for c in s if not unicodedata.combining(c)).upper())
def decimal(v):
 if v is None or str(v).strip()=='':return None
 try:return Decimal(str(v).replace(',','.'))
 except (ValueError,InvalidOperation):return None
tree=ast.parse((root/'importar_precios_renove_nov26.py').read_text(encoding='utf-8'))
payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
rows=json.loads(zlib.decompress(base64.b85decode(payload)))
devices={norm(' '.join([d.marca,d.modelo,d.capacidad])):d for d in Dispositivo.objects.filter(marca__iexact='Apple',modelo__icontains='iphone')}
promos={norm(p.nombre):p for p in PromocionRenove.objects.all()}
mapping=defaultdict(set)
for c in CorrespondenciaTarifaRenove.objects.select_related('columna_precio'):
 mapping[(c.promocion_id,norm(c.columna_precio.nombre))].add(c.columna_precio_id)
count=Counter();seen={};examples=defaultdict(list);promo_counts=Counter()
for promo,name,tar,initial,quota,unico in rows:
 if 'IPHONE' not in norm(name):continue
 d=devices.get(norm('APPLE '+name));p=promos.get(norm(promo))
 if not d or not p:count['sin_dispositivo_promocion']+=1;continue
 ids=mapping.get((p.id,norm(tar)),set())
 if len(ids)!=1:count['columna_no_resuelta']+=1;continue
 key=(d.id,p.id,next(iter(ids)),24)
 vals=[decimal(x) for x in (initial,quota,unico)]
 if vals[0] is None or vals[1] is None or vals[0]<0 or vals[1]<0:
  count['importe_invalido']+=1
  if len(examples['importe_invalido'])<5:examples['importe_invalido'].append([name,promo,tar,str(initial),str(quota)])
  continue
 if vals[2] is not None and vals[2]<0:
  count['pago_unico_negativo']+=1;continue
 if key in seen:
  count['clave_repetida']+=1
  if seen[key]!=vals:count['conflicto_importe_fuente']+=1
  continue
 seen[key]=vals
 if PrecioRenove.objects.filter(dispositivo_id=d.id,promocion_id=p.id,tarifa_id=key[2],meses=24).exists():
  count['clave_existente']+=1;continue
 count['nuevo_valido']+=1;promo_counts[p.nombre]+=1
print('=== VALIDACION FINAL IPHONE: SOLO LECTURA ===')
print('Resumen:',json.dumps(count,ensure_ascii=False,indent=2))
print('Nuevos validos por promocion:',json.dumps(promo_counts,ensure_ascii=False,indent=2))
print('Ejemplos:',json.dumps(examples,ensure_ascii=False,indent=2))
print('NO se ha modificado ningun dato.')
