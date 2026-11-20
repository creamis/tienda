#!/usr/bin/env python3
"""Inspección final de los eventos de selección, solo lectura."""
from pathlib import Path
p=Path('/home/tienda/tienda/crm/templates/crm/renove_particular.html')
s=p.read_text(encoding='utf-8')
for needle in ('ds.onchange','ds.addEventListener','l.dispositivo=','extras()','l.extras=','l.extras =','l.manual=','l.manual =','function extras('):
 print('\n###',needle,'ocurrencias:',s.count(needle))
 start=0
 for n in range(min(s.count(needle),5)):
  i=s.find(needle,start)
  print(s[max(0,i-180):i+500].replace('\n',' '))
  start=i+len(needle)
print('\nFIN SOLO LECTURA')
