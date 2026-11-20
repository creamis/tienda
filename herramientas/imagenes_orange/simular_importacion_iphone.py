#!/usr/bin/env python3
"""Renove: simulacion de importacion iPhone, SIN ESCRITURAS."""
import ast,base64,zlib,json,re,unicodedata,os,sys
from collections import defaultdict,Counter
from decimal import Decimal,InvalidOperation
from pathlib import Path
ROOT=Path('/home/tienda/tienda')
sys.path.insert(0,str(ROOT));os.chdir(ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo,PrecioRenove,PromocionRenove,TarifaRenove,TarifaComercialRenove,CorrespondenciaTarifaRenove
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or ''))
 return re.sub(r'[^A-Z0-9]','', ''.join(c for c in s if not unicodedata.combining(c)).upper())
def money(v):
 try:return Decimal(str(v))
 except (InvalidOperation,ValueError):return None
source=ROOT/'importar_precios_renove_nov26.py'
if not source.exists():sys.exit('FALTA importar_precios_renove_nov26.py')
tree=ast.parse(source.read_text(encoding='utf-8'))
payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
rows=json.loads(zlib.decompress(base64.b85decode(payload)))
iphone=[r for r in rows if 'IPHONE' in norm(r[1])]
devices=defaultdict(list)
for d in Dispositivo.objects.filter(marca__iexact='Apple',modelo__icontains='iphone'):
 devices[norm(' '.join((d.marca,d.modelo,d.capacidad)))].append(d)
promos={norm(p.nombre):p for p in PromocionRenove.objects.all()}
tarifas=defaultdict(list)
for t in TarifaRenove.objects.all():tarifas[norm(t.nombre)].append(t)
comerciales=list(TarifaComercialRenove.objects.all())
corres={(c.tarifa_comercial_id,c.promocion_id):c for c in CorrespondenciaTarifaRenove.objects.select_related('columna_precio')}
pending=defaultdict(list);problems=Counter();details=defaultdict(list)
for row in iphone:
 promo,name,tar,initial,quota,unico=row
 found=devices.get(norm('APPLE '+name),[])
 if len(found)!=1:problems['dispositivo_sin_coincidencia_o_ambiguo']+=1;continue
 d=found[0];p=promos.get(norm(promo))
 if not p:problems['promocion_no_existe']+=1;continue
 vals=(money(initial),money(quota),money(unico))
 if vals[0] is None or vals[1] is None or vals[0]<0 or vals[1]<0:
  problems['precio_no_valido']+=1;continue
 key=(d.id,p.id,norm(tar))
 pending[key].append((d,p,tar,vals))
for key,items in pending.items():
 distinct={(x[3][0],x[3][1],x[3][2]) for x in items}
 if len(distinct)>1:problems['precios_distintos_misma_clave']+=1;details['conflictos'].append((key,len(distinct)))
 else:
  d,p,tar,vals=items[0]
  ts=tarifas.get(norm(tar),[])
  if len(ts)==0:problems['tarifa_precio_a_crear']+=1
  if len(ts)>1:problems['tarifa_precio_ambigua']+=1
  if len(ts)==1:
   existing=list(PrecioRenove.objects.filter(dispositivo=d,promocion=p,tarifa=ts[0],meses=24))
   if len(existing)>1:problems['duplicados_en_bd']+=1
   elif len(existing)==1:
    old=existing[0]
    if old.cuota_mensual!=vals[1] or old.pago_inicial!=vals[0]:problems['conflicto_con_precio_bd']+=1
    else:problems['precio_ya_igual']+=1
   else:problems['precio_nuevo_tarifa_existente']+=1
  segments=[norm(x) for x in re.split(r'\s*/+\s*',tar)]
  matched=[tc for tc in comerciales if norm(tc.nombre) in segments]
  if not matched:problems['sin_tarifa_comercial_equivalente']+=1;details['sin_comercial'].append((d.modelo,tar,p.nombre))
  for tc in matched:
   c=corres.get((tc.id,p.id))
   if c is None:problems['correspondencia_a_crear']+=1
   elif norm(c.columna_precio.nombre)!=norm(tar):problems['correspondencia_apunta_otra_columna']+=1;details['mapeos_conflictivos'].append((tc.nombre,p.nombre,c.columna_precio.nombre,tar))
print('=== SIMULACION IPHONE, SOLO LECTURA ===')
print('Filas fuente:',len(iphone),'| combinaciones unicas:',len(pending))
print('Incidencias y estado:',json.dumps(problems,ensure_ascii=False,indent=2))
for k in ['conflictos','sin_comercial','mapeos_conflictivos']:
 print(k,'total',len(details[k]),'ejemplos:',details[k][:8])
print('Precios a 48 meses en fuente:',0,'(este importador solo contiene 24 meses)')
print('CONCLUSION: esta simulacion NO autoriza importar automaticamente.')
print('FIN. No se ha modificado ningun dato.')
