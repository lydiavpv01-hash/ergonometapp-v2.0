document.addEventListener('DOMContentLoaded',()=>{
  const style=document.createElement('style');
  style.textContent=`
  .ai2-auto{margin:12px 0 0;padding:12px;border:1px solid #dfe6d8;border-radius:10px;background:#f8faf6}.ai2-auto h4{margin:0 0 8px;font-size:12px;color:#536d25}.freq-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}.freq-grid label{font-size:10px}.auto-result{margin-top:10px;padding:10px;border-radius:9px;background:#fff;border:1px solid #e3e8df;font-size:11px;line-height:1.5}.auto-result strong{font-size:13px}.swatch{display:inline-block;width:13px;height:13px;border-radius:4px;margin-right:6px;vertical-align:-2px;border:1px solid rgba(0,0,0,.12)}.swatch-verde{background:#73a942}.swatch-naranja{background:#f4a62a}.swatch-rojo{background:#e6323c}.swatch-morado{background:#51339a}.ai5-table td.color-cell{font-weight:800}.ai5-table td.color-verde{background:#eaf3df}.ai5-table td.color-naranja{background:#fff3df}.ai5-table td.color-rojo{background:#fde9e7}.ai5-table td.color-morado{background:#eee8f6}.refs,.nom-expanded-refs{display:none!important}@media(max-width:700px){.freq-grid{grid-template-columns:1fr}}`;
  document.head.appendChild(style);

  // 1) Ocultar únicamente la galería lateral "Referencias NOM · vista ampliada".
  document.querySelectorAll('.refs').forEach(el=>el.style.display='none');
  document.querySelectorAll('h2,h3,h4,strong').forEach(el=>{
    const t=(el.textContent||'').toLowerCase();
    if(t.includes('referencias nom')&&t.includes('vista ampliada')){
      const box=el.closest('.panel,.factor,.ref-card,section,aside,div');
      if(box) box.style.display='none';
    }
  });

  // 2) AI.2 b) conservar las DOS condiciones moderadas de la ilustración oficial.
  const dist=document.querySelector("#ai2 .choices[data-factor='ai2_distancia']");
  if(dist){
    dist.innerHTML=`
      <div class='choice' data-v='0'>Cerca · brazos alineados verticalmente y torso erguido · 0</div>
      <div class='choice' data-v='3'>Moderado · los brazos se alejan del cuerpo · 3</div>
      <div class='choice' data-v='3'>Moderado · torso inclinado hacia adelante · 3</div>
      <div class='choice' data-v='6'>Lejos · brazos fuera del cuerpo y torso inclinado hacia adelante · 6</div>`;
    dist.querySelectorAll('.choice').forEach(c=>c.addEventListener('click',()=>{
      dist.querySelectorAll('.choice').forEach(x=>x.classList.remove('active'));
      c.classList.add('active');
      if(window.vals){ vals.ai2=vals.ai2||{}; vals.ai2.ai2_distancia=Number(c.dataset.v); }
      if(typeof window.calc==='function') window.calc();
    }));
  }

  // 3) AI.2 a) cálculo automático mediante interpolación entre los puntos de referencia de la gráfica publicada.
  // Frecuencias de referencia expresadas como levantamientos/hora.
  const anchors=[
    {f:1/24,g:23,o:45,r:50},
    {f:2,g:19,o:40,r:50},
    {f:12,g:17,o:39,r:50},
    {f:30,g:15,o:35,r:50},
    {f:60,g:14,o:30,r:47},
    {f:250,g:13,o:22,r:32},
    {f:400,g:11,o:20,r:28},
    {f:720,g:9,o:17,r:24}
  ];
  function interp(f,key){
    if(f<=anchors[0].f) return anchors[0][key];
    if(f>=anchors[anchors.length-1].f) return anchors[anchors.length-1][key];
    for(let i=0;i<anchors.length-1;i++){
      const a=anchors[i],b=anchors[i+1];
      if(f>=a.f&&f<=b.f){const p=(f-a.f)/(b.f-a.f);return a[key]+p*(b[key]-a[key]);}
    }
    return anchors[anchors.length-1][key];
  }
  function evaluate(weight,fph){
    const green=interp(fph,'g'), orange=interp(fph,'o'), red=interp(fph,'r');
    if(weight<=green) return {value:0,color:'Verde',limit:green};
    if(weight<=orange) return {value:4,color:'Naranja',limit:orange};
    if(weight<=red) return {value:6,color:'Rojo',limit:red};
    return {value:10,color:'Morado',limit:red};
  }
  const weight=document.getElementById('pesoAI2');
  const oldFreq=document.getElementById('frecuencia');
  const factor=document.querySelector("#ai2 .choices[data-factor='ai2_peso']");
  if(weight&&oldFreq&&factor){
    oldFreq.closest('div').style.display='none';
    const box=document.createElement('div');box.className='ai2-auto';
    box.innerHTML=`<h4>Frecuencia de levantamiento · cálculo automático</h4>
      <div class='freq-grid'>
        <div><label>Número de levantamientos</label><input id='ai2LiftCount' type='number' min='0' step='1' value='1'></div>
        <div><label>Cada</label><input id='ai2Interval' type='number' min='0.001' step='0.1' value='1'></div>
        <div><label>Unidad de tiempo</label><select id='ai2Unit'><option value='seconds'>segundos</option><option value='minutes' selected>minutos</option><option value='hours'>horas</option><option value='days'>días</option></select></div>
      </div>
      <div class='auto-result' id='ai2GraphResult'>Ingresa el peso y la frecuencia para estimar la banda de la gráfica.</div>`;
    factor.parentElement.insertBefore(box,factor);
    const count=box.querySelector('#ai2LiftCount'), interval=box.querySelector('#ai2Interval'), unit=box.querySelector('#ai2Unit'), out=box.querySelector('#ai2GraphResult');
    function fph(){const n=Number(count.value),t=Number(interval.value);if(!(n>0&&t>0))return 0;const hours=unit.value==='seconds'?t/3600:unit.value==='minutes'?t/60:unit.value==='hours'?t:t*24;return n/hours;}
    function apply(){
      const w=Number(weight.value),f=fph(); if(!(w>=0&&f>0)){out.textContent='Ingresa el peso y una frecuencia válida.';return;}
      const e=evaluate(w,f); oldFreq.value=f.toFixed(3)+' levantamientos/hora';
      const sw='swatch-'+e.color.toLowerCase();
      out.innerHTML=`<strong><span class='swatch ${sw}'></span>${e.color} · Valor ${e.value}</strong><br>${f.toFixed(2)} levantamientos/hora. Resultado obtenido por interpolación digital entre los puntos de referencia de la gráfica de la NOM.`;
      factor.querySelectorAll('.choice').forEach(x=>x.classList.toggle('active',Number(x.dataset.v)===e.value));
      if(window.vals){vals.ai2=vals.ai2||{};vals.ai2.ai2_peso=e.value;}
      if(typeof window.calc==='function') window.calc();
    }
    [weight,count,interval,unit].forEach(el=>{el.addEventListener('input',apply);el.addEventListener('change',apply)});
    apply();
  }

  // 4) AI.5: además del nombre del color, mostrar visualmente el color de la banda en la celda.
  function decorateAI5(){
    const host=document.getElementById('ai5'); if(!host)return;
    host.querySelectorAll('.band').forEach(b=>{
      const td=b.closest('td'); if(!td)return;
      td.classList.remove('color-cell','color-verde','color-naranja','color-rojo','color-morado');
      const txt=(b.textContent||'').trim().toLowerCase();
      if(['verde','naranja','rojo','morado'].includes(txt)){
        td.classList.add('color-cell','color-'+txt);
        if(!b.querySelector('.swatch')) b.insertAdjacentHTML('afterbegin',`<span class='swatch swatch-${txt}'></span>`);
      }
    });
  }
  const ai5=document.getElementById('ai5');
  if(ai5){new MutationObserver(decorateAI5).observe(ai5,{childList:true,subtree:true});decorateAI5();}
  document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',()=>setTimeout(decorateAI5,0)));
});