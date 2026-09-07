(()=>{
  const q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)];
  const scoreEls=qa('.results .result b');
  const saveBtn=qa('.top-actions .primary').find(b=>b.textContent.includes('Guardar'));
  const options=q('.options');
  let lastResult=null;
  const cfg={
    Cuello:{twisted:false,tilted:false,direction:'flexion'},
    Tronco:{twisted:false,tilted:false,direction:'flexion'},
    Piernas:{condition:'both_supported'},
    Brazo:{shoulder_raised:false,abducted:false,supported:false,direction:'flexion'},
    Antebrazo:{},
    Muñeca:{deviated:false,direction:'flexion'},
    Carga:{value:0,unit:'kg',shock:false},
    Acoplamiento:{coupling:'regular'},
    Actividad:{static:false,repetitive:false,rapid_change:false}
  };

  function lastMeasurement(segment){
    const bucket=store?.[segment];
    if(!bucket || !bucket.photos?.length) return null;
    const ap=bucket.photos.find(p=>p.id===bucket.active) || bucket.photos.at(-1);
    if(ap?.measurements?.length) return ap.measurements.at(-1);
    for(let i=bucket.photos.length-1;i>=0;i--){
      const ms=bucket.photos[i].measurements||[];
      if(ms.length) return ms.at(-1);
    }
    return null;
  }

  function segmentOptions(seg){
    if(!options) return;
    const s=cfg[seg]||{};
    const head='<div class="card-head" style="margin:-18px -18px 8px"><h2>Ajustes del segmento</h2><small>Selección técnica</small></div>';
    const radio=(name,val,label,checked)=>`<div class="option"><label><input type="radio" name="${name}" value="${val}" ${checked?'checked':''}> ${label}</label></div>`;
    const check=(id,label,checked)=>`<div class="option"><label><input id="${id}" type="checkbox" ${checked?'checked':''}> ${label}</label></div>`;
    let body='';
    if(seg==='Cuello') body=radio('direction','flexion','Flexión',s.direction==='flexion')+radio('direction','extension','Extensión',s.direction==='extension')+check('neckTwisted','Cuello torcido (+1)',s.twisted)+check('neckTilted','Inclinación lateral (+1)',s.tilted);
    else if(seg==='Tronco') body=radio('direction','flexion','Flexión',s.direction==='flexion')+radio('direction','extension','Extensión',s.direction==='extension')+radio('direction','neutral','Neutral',s.direction==='neutral')+check('trunkTwisted','Tronco torcido (+1)',s.twisted)+check('trunkTilted','Inclinación lateral (+1)',s.tilted);
    else if(seg==='Piernas') body=`<div class="option"><label>Condición de apoyo</label><select id="legsCondition" style="width:100%;margin-top:8px;padding:9px;border:1px solid #dfe4dd;border-radius:7px"><option value="both_supported" ${s.condition==='both_supported'?'selected':''}>Ambas piernas apoyadas</option><option value="unilateral" ${s.condition==='unilateral'?'selected':''}>Apoyo unilateral / una pierna levantada</option><option value="unstable" ${s.condition==='unstable'?'selected':''}>Postura inestable</option></select></div><div class="option"><span style="font-size:11px;color:#68716b">El ángulo confirmado se usa como flexión de rodilla.</span></div>`;
    else if(seg==='Brazo') body=radio('direction','flexion','Flexión',s.direction==='flexion')+radio('direction','extension','Extensión',s.direction==='extension')+radio('direction','neutral','Neutral',s.direction==='neutral')+check('armRaised','Hombro elevado (+1)',s.shoulder_raised)+check('armAbducted','Brazo abducido (+1)',s.abducted)+check('armSupported','Brazo apoyado (-1)',s.supported);
    else if(seg==='Antebrazo') body='<div class="option"><span style="font-size:11px;color:#68716b">El puntaje se obtiene directamente del ángulo confirmado.</span></div>';
    else if(seg==='Muñeca') body=radio('direction','flexion','Flexión',s.direction==='flexion')+radio('direction','extension','Extensión',s.direction==='extension')+radio('direction','neutral','Neutral',s.direction==='neutral')+check('wristDeviated','Desviación / torsión de muñeca (+1)',s.deviated);
    else if(seg==='Carga') body=`<div class="option"><label>Carga manipulada</label><div style="display:grid;grid-template-columns:1fr 90px;gap:8px;margin-top:8px"><input id="loadValue" type="number" min="0" step="0.1" value="${s.value}" style="padding:9px;border:1px solid #dfe4dd;border-radius:7px"><select id="loadUnit" style="padding:9px;border:1px solid #dfe4dd;border-radius:7px"><option value="kg" ${s.unit==='kg'?'selected':''}>kg</option><option value="lb" ${s.unit==='lb'?'selected':''}>lb</option></select></div></div>${check('loadShock','Carga aplicada con golpe o fuerza brusca (+1)',s.shock)}`;
    else if(seg==='Acoplamiento') body=`<div class="option"><label>Calidad del acoplamiento</label><select id="coupling" style="width:100%;margin-top:8px;padding:9px;border:1px solid #dfe4dd;border-radius:7px"><option value="good" ${s.coupling==='good'?'selected':''}>Bueno</option><option value="regular" ${s.coupling==='regular'?'selected':''}>Regular</option><option value="poor" ${s.coupling==='poor'?'selected':''}>Malo</option><option value="unacceptable" ${s.coupling==='unacceptable'?'selected':''}>Inaceptable</option></select></div>`;
    else if(seg==='Actividad') body=check('activityStatic','Postura estática prolongada (+1)',s.static)+check('activityRepetitive','Actividad repetitiva (+1)',s.repetitive)+check('activityRapid','Cambios rápidos o inestables (+1)',s.rapid_change);
    options.innerHTML=head+body;

    qa('input[name="direction"]').forEach(x=>x.addEventListener('change',()=>{ cfg[seg].direction=x.value; try{renderGuides()}catch{}; calculateLive(); }));
    const bind=(id,key,kind='checked')=>{const el=q('#'+id); if(el) el.addEventListener(kind==='value'?'input':'change',()=>{cfg[seg][key]=kind==='checked'?el.checked:el.value; calculateLive();});};
    if(seg==='Cuello'){bind('neckTwisted','twisted');bind('neckTilted','tilted');}
    if(seg==='Tronco'){bind('trunkTwisted','twisted');bind('trunkTilted','tilted');}
    if(seg==='Piernas'){const el=q('#legsCondition');if(el)el.addEventListener('change',()=>{cfg.Piernas.condition=el.value;calculateLive();});}
    if(seg==='Brazo'){bind('armRaised','shoulder_raised');bind('armAbducted','abducted');bind('armSupported','supported');}
    if(seg==='Muñeca'){bind('wristDeviated','deviated');}
    if(seg==='Carga'){
      const lv=q('#loadValue'),lu=q('#loadUnit'),ls=q('#loadShock');
      if(lv)lv.addEventListener('input',()=>{cfg.Carga.value=Number(lv.value||0);calculateLive();});
      if(lu)lu.addEventListener('change',()=>{cfg.Carga.unit=lu.value;calculateLive();});
      if(ls)ls.addEventListener('change',()=>{cfg.Carga.shock=ls.checked;calculateLive();});
    }
    if(seg==='Acoplamiento'){const el=q('#coupling');if(el)el.addEventListener('change',()=>{cfg.Acoplamiento.coupling=el.value;calculateLive();});}
    if(seg==='Actividad'){
      [['activityStatic','static'],['activityRepetitive','repetitive'],['activityRapid','rapid_change']].forEach(([id,key])=>{const el=q('#'+id);if(el)el.addEventListener('change',()=>{cfg.Actividad[key]=el.checked;calculateLive();});});
    }
  }

  function payload(){
    const n=lastMeasurement('Cuello'),t=lastMeasurement('Tronco'),l=lastMeasurement('Piernas'),a=lastMeasurement('Brazo'),f=lastMeasurement('Antebrazo'),w=lastMeasurement('Muñeca');
    if(!n||!t||!l||!a||!f||!w) return null;
    return {
      neck:{angle:n.angle,direction:n.direction||cfg.Cuello.direction,twisted:cfg.Cuello.twisted,tilted:cfg.Cuello.tilted},
      trunk:{angle:t.angle,direction:t.direction||cfg.Tronco.direction,twisted:cfg.Tronco.twisted,tilted:cfg.Tronco.tilted},
      legs:{condition:cfg.Piernas.condition,knee_angle:l.angle},
      upper_arm:{angle:a.angle,direction:a.direction||cfg.Brazo.direction,shoulder_raised:cfg.Brazo.shoulder_raised,abducted:cfg.Brazo.abducted,supported:cfg.Brazo.supported},
      forearm:{angle:f.angle},
      wrist:{angle:w.angle,direction:w.direction||cfg.Muñeca.direction,deviated:cfg.Muñeca.deviated},
      load:{value:cfg.Carga.value,unit:cfg.Carga.unit},
      shock:cfg.Carga.shock,
      coupling:cfg.Acoplamiento.coupling,
      activity:{static:cfg.Actividad.static,repetitive:cfg.Actividad.repetitive,rapid_change:cfg.Actividad.rapid_change}
    };
  }

  function setScores(r){
    if(!scoreEls.length)return;
    if(!r){scoreEls.forEach(e=>e.textContent='—');lastResult=null;return;}
    scoreEls[0].textContent=r.score_a??'—';
    scoreEls[1].textContent=r.score_b??'—';
    scoreEls[2].textContent=r.score_c??'—';
    scoreEls[3].textContent=r.activity_score??'—';
    scoreEls[4].textContent=r.final_score??'—';
    const st=q('.status');if(st&&r.risk_level)st.textContent=`REBA ${r.final_score} · ${r.risk_level}`;
  }

  async function calculateLive(){
    const p=payload();
    if(!p){setScores(null);return;}
    try{
      const res=await fetch('/reba/api/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});
      const j=await res.json();
      if(!res.ok||j.status!=='success')throw new Error(j.message||'No se pudo calcular');
      lastResult=j.result;setScores(lastResult);
    }catch(err){console.error('REBA calculate:',err);}
  }

  function formData(){
    const inputs=qa('.person input');
    return {trabajador:inputs[0]?.value?.trim()||'',puesto:inputs[1]?.value?.trim()||'',area:inputs[2]?.value?.trim()||'',tarea:inputs[3]?.value?.trim()||'',evaluador:inputs[4]?.value?.trim()||'',fecha:inputs[5]?.value||''};
  }

  async function saveEvaluation(){
    const p=payload(),meta=formData();
    if(!meta.trabajador||!meta.puesto){alert('Completa Nombre del trabajador y Puesto / cargo antes de guardar.');return;}
    if(!p){alert('Faltan mediciones confirmadas en uno o más segmentos: Cuello, Tronco, Piernas, Brazo, Antebrazo y Muñeca.');return;}
    await calculateLive();
    if(!lastResult){alert('No fue posible calcular REBA. Revisa las mediciones.');return;}
    const photos={};
    Object.keys(store).forEach(seg=>{photos[seg]=(store[seg].photos||[]).map(ph=>({name:ph.name,measurements:ph.measurements.map(m=>({angle:m.angle,direction:m.direction,points:m.points}))}))});
    saveBtn.disabled=true;const old=saveBtn.textContent;saveBtn.textContent='Guardando…';
    try{
      const res=await fetch('/reba/nueva',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({meta,evaluation:p,result:lastResult,photos,settings:cfg})});
      const j=await res.json();
      if(!res.ok||j.status!=='success')throw new Error(j.message||'No se pudo guardar');
      saveBtn.textContent='✓ Evaluación guardada';
      const st=q('.status');if(st)st.textContent=`Guardada · Folio ${j.id} · REBA ${lastResult.final_score}`;
      setTimeout(()=>saveBtn.textContent=old,2500);
    }catch(err){alert('Error al guardar: '+err.message);saveBtn.textContent=old;}
    finally{saveBtn.disabled=false;}
  }

  if(saveBtn)saveBtn.addEventListener('click',saveEvaluation);
  qa('.step').forEach(b=>b.addEventListener('click',()=>setTimeout(()=>{segmentOptions(b.dataset.segment);calculateLive();},0)));
  const timer=setInterval(calculateLive,1000);
  window.addEventListener('beforeunload',()=>clearInterval(timer));
  segmentOptions(current||'Cuello');
  calculateLive();
})();
