#!/usr/bin/env python3
"""Diagnostico no destructivo para preparar financiación 24/48 de accesorios Renove."""
import json,os,re,sys
from pathlib import Path
root=Path('/home/tienda/tienda')
tpl=root/'crm/templates/crm/renove_particular.html'
if not tpl.exists():raise SystemExit('No se encuentra plantilla Renove')
html=tpl.read_text(encoding='utf8')
m=re.search(r'<script id="renove-segunda-venta" type="application/json">(.*?)</script>',html,re.S)
if not m:raise SystemExit('No se encuentra catalogo de segunda venta')
items=json.loads(m.group(1))
print('=== CATALOGO ACTUAL DE ACCESORIOS ===')
print('Referencias:',len(items))
print('Tipos:',{t:sum(a.get('tipo')==t for a in items) for t in sorted(set(a.get('tipo') for a in items))})
print('Con plazo explicito:',sum('meses' in a for a in items))
print('Con cuota 48:',sum('cuota_48' in a for a in items))
for name in ('APPLE AIRPODS PRO 3','AURICULARES HONOR CHOICE S10','HONOR BAND 10'):
 print(name,':',next((a for a in items if a.get('nombre')==name),'NO ENCONTRADO'))
print('=== ESTADO DEL CALCULO ===')
print('24 meses fijo:',"3 dispositivos · 24 meses" in html)
print('Suma cuotas accesorios:',"l.extras.reduce((n,a)=>n+a.cuota,0)" in html)
print('=== COPIAS EXISTENTES ===')
print('Copias de plantilla:',sum(1 for p in (root/'crm').glob('copias_*/**/renove_particular.html')))
print('FIN: NO SE HAN MODIFICADO ARCHIVOS')
