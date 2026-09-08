(function(){
  const SAVE_TIMEOUT_MS=45000;
  const MAX_IMAGE_SIDE=1600;
  const JPEG_QUALITY=0.82;
  const MAX_SINGLE_UPLOAD_BYTES=12*1024*1024;
  const MAX_ENCODED_PAYLOAD_CHARS=18*1024*1024;

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

  function readAsDataURL(file){
    return new Promise((resolve,reject)=>{
      const r=new FileReader();
      r.onload=()=>resolve(r.result);
      r.onerror=()=>reject(new Error('No se pudo leer '+file.name));
      r.readAsDataURL(file);
    });
  }

  function loadImage(src){
    return new Promise((resolve,reject)=>{
      const img=new Image();
      img.onload=()=>resolve(img);
      img.onerror=()=>reject(new Error('No se pudo procesar la imagen'));
      img.src=src;
    });
  }

  async function optimizedImage(file,field){
    if(file.size>MAX_SINGLE_UPLOAD_BYTES)throw new Error('La imagen "'+file.name+'" excede 12 MB. Reduce su tamaño antes de guardar.');
    const raw=await readAsDataURL(file);
    if(!String(file.type||'').startsWith('image/'))return {field,name:file.name,type:file.type,size:file.size,data:raw};

    /* Los logos pequeños se conservan sin recomprimir para no degradar texto o transparencias. */
    const isLogo=/logo_/i.test(field||'');
    if(isLogo && file.size<=1500000)return {field,name:file.name,type:file.type,size:file.size,data:raw};

    try{
      const img=await loadImage(raw);
      const scale=Math.min(1,MAX_IMAGE_SIDE/Math.max(img.naturalWidth||img.width,img.naturalHeight||img.height));
      const w=Math.max(1,Math.round((img.naturalWidth||img.width)*scale));
      const h=Math.max(1,Math.round((img.naturalHeight||img.height)*scale));
      const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
      const ctx=canvas.getContext('2d');
      if(!ctx)return {field,name:file.name,type:file.type,size:file.size,data:raw};
      /* Fondo blanco evita fondo negro al pasar imágenes transparentes a JPEG. */
      ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);ctx.drawImage(img,0,0,w,h);
      const data=canvas.toDataURL('image/jpeg',JPEG_QUALITY);
      return {field,name:file.name.replace(/\.[^.]+$/,'')+'.jpg',type:'image/jpeg',size:Math.round(data.length*0.75),data,original_name:file.name,original_size:file.size};
    }catch(_){
      return {field,name:file.name,type:file.type,size:file.size,data:raw};
    }
  }

  async function collectUploads(button){
    const files=[];
    const tasks=[];
    Array.from(document.querySelectorAll('input[type=file]')).forEach(inp=>{
      const field=inp.name||inp.id||'archivo';
      Array.from(inp.files||[]).forEach(file=>tasks.push({field,file}));
    });
    for(let i=0;i<tasks.length;i++){
      if(button)button.textContent='Preparando imágenes '+(i+1)+'/'+tasks.length+'…';
      files.push(await optimizedImage(tasks[i].file,tasks[i].field));
      await new Promise(r=>setTimeout(r,0));
    }
    return files;
  }

  async function persist(payload,button){
    if(button.dataset.saving==='1')return;
    const old=button.textContent;
    button.dataset.saving='1';button.disabled=true;button.textContent='Preparando datos…';
    let timer=null;
    try{
      payload.snapshot=collectSnapshot();
      payload.uploads=await collectUploads(button);
      button.textContent='Guardando…';
      const body=JSON.stringify(payload);
      if(body.length>MAX_ENCODED_PAYLOAD_CHARS){
        throw new Error('La evaluación contiene demasiadas imágenes para enviarse en una sola operación. Reduce la cantidad o tamaño de fotografías y vuelve a guardar.');
      }
      const controller=new AbortController();
      timer=setTimeout(()=>controller.abort(),SAVE_TIMEOUT_MS);
      const r=await fetch('/api/evaluaciones',{method:'POST',headers:{'Content-Type':'application/json'},body,signal:controller.signal});
      clearTimeout(timer);timer=null;
      let j={};
      try{j=await r.json()}catch(_){throw new Error('El servidor respondió sin un resultado válido. No se confirmó el guardado.');}
      if(!r.ok||j.status!=='success')throw new Error(j.message||'No se pudo guardar');
      button.textContent='Guardado ✓';
      setTimeout(()=>{window.location.href='/evaluaciones'},550);
    }catch(e){
      if(timer)clearTimeout(timer);
      button.disabled=false;button.dataset.saving='0';button.textContent=old;
      const msg=e&&e.name==='AbortError'
        ?'El guardado superó 45 segundos y se canceló para evitar que la pantalla quede bloqueada. Revisa Evaluaciones guardadas antes de intentarlo otra vez. Si no aparece, reduce las fotografías o vuelve a guardar.'
        :(e.message||'No se pudo guardar la evaluación.');
      alert('Error al guardar: '+msg);
    }
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
