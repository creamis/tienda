#!/usr/bin/env python3
"""Solo lectura: diagnostica coincidencias iPhone entre importador y BD."""
import ast,base64,zlib,json,re,unicodedata,os,sys
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path('/home/tienda/tienda');sys.path.insert(0,str(ROOT));os.chdir(ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','orange_project.settings')
import django;django.setup()
from crm.models import Dispositivo,PrecioRenove,CorrespondenciaTarifaRenove,PromocionRenove
def norm(s):
 s=unicodedata.normalize('NFKD',str(s or ''))
 return re.sub('[^A-Z0-9]','', ''.join(c for c in s if not unicodedata.combining(c)).upper())
source=Path('/home/tienda/tienda/importar_precios_renove_nov26.py')
if not source.exists():sys.exit('FALTA importar_precios_renove_nov26.py')
tree=ast.parse(source.read_text(encoding='utf-8'))
payload=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAYLOAD' for t in n.targets))
rows=json.loads(zlib.decompress(base64.b85decode(payload)))
byname=defaultdict(list)
for d in Dispositivo.objects.filter(categoria__iexact='Smartphone'):
 byname[norm(' '.join([d.marca,d.modelo,d.capacidad]))].append(d)
iphone=[r for r in rows if 'IPHONE' in norm(r[1])]
results=defaultdict(list);unmatched=Counter();ambiguous=Counter()
for promo,name,tar,initial,quota,unico in iphone:
 key=norm('APPLE '+name) if norm(name).startswith('IPHONE') else norm(name)
 found=byname.get(key,[])
 if len(found)==1:results[found[0].id].append((promo,tar,quota))
 elif len(found)>1:ambiguous[name]+=1
 else:unmatched[name]+=1
print('=== AUDITORIA IPHONE V2 SOLO LECTURA ===')
print('Filas fuente:',len(iphone),'modelos coincidentes:',len(results),'filas coincidentes:',sum(map(len,results.values())))
print('Sin coincidencia:',dict(unmatched),'ambiguos:',dict(ambiguous))
for d in Dispositivo.objects.filter(marca__iexact='Apple',modelo__icontains='iphone').order_by('modelo','capacidad'):
 vals=results.get(d.id,[])
 print('ID=%s %s %s | filas=%s | promociones=%s | precios_BD=%s'%(d.id,d.modelo,d.capacidad,len(vals),sorted(set(x[0] for x in vals)),PrecioRenove.objects.filter(dispositivo=d).count()))
print('CORRESPONDENCIAS:',CorrespondenciaTarifaRenove.objects.count())
print('PROMOCIONES:',list(PromocionRenove.objects.values_list('id','nombre')))
print('PLAZOS BD:',dict(Counter(PrecioRenove.objects.values_list('meses',flat=True))))
print('FIN. Ningun dato modificado. No ejecutar --aplicar.')
