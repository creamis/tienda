#!/usr/bin/env python3
"""Importación CONTROLADA de 968 precios iPhone. Por defecto solo simula.
Uso: python importar_iphone_968.py
     python importar_iphone_968.py --aplicar
Requiere copia de seguridad previa. Nunca actualiza registros existentes.
"""
import ast,base64,zlib,json,re,unicodedata,os,sys
from collections import defaultdict,Counter
from decimal import Decimal,InvalidOperation
from pathlib import Path
from django.db import transaction
root=Path('/home/tienda/tienda');os.chdir(root);sys.path.insert(0,str(root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo,PrecioRenove,PromocionRenove,CorrespondenciaTarifaRenove
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or ''))
 return re.sub('[^A-Z0-9]','', ''.join(c for c in s if not unicodedata.combining(c)).upper())
def dec(v):
 if v is None or str(v).strip()=='':return None
 try:return Decimal(str(v).replace(',','.'))
 except (ValueError,InvalidOperation):return None
def main():
 apply='--aplicar' in sys.argv
 if len(sys.argv)>2 or (len(sys.argv)==2 and not apply):sys.exit('Uso: python importar_iphone_968.py [--aplicar]')
 source=root/'importar_precios_renove_nov26.py'
 if not source.exists():sys.exit('Falta fuente: '+str(source))
 tree=ast.parse(source.read_text(encoding='utf-8'))
 payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
 rows=json.loads(zlib.decompress(base64.b85decode(payload)))
 devices=defaultdict(list)
 for d in Dispositivo.objects.filter(marca__iexact='Apple',modelo__icontains='iphone'):
  devices[norm(' '.join([d.marca,d.modelo,d.capacidad]))].append(d)
 promos=defaultdict(list)
 for p in PromocionRenove.objects.all():promos[norm(p.nombre)].append(p)
 mapping=defaultdict(set)
 for c in CorrespondenciaTarifaRenove.objects.select_related('columna_precio'):
  mapping[(c.promocion_id,norm(c.columna_precio.nombre))].add(c.columna_precio_id)
 expected={'MAX DTO':242,'MEJOR CON DTO':242,'MEJOR PRECIO':242,'RENOVE':242}
 candidates={};counts=Counter();promo_counts=Counter();source_count=0
 for promo,name,tar,initial,quota,unico in rows:
  if 'IPHONE' not in norm(name):continue
  source_count+=1
  ds=devices.get(norm('APPLE '+name),[])
  ps=promos.get(norm(promo),[])
  if len(ds)!=1 or len(ps)!=1:sys.exit('ABORTADO: dispositivo o promocion ambiguos: '+repr((promo,name)))
  d,p=ds[0],ps[0]
  ids=mapping.get((p.id,norm(tar)),set())
  if len(ids)==0:counts['sin_correspondencia']+=1;continue
  if len(ids)!=1:sys.exit('ABORTADO: columna ambigua: '+repr((promo,tar,ids)))
  values=(dec(initial),dec(quota),dec(unico))
  if values[0] is None or values[1] is None or values[0]<0 or values[1]<0 or (values[2] is not None and values[2]<0):
   sys.exit('ABORTADO: importes invalidos: '+repr((promo,name,tar,values)))
  key=(d.id,p.id,next(iter(ids)),24)
  if key in candidates:sys.exit('ABORTADO: clave fuente repetida: '+repr(key))
  candidates[key]=values
  promo_counts[p.nombre]+=1
 if source_count!=1408 or counts['sin_correspondencia']!=440 or len(candidates)!=968 or dict(promo_counts)!=expected:
  sys.exit('ABORTADO: lote diferente al validado: '+repr((source_count,counts,len(candidates),promo_counts)))
 backups=sorted((root/'copias_seguridad').glob('crm_antes_iphone_*.sqlite3'))
 if apply and not backups:sys.exit('ABORTADO: no existe copia de seguridad')
 print('Filas iPhone:',source_count,'| Fuera del mapeo:',counts['sin_correspondencia'],'| Candidatas:',len(candidates))
 print('Por promocion:',dict(promo_counts))
 print('Backup:',backups[-1] if backups else 'NO ENCONTRADO')
 with transaction.atomic():
  # Revisión de existencia dentro de la misma transacción.
  all_existing=set(PrecioRenove.objects.filter(dispositivo_id__in={k[0] for k in candidates},promocion_id__in={k[1] for k in candidates},meses=24).values_list('dispositivo_id','promocion_id','tarifa_id','meses'))
  clashes=all_existing.intersection(candidates)
  if clashes:sys.exit('ABORTADO: existen ya '+str(len(clashes))+' precios del lote')
  before=PrecioRenove.objects.count()
  if apply:
   objects=[PrecioRenove(dispositivo_id=d,promocion_id=p,tarifa_id=t,meses=24,pago_inicial=v[0],cuota_mensual=v[1],pago_unico=v[2],activo=True) for (d,p,t,m),v in candidates.items()]
   PrecioRenove.objects.bulk_create(objects,batch_size=200)
   after=PrecioRenove.objects.count()
   if after-before!=968:raise RuntimeError('Cantidad inesperada, transaccion revertida')
   print('IMPORTACION REAL COMPLETADA:',after-before,'| total:',after)
  else:
   print('SIMULACION CORRECTA. Antes:',before,'| despues previsto:',before+968)
   print('Para aplicar: python importar_iphone_968.py --aplicar')
if __name__=='__main__':main()
