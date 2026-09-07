(function(){
  function textOf(el){return el ? (el.value || el.textContent || '').trim() : ''}
  function firstInputs(){return Array.from(document.querySelectorAll('input')).filter(x=>x.type!=='checkbox'&&x.type!=='radio'&&x.type!=='file')}
  function riskFromScore(t){if(t>=21)return 'Muy Alto · Inaceptable';if(t>=13)return 'Alto · Significativo';if(t>=5)return 'Medio · Posible';return 'Bajo · Aceptable'}
  function totalObj(o){return Object.values(o||{}).reduce((a,b)=>a+(Number(b)||0),0)}
  function nearestLabel(el){
    if(!el)return '';
    if(el.id){const l=document.querySelector('label[for="'+CSS.escape(el.id)+'"]');if(l)return l.textContent.trim()}
    const wrap=el.closest('div');const l=wrap&&wrap.querySelector(':scope > label');return l?l.textContent.trim():'';
  }
  function collectSnapshot(){
    const fields=[];
    document.querySelectorAll('input,select,textarea').forEach((el,i)=>{
      if(el.type==='file'||el.type==='button'||el.type==='submit'||el.type==='hidden')return;
      if((el.type==='checkbox'||el.type==='radio')&&!el.checked)return;
      const value=el.type==='checkbox'||el.type==='radio'?(el.value||'Sí'):el.value;
      if(value===undefined||value===null||String(value).trim()==='')return;
      fields.push({id:el.id||'',name:el.name||'',label:nearestLabel(el)||el.getAttribute('aria-label')||('Campo '+(i+1)),value:String(value)});
    });
    const selections=[];
    document.querySelectorAll('.choices').forEach(g=>{
      const active=g.querySelector('.choice.active');if(!active)return;
      const factor=g.dataset.factor||'';
      const box=g.closest('.factor,.q');
      const title=box&&box.querySelector('h3,b');
      selections.push({factor,title:title?title.textContent.trim():factor,selection:active.textContent.trim(),value:active.dataset.v!==undefined?active.dataset.v:''});
    });
    document.querySelectorAll('.opts').forEach(g=>{
      const active=g.querySelector('.opt.active');if(!active)return;
      const box=g.closest('.q');const title=box&&box.querySelector('b');
      selections.push({factor:g.dataset.name||'',title:title?title.textContent.trim():(g.dataset.name||''),selection:active.textContent.trim(),value:active.dataset.v||active.textContent.trim()});
    });
    return {fields,selections};
  }
  async function collectUploads(){
    const files=[];
    const inputs=Array.from(document.querySelectorAll('input[type=file]'));
    for(const inp of inputs){
      for(const file of Array.from(inp.files||[])){
        const data=await new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsDataURL(file)});
        files.push({field:inp.name||inp.id||'archivo',name:file.name,type:file.type,size:file.size,data});
      }
    }
    return files;
  }
  async function persist(payload,button){
    const old=button.textContent; button.disabled=true; button.textContent='Guardando…';
    try{
      payload.snapshot=collectSnapshot();
      payload.uploads=await collectUploads();
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
    button.addEventListener('click',async()=>{
      const inputs=firstInputs();
      const trabajador=textOf(document.querySelector('#trabajador'))||textOf(inputs[0]);
      const puesto=textOf(document.querySelector('#puesto'))||textOf(inputs[1]);
      const scores={ai2:typeof vals!=='undefined'?totalObj(vals.ai2):0,ai3:typeof vals!=='undefined'?totalObj(vals.ai3):0,ai4:typeof vals!=='undefined'?totalObj(vals.ai4):0};
      const final=Math.max(scores.ai2,scores.ai3,scores.ai4);
      await persist({metodo:'APENDICE_I',meta:{trabajador,puesto,fecha:new Date().toLocaleDateString('es-MX')},evaluation:{values:typeof vals!=='undefined'?vals:{},scores},result:{final_score:final,risk_level:riskFromScore(final)}},button);
    });
  }
  function appendixII(){
    const button=document.querySelector('.save'); if(!button)return;
    button.onclick=null;
    button.addEventListener('click',async()=>{
      const inputs=firstInputs();
      const trabajador=textOf(inputs[0]),puesto=textOf(inputs[1]);
      const final=Number(textOf(document.getElementById('total')))||0;
      await persist({metodo:'APENDICE_II',meta:{trabajador,puesto,fecha:new Date().toLocaleDateString('es-MX')},evaluation:{values:typeof vals!=='undefined'?vals:{},modo:textOf(document.getElementById('modo')),peso:textOf(document.getElementById('peso'))},result:{final_score:final,risk_level:textOf(document.getElementById('risk'))||riskFromScore(final)}},button);
    });
  }
  function kuorinka(){
    const button=document.querySelector('.save'); if(!button)return;
    button.onclick=null;
    button.addEventListener('click',async()=>{
      const positives=typeof data!=='undefined'?Object.entries(data).filter(([k,v])=>v&&v.molestias==='Sí').map(([k])=>k):[];
      await persist({metodo:'KUORINKA',meta:{trabajador:'Cuestionario individual',puesto:'No especificado',fecha:new Date().toLocaleDateString('es-MX')},evaluation:{regions:typeof data!=='undefined'?data:{}},result:{final_score:null,risk_level:positives.length?positives.length+' regiones con molestias':'Sin molestias positivas',summary:positives.join(', ')}},button);
    });
  }
  const p=location.pathname;
  if(p==='/apendice-i/nueva')appendixI();
  else if(p==='/apendice-ii/nueva')appendixII();
  else if(p==='/cuestionario-nordico/nueva')kuorinka();
})();
