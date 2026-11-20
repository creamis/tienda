#!/usr/bin/env python3
"""Extrae exclusivamente la lógica actual de Renove Particular, sin cambios."""
from pathlib import Path
root=Path('/home/tienda/tienda')
targets=[
 (root/'crm/views.py',95,137),
 (root/'crm/templates/crm/renove_particular.html',1,150),
 (root/'crm/models.py',65,100),
 (root/'crm/models.py',130,170),
]
for p,start,end in targets:
 print('\n'+'='*20+' '+str(p.relative_to(root))+' '+str(start)+'-'+str(end)+' '+'='*20)
 if not p.exists():
  print('NO EXISTE');continue
 lines=p.read_text(encoding='utf-8').splitlines()
 for i in range(start-1,min(end,len(lines))):print(f'{i+1:04d}: {lines[i]}')
print('\nFIN. SOLO LECTURA.')
