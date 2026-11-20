#!/usr/bin/env python3
"""Renove: sincroniza automáticamente financiación de accesorios con smartphone."""
from pathlib import Path
from datetime import datetime
import shutil,sys
p=Path('/home/tienda/tienda/crm/templates/crm/renove_particular.html')
if not p.is_file():sys.exit('ERROR: plantilla no encontrada')
s=p.read_text(encoding='utf-8')
marker='/* RENOVE_PLAZOS_AUTO_V1 */'
if marker in s:sys.exit('YA INSTALADO. Sin cambios.')
required='/* RENOVE_PACK_MARCA_V1 */'
if required not in s:sys.exit('ABORTADO: falta la version de packs por marca.')
old1="plazos:[24,24],mesesPrincipal:24,manual:false,accesoriosElegidosManualmente:[false,false]"
new1="plazos:[24,24],mesesPrincipal:24,manual:false,accesoriosElegidosManualmente:[false,false],plazosElegidosManualmente:[false,false]"
old2="s.onchange=()=>{l.extras[k]=accesorios[Number(s.value)];l.plazos[k]=24;if(!Array.isArray(l.accesoriosElegidosManualmente))l.accesoriosElegidosManualmente=[false,false];l.accesoriosElegidosManualmente[k]=true;pintar()};"
new2="s.onchange=()=>{l.extras[k]=accesorios[Number(s.value)];if(!Array.isArray(l.accesoriosElegidosManualmente))l.accesoriosElegidosManualmente=[false,false];l.accesoriosElegidosManualmente[k]=true;if(!Array.isArray(l.plazosElegidosManualmente))l.plazosElegidosManualmente=[false,false];l.plazosElegidosManualmente[k]=false;sincronizarPlazosRenove(l);pintar()};"
old3="plazo.onchange=()=>{l.plazos[k]=Number(plazo.value);pintar()};"
new3="plazo.onchange=()=>{l.plazos[k]=Number(plazo.value);if(!Array.isArray(l.plazosElegidosManualmente))l.plazosElegidosManualmente=[false,false];l.plazosElegidosManualmente[k]=true;pintar()};"
old4="selectorPlazoMovil.onchange=()=>{l.mesesPrincipal=Number(selectorPlazoMovil.value);pintar()};"
new4="selectorPlazoMovil.onchange=()=>{l.mesesPrincipal=Number(selectorPlazoMovil.value);sincronizarPlazosRenove(l);pintar()};"
old5="l.plazos[k]=24;\n  }\n });\n pintar()"
new5="l.plazos[k]=24;\n  }\n });\n sincronizarPlazosRenove(l);\n pintar()"
old6="if(!disponible48&&l.mesesPrincipal===48)l.mesesPrincipal=24;"
new6="if(!disponible48&&l.mesesPrincipal===48){l.mesesPrincipal=24;sincronizarPlazosRenove(l);}"
helper="""/* RENOVE_PLAZOS_AUTO_V1 */
function sincronizarPlazosRenove(l){
 if(!Array.isArray(l.plazosElegidosManualmente))l.plazosElegidosManualmente=[false,false];
 if(!Array.isArray(l.plazos))l.plazos=[24,24];
 (l.extras||[]).forEach((a,k)=>{
  if(l.plazosElegidosManualmente[k])return;
  const precio48=a&&a.cuota_48;
  const disponible48=typeof precio48==='number'&&Number.isFinite(precio48)&&precio48>=0;
  l.plazos[k]=Number(l.mesesPrincipal)===48&&disponible48?48:24;
 });
}
"""
changes=[(old1,new1,'estado inicial'),(old2,new2,'sustitucion accesorio'),(old3,new3,'plazo manual'),(old4,new4,'plazo smartphone'),(old5,new5,'cambio smartphone'),(old6,new6,'48 no disponible')]
for a,b,label in changes:
 n=s.count(a)
 if n!=1:sys.exit(f'ABORTADO SIN CAMBIOS: {label}, coincidencias {n} (se esperaba 1)')
s=s.replace('function extras(marca){',helper+'\nfunction extras(marca){',1)
for a,b,_ in changes:s=s.replace(a,b,1)
if s.count(marker)!=1:sys.exit('ABORTADO: marcador duplicado')
if s.count('l.manual=!l.manual;pintar()')!=1:sys.exit('ABORTADO: editor inesperado')
if s.count("const largo=(l.mesesPrincipal===48)||l.plazos.some(n=>n===48)")!=1:sys.exit('ABORTADO: calculo inesperado')
backup=p.with_name(p.name+'.bak_plazos_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
shutil.copy2(p,backup)
tmp=p.with_name(p.name+'.tmp_plazos')
try:
 tmp.write_text(s,encoding='utf-8')
 tmp.replace(p)
except Exception:
 if tmp.exists():tmp.unlink()
 shutil.copy2(backup,p)
 raise
print('INSTALADO RENOVE PLAZOS AUTO V1')
print('BACKUP:',backup)
print('Smartphone 48 -> accesorios 48 si existe cuota_48 numerica; si no, 24.')
print('Smartphone 24 -> accesorios 24, salvo plazos fijados manualmente.')
print('Cambios manuales de accesorios y de plazos conservados.')
print('No se han modificado precios ni formulas de total.')
