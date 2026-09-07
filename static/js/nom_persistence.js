(function(){
  function textOf(el){return el ? (el.value || el.textContent || '').trim() : ''}
  function firstInputs(){return Array.from(document.querySelectorAll('input')).filter(x=>x.type!=='checkbox'&&x.type!=='radio')}
  function riskFromScore(t){if(t>=21)return 'Muy Alto · Inaceptable';if(t>=13)return 'Alto · Significativo';if(t>=5)return 'Medio · Posible';return 'Bajo · Aceptable'}
  function totalObj(o){return Object.values(o||{}).reduce((a,b)=>a+(Number(b)||0),0)}
  async function persist(payload,button){
    const old=button.textContent; button.disabled=true; button.textContent='Guardando…';
    try{
      const r=await fetch('/api/evaluaciones',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      const j=await r.json();
      if(!r.ok||j.status!=='success')throw new Error(j.message||'No se pudo guardar');
      button.textContent='Guardado ✓';
      setTimeout(()=>{window.location.href='/evaluaciones'},550);
    }catch(e){button.disabled=false;button.textContent=old;alert('Error al guardar: '+e.message)}
  }
  function appendixI(){
    const button=document.querySelector('.save'); if(!button)return;
    button.onclick=null;
    button.addEventListener('click',()=>{
      const inputs=firstInputs();
      const trabajador=textOf(document.querySelector('#trabajador'))||textOf(inputs[0]);
      const puesto=textOf(document.querySelector('#puesto'))||textOf(inputs[1]);
      const scores={ai2:typeof vals!=='undefined'?totalObj(vals.ai2):0,ai3:typeof vals!=='undefined'?totalObj(vals.ai3):0,ai4:typeof vals!=='undefined'?totalObj(vals.ai4):0};
      const final=Math.max(scores.ai2,scores.ai3,scores.ai4);
      persist({metodo:'APENDICE_I',meta:{trabajador,puesto,fecha:new Date().toLocaleDateString('es-MX')},evaluation:{values:typeof vals!=='undefined'?vals:{},scores},result:{final_score:final,risk_level:riskFromScore(final)}},button);
    });
  }
  function appendixII(){
    const button=document.querySelector('.save'); if(!button)return;
    button.onclick=null;
    button.addEventListener('click',()=>{
      const inputs=firstInputs();
      const trabajador=textOf(inputs[0]),puesto=textOf(inputs[1]);
      const final=Number(textOf(document.getElementById('total')))||0;
      persist({metodo:'APENDICE_II',meta:{trabajador,puesto,fecha:new Date().toLocaleDateString('es-MX')},evaluation:{values:typeof vals!=='undefined'?vals:{},modo:textOf(document.getElementById('modo')),peso:textOf(document.getElementById('peso'))},result:{final_score:final,risk_level:textOf(document.getElementById('risk'))||riskFromScore(final)}},button);
    });
  }
  function kuorinka(){
    const button=document.querySelector('.save'); if(!button)return;
    button.onclick=null;
    button.addEventListener('click',()=>{
      const positives=typeof data!=='undefined'?Object.entries(data).filter(([k,v])=>v&&v.molestias==='Sí').map(([k])=>k):[];
      persist({metodo:'KUORINKA',meta:{trabajador:'Cuestionario individual',puesto:'No especificado',fecha:new Date().toLocaleDateString('es-MX')},evaluation:{regions:typeof data!=='undefined'?data:{}},result:{final_score:null,risk_level:positives.length?positives.length+' regiones con molestias':'Sin molestias positivas',summary:positives.join(', ')}},button);
    });
  }
  const p=location.pathname;
  if(p==='/apendice-i/nueva')appendixI();
  else if(p==='/apendice-ii/nueva')appendixII();
  else if(p==='/cuestionario-nordico/nueva')kuorinka();
})();
