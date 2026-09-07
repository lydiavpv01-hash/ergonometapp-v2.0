from flask import Blueprint, render_template

bp_apendice_i = Blueprint('apendice_i', __name__, url_prefix='/apendice-i')

AI5_ENHANCEMENT = r"""
<style>
.ai5-title{font:500 18px Georgia;margin:0 0 8px}.ai5-intro{font-size:11px;line-height:1.6;color:#56605a;margin:0 0 14px}.ai5-table-wrap{overflow:auto;border:1px solid #e3e8df;border-radius:12px;margin-bottom:16px}.ai5-table{width:100%;border-collapse:collapse;min-width:880px;font-size:11px}.ai5-table th,.ai5-table td{border-bottom:1px solid #e3e8df;border-right:1px solid #edf0ec;padding:9px 8px;text-align:center;vertical-align:middle}.ai5-table th:last-child,.ai5-table td:last-child{border-right:0}.ai5-table th{background:#f7f9f5;color:#59625c;font-size:10px;text-transform:uppercase;letter-spacing:.03em}.ai5-table td:first-child,.ai5-table th:first-child{text-align:left;min-width:285px}.band{display:inline-block;min-width:68px;padding:4px 7px;border-radius:999px;font-size:10px;font-weight:800}.band-green{background:#eaf3df;color:#466326}.band-orange{background:#fff0d8;color:#9a5e0a}.band-red{background:#fde5e2;color:#9c342d}.band-purple{background:#eee5f7;color:#6c438c}.band-empty{background:#f1f3f1;color:#8a928c}.ai5-total{font-weight:900;font-size:13px}.ai5-level{font-weight:800}.ai5-actions{width:100%;border-collapse:collapse;font-size:11px}.ai5-actions th,.ai5-actions td{padding:10px;border-bottom:1px solid #e3e8df;vertical-align:top;text-align:left}.ai5-actions th{font-size:10px;text-transform:uppercase;color:#6d756f}.ai5-section-label{font-size:12px;font-weight:850;color:#536d25;margin:18px 0 8px}.ai5-note{border-left:4px solid #536d25;background:#f7faf3;border-radius:8px;padding:11px 12px;font-size:11px;line-height:1.55;color:#52604e;margin-bottom:14px}
</style>
<script>
(function(){
 const factorRows=[
  ['Peso de la carga / frecuencia de transporte','ai2_peso','ai3_peso','ai4_peso'],
  ['Distancia horizontal entre las manos y la parte inferior de la espalda','ai2_distancia','ai3_distancia','ai4_distancia'],
  ['Región de levantamiento vertical','ai2_vertical',null,'ai4_vertical'],
  ['Torsión y flexión lateral del torso / Carga asimétrica sobre el torso','ai2_torsion','ai3_asimetria','ai4_torsion'],
  ['Restricciones posturales','ai2_restriccion','ai3_restriccion','ai4_restriccion'],
  ['Acoplamiento mano-carga (elementos de sujeción)','ai2_agarre','ai3_agarre','ai4_agarre'],
  ['Superficie de trabajo','ai2_superficie','ai3_superficie','ai4_superficie'],
  ['Otros factores ambientales','ai2_ambiente','ai3_ambiente','ai4_ambiente'],
  ['Distancia de transporte',null,'ai3_distancia_transporte',null],
  ['Obstáculos en la ruta (sólo en transporte)',null,'ai3_obstaculos',null],
  ['Comunicación, coordinación y control (sólo manejo manual de cargas en equipo)',null,null,'ai4_coordinacion']
 ];
 function colorFor(key,v){
   if(v===undefined || v===null) return null;
   if(v===0) return 'Verde';
   if(key && key.endsWith('_peso')) return v===4?'Naranja':v===6?'Rojo':'Morado';
   const orangeValues={ai2_distancia:[3],ai2_vertical:[1],ai2_torsion:[1],ai2_restriccion:[1],ai2_agarre:[1],ai2_superficie:[1],ai2_ambiente:[1],ai3_distancia:[3],ai3_asimetria:[1],ai3_restriccion:[1],ai3_agarre:[1],ai3_superficie:[1],ai3_ambiente:[1],ai3_distancia_transporte:[1],ai3_obstaculos:[1],ai4_distancia:[3],ai4_vertical:[1],ai4_torsion:[1],ai4_restriccion:[1],ai4_agarre:[1],ai4_superficie:[1],ai4_ambiente:[1],ai4_coordinacion:[1]};
   return (orangeValues[key]||[]).includes(v)?'Naranja':'Rojo';
 }
 function badge(color){if(!color)return '<span class="band band-empty">—</span>';return '<span class="band band-'+color.toLowerCase()+'">'+color+'</span>'}
 function val(section,key){return key&&vals[section]&&Object.prototype.hasOwnProperty.call(vals[section],key)?vals[section][key]:null}
 function total(section){return Object.values(vals[section]||{}).reduce((a,b)=>a+(Number(b)||0),0)}
 function level(t){if(t>=21)return ['Muy Alto - Inaceptable','Se requieren acciones correctivas inmediatamente'];if(t>=13)return ['Alto - Significativo','Se requieren acciones correctivas pronto'];if(t>=5)return ['Medio - Posible','Se requieren acciones correctivas a corto plazo'];return ['Bajo - Aceptable','No se requieren acciones correctivas']}
 function cell(section,key){const v=val(section,key),c=colorFor(key,v);return '<td>'+badge(c)+'</td><td>'+(v===null?'—':v)+'</td>'}
 function renderAI5(){
  const host=document.getElementById('ai5'); if(!host)return;
  const t2=total('ai2'),t3=total('ai3'),t4=total('ai4'),l2=level(t2),l3=level(t3),l4=level(t4);
  host.innerHTML=`<h3 class="ai5-title">AI.5 Estimación del nivel de riesgo</h3>
  <p class="ai5-intro">Para estimar el nivel de riesgo se deberá registrar el color y valor obtenido en cada uno de los factores analizados para cada tipo de actividad, determinar el nivel de riesgo y definir las acciones correspondientes.</p>
  <div class="ai5-section-label">a) Registro de color y valor por factor</div>
  <div class="ai5-table-wrap"><table class="ai5-table"><thead><tr><th rowspan="2">Factores de riesgo</th><th colspan="2">Levantar</th><th colspan="2">Transportar</th><th colspan="2">Equipo</th></tr><tr><th>Color</th><th>Valor</th><th>Color</th><th>Valor</th><th>Color</th><th>Valor</th></tr></thead><tbody>
  ${factorRows.map(r=>`<tr><td>${r[0]}</td>${cell('ai2',r[1])}${cell('ai3',r[2])}${cell('ai4',r[3])}</tr>`).join('')}
  <tr><td class="ai5-total">Puntuación</td><td colspan="2" class="ai5-total">${t2}</td><td colspan="2" class="ai5-total">${t3}</td><td colspan="2" class="ai5-total">${t4}</td></tr>
  <tr><td class="ai5-total">Nivel de Riesgo</td><td colspan="2" class="ai5-level">${l2[0]}</td><td colspan="2" class="ai5-level">${l3[0]}</td><td colspan="2" class="ai5-level">${l4[0]}</td></tr>
  </tbody></table></div>
  <div class="ai5-section-label">b) Determinar el nivel de riesgo</div>
  <div class="ai5-table-wrap"><table class="ai5-actions"><thead><tr><th>Nivel de riesgo</th><th>Prioridad</th><th>Puntaje total</th></tr></thead><tbody><tr><td>Bajo – Aceptable</td><td>No se requieren acciones correctivas</td><td>0 a 4</td></tr><tr><td>Medio – Posible</td><td>Se requieren acciones correctivas a corto plazo</td><td>5 a 12</td></tr><tr><td>Alto – Significativo</td><td>Se requieren acciones correctivas pronto</td><td>13 a 20</td></tr><tr><td>Muy Alto - Inaceptable</td><td>Se requieren acciones correctivas inmediatamente</td><td>21 a 32</td></tr></tbody></table></div>
  <div class="ai5-section-label">c) Acciones conforme al nivel de riesgo</div>
  <div class="ai5-table-wrap"><table class="ai5-actions"><thead><tr><th>Nivel de riesgo</th><th>Acciones</th></tr></thead><tbody><tr><td>Bajo – Aceptable</td><td>Sólo se requiere dar seguimiento a los grupos más vulnerables, como mujeres en periodo de gestación o trabajadores menores de edad.</td></tr><tr><td>Medio – Posible</td><td>Se debe examinar las tareas con mayor detalle mediante una evaluación específica, o implantar medidas de control mediante un Programa de ergonomía para el manejo manual de cargas.</td></tr><tr><td>Alto – Significativo</td><td>Se requiere una acción rápida y establecer medidas de control mediante un Programa de ergonomía para el manejo manual de cargas.</td></tr><tr><td>Muy Alto - Inaceptable</td><td>Se deben detener las actividades e implementar medidas de control mediante un Programa de ergonomía para el manejo manual de cargas.</td></tr></tbody></table></div>`;
 }
 const originalCalc=calc; calc=function(){originalCalc();renderAI5()};
 document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>{if(b.dataset.sec==='ai5')renderAI5()}));
 renderAI5();
})();
</script>
"""

@bp_apendice_i.route('/nueva', methods=['GET'])
def nueva():
    html = render_template('apendice_i_workspace.html')
    intro = render_template('apendice_i_intro.html')
    refinements = render_template('apendice_i_refinements_v3.html')
    refinements_v4 = render_template('apendice_i_refinements_v4.html')
    refinements_v5 = render_template('apendice_i_refinements_v5.html')
    refinements_v7 = render_template('apendice_i_refinements_v7.html')
    html = html.replace("<div class='tabs'>", intro + "<div class='tabs'>", 1)
    return html.replace('</body>', AI5_ENHANCEMENT + refinements + refinements_v4 + refinements_v5 + refinements_v7 + '</body>')
