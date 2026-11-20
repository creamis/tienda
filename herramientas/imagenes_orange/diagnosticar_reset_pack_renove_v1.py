#!/usr/bin/env python3
"""Diagnostico de cambio de smartphone Renove; solo lectura, no datos personales."""
from pathlib import Path
p=Path('/home/tienda/tienda/crm/templates/crm/renove_particular.html')
if not p.exists():raise SystemExit('NO EXISTE LA PLANTILLA')
s=p.read_text(encoding='utf-8')
for marker in ['RENOVE_PACK_MARCA_V1','RENOVE_PLAZOS_AUTO_V1','accesoriosElegidosManualmente','plazosElegidosManualmente','sincronizarPlazosRenove(l)']:
 print(marker,':',s.count(marker))
for needle in ['l.plazos[k]=24;','sincronizarPlazosRenove(l);\n pintar()','l.accesoriosElegidosManualmente']:
 print('\n--- CONTEXTO',needle,'---')
 pos=0
 for i in range(min(s.count(needle),4)):
  j=s.find(needle,pos)
  if j<0:break
  print('APARICION',i+1,'POSICION',j)
  print(s[max(0,j-650):min(len(s),j+400)])
  pos=j+len(needle)
print('\nDIAGNOSTICO COMPLETADO SIN CAMBIOS')
