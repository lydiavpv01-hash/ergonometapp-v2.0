(()=>{
  const q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)];
  const scoreEls=qa('.results .result b');
  const saveBtn=qa('.top-actions .primary').find(b=>b.textContent.includes('Guardar'));
  const options=q('.options');
  let lastResult=null;
  const optionState={
    Cuello:{direction:'flexion',neckTwisted:false,neckTilted:false},
    Tronco:{direction:'flexion',trunkTwisted:false,trunkTilted:false},
    Piernas:{legsCondition:'both_supported'},
    Brazo:{direction:'flexion',armRaised:false,armAbducted:false,armSupported:false},
    Antebrazo:{},
    Muñeca:{direction:'flexion',wristDeviated:false},
    Carga:{loadValue:0,loadUnit:'kg',loadShock:false},
    Acoplamiento:{coupling:'regular'},
    Actividad:{activityStatic:false,activityRepetitive:false,activityRapid:false}
  };

  function lastMeasurement(segment){
    const bucket=store?.[segment];
    if(!bucket || !bucket.photos?.length) return null;
    const activePhoto=bucket.photos.find(p=>p.id===bucket.active) || bucket.photos.at(-1);
    if(activePhoto?.measurements?.length) return activePhoto.measurements.at(-1);
    for(let i=bucket.photos.length-1;i>=0;i--){
      const ms=bucket.photos[i].measurements||[];
      if(ms.length) return ms.at(-1);
    }
    return null;
  }

  function snapshotOptions(seg){
    const st=optionState[seg]||{};
    options?.querySelectorAll('input,select').forEach(el=>{
      if(el.type==='radio'){ if(el.checked) st[el.name]=el.value; }
      else if(el.type==='checkbox') st[el.id]=el.checked;
      else st[el.id]=el.value;
    });
  }
  function restoreOptions(seg){
    const st=optionState[seg]||{};
    options?.querySelectorAll('input,select').forEach(el=>{
      if(el.type==='radio') el.checked=st[el.name]===el.value;
      else if(el.type==='checkbox' && el.id in st) el.checked=!!st[el.id];
      else if(el.id in st) el.value=st[el.id];
    });
  }
  function controlState(){
    const s=optionState;
    return {
      neck:{twisted:!!s.Cuello.neckTwisted,tilted:!!s.Cuello.neckTilted},
      trunk:{twisted:!!s.Tronco.trunkTwisted,tilted:!!s.Tronco.trunkTilted},
      legs:{condition:s.Piernas.legsCondition||'both_supported'},
      upper_arm:{shoulder_raised:!!s.Brazo.armRaised,abducted:!!s.Brazo.armAbducted,supported:!!s.Brazo.armSupported},
      wrist:{deviated:!!s.Muñeca.wristDeviated},
      load:{value:Number(s.Carga.loadValue||0),unit:s.Carga.loadUnit||'kg',shock:!!s.Carga.loadShock},
      coupling:s.Acoplamiento.coupling||'regular',
      activity:{static:!!s.Actividad.activityStatic,repetitive:!!s.Actividad.activityRepetitive,rapid_change:!!s.Actividad.activityRapid}
    };
  }

  function segmentOptions(seg){
    if(!options) return;
    const head='<div class="card-head" style="margin:-18px -18px 8px"><h2>Ajustes del segmento</h2><small>Selección técnica</small></div>';
    const radio=(name,val,label)=>`<div class="option"><label><input type="radio" name="${name}" value="${val}"> ${label}</label></div>`;
    const check=(id,label)=>`<div class="option"><label><input id="${id}" type="checkbox"> ${label}</label></div>`;
    let body='';
    if(seg==='Cuello') body=radio('direction','flexion','Flexión')+radio('direction','extension','Extensión')+check('neckTwisted','Cuello torcido (+1)')+check('neckTilted','Inclinación lateral (+1)');
    else if(seg==='Tronco') body=radio('direction','flexion','Flexión')+radio('direction','extension','Extensión')+radio('direction','neutral','Neutral')+check('trunkTwisted','Tronco torcido (+1)')+check('trunkTilted','Inclinación lateral (+1)');
    else if(seg==='Piernas') body=`<div class="option"><label>Condición de apoyo</label><select id="legsCondition" style="width:100%;margin-top:8px;padding:9px;border:1px solid #dfe4dd;border-radius:7px"><option value="both_supported">Ambas piernas apoyadas</option><option value="unilateral">Apoyo unilateral / una pierna levantada</option><option value="unstable">Postura inestable</option></select></div><div class="option"><span style="font-size:11px;color:#68716b">El ángulo confirmado se usa como flexión de rodilla.</span></div>`;
    else if(seg==='Brazo') body=radio('direction','flexion','Flexión')+radio('direction','extension','Extensión')+radio('direction','neutral','Neutral')+check('armRaised','Hombro elevado (+1)')+check('armAbducted','Brazo abducido (+1)')+check('armSupported','Brazo apoyado (-1)');
    else if(seg==='Antebrazo') body='<div class="option"><span style="font-size:11px;color:#68716b">El puntaje se obtiene directamente del ángulo confirmado.</span></div>';
    else if(seg==='Muñeca') body=radio('direction','flexion','Flexión')+radio('direction','extension','Extensión')+radio('direction','neutral','Neutral')+check('wristDeviated','Desviación / torsión de muñeca (+1)');
    else if(seg==='Carga') body=`<div class="option"><label>Carga manipulada</label><div style="display:grid;grid-template-columns:1fr 90px;gap:8px;margin-top:8px"><input id="loadValue" type="number" min="0" step="0.1" style="padding:9px;border:1px solid #dfe4dd;border-radius:7px"><select id="loadUnit" style="padding:9px;border:1px solid #dfe4dd;border-radius:7px"><option value="kg">kg</option><option value="lb">lb</option></select></div></div>${check('loadShock','Carga aplicada con golpe o fuerza brusca (+1)')}`;
    else if(seg==='Acoplamiento') body=`<div class="option"><label>Calidad del acoplamiento</label><select id="coupling" style="width:100%;margin-top:8px;padding:9px;border:1px solid #dfe4dd;border-radius:7px"><option value="good">Bueno</option><option value="regular">Regular</option><option value="poor">Malo</option><option value="unacceptable">Inaceptable</option></select></div>`;
    else if(seg==='Actividad') body=check('activityStatic','Postura estática prolongada (+1)')+check('activityRepetitive','Actividad repetitiva (+1)')+check('activityRapid','Cambios rápidos o inestables (+1)');
    options.innerHTML=head+body;
    restoreOptions(seg);
    qa('input[name="direction"]').forEach(x=>x.onchange=()=>{snapshotOptions(seg);try{renderGuides()}catch{};calculateLive()});
    options.querySelectorAll('input,select').forEach(x=>x.addEventListener('change',()=>{snapshotOptions(seg);calculateLive()}));
  }

  function payload(){
    snapshotOptions(current);
    const n=lastMeasurement('Cuello'), t=lastMeasurement('Tronco'), l=lastMeasurement('Piernas'), a=lastMeasurement('Brazo'), f=lastMeasurement('Antebrazo'), w=lastMeasurement('Muñeca');
    if(!n||!t||!l||!a||!f||!w) return null;
    const s=controlState();
    return {
      neck:{angle:n.angle,direction:n.direction||optionState.Cuello.direction||'flexion',twisted:s.neck.twisted,tilted:s.neck.tilted},
      trunk:{angle:t.angle,direction:t.direction||optionState.Tronco.direction||'flexion',twisted:s.trunk.twisted,tilted:s.trunk.tilted},
      legs:{condition:s.legs.condition,knee_angle:l.angle},
      upper_arm:{angle:a.angle,direction:a.direction||optionState.Brazo.direction||'flexion',shoulder_raised:s.upper_arm.shoulder_raised,abducted:s.upper_arm.abducted,supported:s.upper_arm.supported},
      forearm:{angle:f.angle},
      wrist:{angle:w.angle,direction:w.direction||optionState.Muñeca.direction||'flexion',deviated:s.wrist.deviated},
      load:{value:s.load.value,unit:s.load.unit},shock:s.load.shock,coupling:s.coupling,activity:s.activity
    };
  }
  function setScores(r){if(!scoreEls.length)return;if(!r){scoreEls.forEach(e=>e.textContent='—');return}scoreEls[0].textContent=r.score_a??'—';scoreEls[1].textContent=r.score_b??'—';scoreEls[2].textContent=r.score_c??'—';scoreEls[3].textContent=r.activity_score??'—';scoreEls[4].textContent=r.final_score??'—';const st=q('.status');if(st&&r.risk_level)st.textContent=`REBA ${r.final_score} · ${r.risk_level}`}
  async function calculateLive(){const p=payload();if(!p){setScores(null);return}try{const res=await fetch('/reba/api/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});const j=await res.json();if(!res.ok||j.status!=='success')throw new Error(j.message||'No se pudo calcular');lastResult=j.result;setScores(lastResult)}catch(err){console.error(err)}}
  function formData(){const inputs=qa('.person input');return{trabajador:inputs[0]?.value?.trim()||'',puesto:inputs[1]?.value?.trim()||'',area:inputs[2]?.value?.trim()||'',tarea:inputs[3]?.value?.trim()||'',evaluador:inputs[4]?.value?.trim()||'',fecha:inputs[5]?.value||''}}
  async function saveEvaluation(){snapshotOptions(current);const p=payload(),meta=formData();if(!meta.trabajador||!meta.puesto){alert('Completa Nombre del trabajador y Puesto / cargo antes de guardar.');return}if(!p){alert('Faltan mediciones confirmadas en uno o más segmentos: Cuello, Tronco, Piernas, Brazo, Antebrazo y Muñeca.');return}if(!lastResult)await calculateLive();if(!lastResult){alert('No fue posible calcular REBA. Revisa las mediciones.');return}
    const photos={};Object.keys(store).forEach(seg=>{photos[seg]=(store[seg].photos||[]).map(ph=>({name:ph.name,src:ph.src,measurements:ph.measurements.map(m=>({angle:m.angle,direction:m.direction,points:m.points}))}))});
    saveBtn.disabled=true;const old=saveBtn.textContent;saveBtn.textContent='Guardando…';try{const res=await fetch('/reba/nueva',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({meta,evaluation:p,result:lastResult,photos,options:optionState})});const j=await res.json();if(!res.ok||j.status!=='success')throw new Error(j.message||'No se pudo guardar');saveBtn.textContent='✓ Evaluación guardada';const st=q('.status');if(st)st.textContent=`Guardada · Folio ${j.id} · REBA ${lastResult.final_score}`;setTimeout(()=>saveBtn.textContent=old,2500)}catch(err){alert('Error al guardar: '+err.message);saveBtn.textContent=old}finally{saveBtn.disabled=false}}
  if(saveBtn)saveBtn.addEventListener('click',saveEvaluation);
  qa('.step').forEach(b=>b.addEventListener('click',()=>{snapshotOptions(current);setTimeout(()=>{segmentOptions(b.dataset.segment);calculateLive()},0)}));
  const timer=setInterval(calculateLive,900);window.addEventListener('beforeunload',()=>clearInterval(timer));segmentOptions(current||'Cuello');calculateLive();
})();
