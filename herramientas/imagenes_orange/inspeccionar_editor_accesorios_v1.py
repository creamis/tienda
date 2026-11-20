#!/usr/bin/env python3
"""Última inspección del selector manual de accesorios; solo lectura."""
from pathlib import Path
s=Path('/home/tienda/tienda/crm/templates/crm/renove_particular.html').read_text()
for key in ("if(l.manual)", "if (l.manual)", "l.extras[", ".extras.splice(", "selector.onchange", "select.onchange", "onchange=()=>"):
 print("\n###",key,"TOTAL",s.count(key))
 start=0
 for _ in range(min(8,s.count(key))):
  pos=s.find(key,start)
  print(s[max(0,pos-220):pos+420].replace("\n"," "))
  start=pos+len(key)
