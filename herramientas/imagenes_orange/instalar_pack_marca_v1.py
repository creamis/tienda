#!/usr/bin/env python3
"""Instala packs Renove por marca sin alterar precios ni editor manual."""
from pathlib import Path
from datetime import datetime
import shutil,sys
p=Path('/home/tienda/tienda/crm/templates/crm/renove_particular.html')
if not p.is_file():sys.exit('ERROR: plantilla no encontrada')
s=p.read_text(encoding='utf-8')
marker='/* RENOVE_PACK_MARCA_V1 */'
if marker in s:sys.exit('YA INSTALADO: no se han realizado cambios')
old_extras="function extras(){const pick=t=>accesorios.filter(a=>a.tipo===t).sort((a,b)=>(a.cuota*24+a.inicial)-(b.cuota*24+b.inicial)||a.nombre.localeCompare(b.nombre))[0];return [pick('auriculares'),pick('reloj')].filter(Boolean)}"
new_extras="""/* RENOVE_PACK_MARCA_V1 */
function marcaPack(s){
 const v=String(s||'').toUpperCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').trim();
 if(/^(APPLE|IPHONE|IPAD)\\b/.test(v))return 'APPLE';
 if(/^(SAMSUNG|GALAXY)\\b/.test(v))return 'SAMSUNG';
 if(/^(XIAOMI|REDMI|POCO)\\b/.test(v))return 'XIAOMI';
 if(/^(MOTOROLA|MOTO)\\b/.test(v))return 'MOTOROLA';
 if(/^(HONOR|HUAWEI|OPPO|VIVO|ZTE|REALME|TCL|GOOGLE|PIXEL)\\b/.test(v))return v.split(/\\s+/)[0]==='PIXEL'?'GOOGLE':v.split(/\\s+/)[0];
 return v.split(/\\s+/)[0]||'';
}
function marcaAccesorio(a){
 const n=String(a.nombre||'').toUpperCase();
 const m=n.replace(/^AURICULARES\\s+/,'').trim();
 if(/^(APPLE|AIRPODS|APPLE WATCH)\\b/.test(m))return 'APPLE';
 if(/^(SAMSUNG|GALAXY)\\b/.test(m))return 'SAMSUNG';
 if(/^(XIAOMI|REDMI|POCO)\\b/.test(m))return 'XIAOMI';
 if(/^(MOTOROLA|MOTO)\\b/.test(m))return 'MOTOROLA';
 if(/^(HONOR|HUAWEI|OPPO|VIVO|ZTE|REALME|TCL|GOOGLE|PIXEL)\\b/.test(m))return m.split(/\\s+/)[0]==='PIXEL'?'GOOGLE':m.split(/\\s+/)[0];
 return m.split(/\\s+/)[0]||'';
}
function extras(marca){
 const marcaBuscada=marcaPack(marca);
 const pick=t=>{
  const todos=accesorios.filter(a=>a.tipo===t).sort((a,b)=>(Number(a.cuota)*24+Number(a.inicial))-(Number(b.cuota)*24+Number(b.inicial))||a.nombre.localeCompare(b.nombre));
  return todos.find(a=>marcaBuscada&&marcaAccesorio(a)===marcaBuscada)
    ||todos.find(a=>marcaBuscada&&marcaAccesorio(a)==='HUAWEI')
    ||todos[0];
 };
 return [pick('auriculares'),pick('reloj')].filter(Boolean);
}"""
old_change="ds.onchange=()=>{l.dispositivo=ds.value;l.mesesPrincipal=24;pintar()};"
new_change="""ds.onchange=()=>{
 l.dispositivo=ds.value;
 l.mesesPrincipal=24;
 const d=datos.find(x=>String(x.id)===String(l.dispositivo));
 const sugeridos=extras(d?.marca||'');
 if(!Array.isArray(l.accesoriosElegidosManualmente))l.accesoriosElegidosManualmente=[false,false];
 sugeridos.forEach((a,k)=>{
  if(!l.accesoriosElegidosManualmente[k]){
   l.extras[k]=a;
   l.plazos[k]=24;
  }
 });
 pintar()
};"""
old_manual="s.onchange=()=>{l.extras[k]=accesorios[Number(s.value)];l.plazos[k]=24;pintar()};"
new_manual="s.onchange=()=>{l.extras[k]=accesorios[Number(s.value)];l.plazos[k]=24;if(!Array.isArray(l.accesoriosElegidosManualmente))l.accesoriosElegidosManualmente=[false,false];l.accesoriosElegidosManualmente[k]=true;pintar()};"
old_new="extras:extras(),plazos:[24,24],mesesPrincipal:24,manual:false"
new_new="extras:extras(),plazos:[24,24],mesesPrincipal:24,manual:false,accesoriosElegidosManualmente:[false,false]"
replacements=[(old_extras,new_extras,'selector automatico'),(old_change,new_change,'cambio smartphone'),(old_manual,new_manual,'cambio manual'),(old_new,new_new,'estado de linea')]
for a,b,name in replacements:
 n=s.count(a)
 if n!=1:sys.exit(f'ABORTADO SIN CAMBIOS: {name} aparece {n} veces (se esperaba 1)')
for a,b,_ in replacements:s=s.replace(a,b,1)
assert s.count(marker)==1
assert s.count('l.plazos[k]=Number(plazo.value);pintar()')==1
assert s.count("l.manual=!l.manual;pintar()")==1
backup=p.with_name(p.name+'.bak_marca_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
shutil.copy2(p,backup)
temp=p.with_name(p.name+'.tmp_marca')
try:
 temp.write_text(s,encoding='utf-8')
 temp.replace(p)
except Exception:
 if temp.exists():temp.unlink()
 shutil.copy2(backup,p)
 raise
print('INSTALADO RENOVE PACK MARCA V1')
print('BACKUP:',backup)
print('Smartphone -> accesorios mas baratos de misma marca; Huawei; mas baratos globales')
print('Cambios manuales individuales respetados, precios y financiacion intactos')
print('Reinicia la web desde PythonAnywhere si no se refleja al recargar.')
