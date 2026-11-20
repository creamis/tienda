#!/usr/bin/env python3
"""Reinicia accesorios y plazos manuales al cambiar smartphone en Renove Particular."""
from pathlib import Path
from datetime import datetime
import shutil,sys
p=Path('/home/tienda/tienda/crm/templates/crm/renove_particular.html')
if not p.is_file():sys.exit('ABORTADO: plantilla inexistente')
s=p.read_text(encoding='utf-8')
marker='/* RENOVE_RESET_PACK_SMARTPHONE_V1 */'
if marker in s:sys.exit('YA INSTALADO: sin cambios')
if s.count('/* RENOVE_PACK_MARCA_V1 */')!=1 or s.count('/* RENOVE_PLAZOS_AUTO_V1 */')!=1:sys.exit('ABORTADO: versiones de Renove inesperadas')
old=""" const sugeridos=extras(d?.marca||'');
 if(!Array.isArray(l.accesoriosElegidosManualmente))l.accesoriosElegidosManualmente=[false,false];
 sugeridos.forEach((a,k)=>{
  if(!l.accesoriosElegidosManualmente[k]){
   l.extras[k]=a;
   l.plazos[k]=24;
  }
 });
 sincronizarPlazosRenove(l);
 pintar()"""
new=""" /* RENOVE_RESET_PACK_SMARTPHONE_V1 */
 const sugeridos=extras(d?.marca||'');
 l.accesoriosElegidosManualmente=[false,false];
 l.plazosElegidosManualmente=[false,false];
 l.extras=[...sugeridos];
 l.plazos=[24,24];
 l.manual=false;
 sincronizarPlazosRenove(l);
 pintar()"""
if s.count(old)!=1:sys.exit(f'ABORTADO: bloque de cambio de smartphone inesperado (coincidencias: {s.count(old)}); no se modifica nada')
if 'ds.onchange=()=>{' not in s:sys.exit('ABORTADO: selector smartphone no encontrado')
if s.count('sincronizarPlazosRenove(l);')<2:sys.exit('ABORTADO: falta sincronizacion de plazos')
newtext=s.replace(old,new,1)
if newtext.count(marker)!=1:sys.exit('ABORTADO: marcador no unico')
backup=p.with_name(p.name+'.bak_reset_pack_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
shutil.copy2(p,backup)
tmp=p.with_name(p.name+'.tmp_reset_pack')
try:
 tmp.write_text(newtext,encoding='utf-8')
 tmp.replace(p)
except Exception:
 if tmp.exists():tmp.unlink()
 shutil.copy2(backup,p)
 raise
print('CORRECTO: al cambiar smartphone se reinicia la composicion del pack.')
print('Accesorios y plazos manuales reiniciados; se seleccionan accesorios por marca.')
print('Tarifa y promocion conservadas. Financiacion smartphone reiniciada a 24 meses como antes.')
print('BACKUP:',backup)
