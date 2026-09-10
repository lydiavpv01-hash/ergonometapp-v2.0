from flask import Blueprint, render_template, request, redirect, session, jsonify, send_file
from functools import wraps
import json, re, unicodedata

bp_main = Blueprint('main', __name__)
DEMO_USERS = {'admin': 'password123', 'lydia': 'ergonometapp2025', 'jaquelin.garcia@rfranyutti.com.mx': '$user4RFJ4QG'}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session: return redirect('/login')
        session.permanent = True
        session.modified = True
        return f(*args, **kwargs)
    return decorated_function

@bp_main.route('/')
def index(): return redirect('/dashboard') if 'usuario' in session else redirect('/login')

@bp_main.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        usuario=request.form.get('usuario'); password=request.form.get('password')
        if usuario in DEMO_USERS and DEMO_USERS[usuario] == password:
            session.clear()
            session.permanent = True
            session['usuario']=usuario
            session.modified = True
            return redirect('/dashboard')
        return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')

@bp_main.route('/logout')
def logout(): session.clear(); return redirect('/login')

@bp_main.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html', usuario=session.get('usuario'))

def _evaluaciones():
    from models.reba_evaluation import RebaEvaluation
    return RebaEvaluation.query.filter_by(usuario=session.get('usuario','')).order_by(RebaEvaluation.created_at.desc()).all()

def _nom_evaluaciones():
    from models.generic_evaluation import GenericEvaluation
    rows=GenericEvaluation.query.filter_by(usuario=session.get('usuario','')).order_by(GenericEvaluation.created_at.desc()).all()
    return {
        'APENDICE_I':[e for e in rows if e.metodo=='APENDICE_I'],
        'APENDICE_II':[e for e in rows if e.metodo=='APENDICE_II'],
        'KUORINKA':[e for e in rows if e.metodo=='KUORINKA'],
    }

@bp_main.route('/evaluaciones')
@login_required
def evaluaciones_guardadas():
    return render_template('evaluaciones_guardadas.html', usuario=session.get('usuario'), evaluaciones=_evaluaciones(), nom=_nom_evaluaciones())

@bp_main.route('/reportes')
@login_required
def reportes(): return redirect('/evaluaciones')

def _evaluation_or_403(evaluation_id):
    from models.reba_evaluation import RebaEvaluation
    e=RebaEvaluation.query.get_or_404(evaluation_id)
    return e if e.usuario == session.get('usuario','') else None

def _json_data(e):
    try: payload=json.loads(e.payload_json or '{}')
    except Exception: payload={}
    try: result=json.loads(e.result_json or '{}')
    except Exception: result={}
    return payload,result

@bp_main.route('/evaluaciones/<int:evaluation_id>')
@login_required
def evaluacion_detalle(evaluation_id):
    e=_evaluation_or_403(evaluation_id)
    if not e: return jsonify({'status':'error','message':'No autorizado'}),403
    payload,result=_json_data(e)
    return render_template('evaluacion_detalle.html',usuario=session.get('usuario'),e=e,payload=payload,result=result)

@bp_main.route('/evaluaciones/nom/<int:evaluation_id>')
@login_required
def evaluacion_nom_detalle(evaluation_id):
    from models.generic_evaluation import GenericEvaluation
    e=GenericEvaluation.query.get_or_404(evaluation_id)
    if e.usuario != session.get('usuario',''):
        return jsonify({'status':'error','message':'No autorizado'}),403
    payload,result=_json_data(e)
    return render_template('evaluacion_nom_detalle.html',usuario=session.get('usuario'),e=e,payload=payload,result=result)

def _safe_key(text):
    text=unicodedata.normalize('NFD',str(text or '')).encode('ascii','ignore').decode('ascii').lower()
    return re.sub(r'(^_|_$)','',re.sub(r'[^a-z0-9]+','_',text))[:70]

def _risk_level(score):
    score=int(score or 0)
    if score>=21:return 'Muy Alto · Inaceptable'
    if score>=13:return 'Alto · Significativo'
    if score>=5:return 'Medio · Posible'
    return 'Bajo · Aceptable'

def _color_for(key,value,method='APENDICE_I'):
    if value is None:return ('','c-empty')
    try:v=float(value)
    except Exception:return ('','c-empty')
    if v==0:return ('Verde','c-verde')
    if key and ('peso' in key or key=='weight'):
        if v in (1,2,3,4):return ('Amarillo','c-amarillo')
        if v in (5,6):return ('Rojo','c-rojo')
        return ('Magenta','c-magenta')
    if method=='APENDICE_II':
        if v<=3:return ('Amarillo','c-amarillo')
        if v<=6:return ('Rojo','c-rojo')
        return ('Magenta','c-magenta')
    if v in (1,3,4):return ('Amarillo','c-amarillo')
    if v in (2,6):return ('Rojo','c-rojo')
    return ('Rojo','c-rojo')

def _snapshot_maps(payload):
    snap=payload.get('snapshot') or {}
    fields=snap.get('fields') or []
    sels=snap.get('selections') or []
    sel_by={s.get('factor',''):s for s in sels}
    field_by_name={f.get('name',''):f for f in fields if f.get('name')}
    uploads=payload.get('uploads') or []
    uploads_by={}
    for u in uploads: uploads_by.setdefault(u.get('field',''),[]).append(u)
    return fields,sel_by,field_by_name,uploads,uploads_by

def _generic_matrix(e,payload,result):
    fields,sel_by,field_by_name,uploads,uploads_by=_snapshot_maps(payload)
    meta=payload.get('meta') or {}
    field_values={f.get('label',''):f.get('value','') for f in fields}
    base_meta={
        'empresa':field_values.get('Empresa') or field_values.get('Empresa:') or '',
        'area':field_values.get('Área') or field_values.get('Area') or '',
        'subarea':field_values.get('Subárea') or field_values.get('Subarea') or '',
        'fecha':meta.get('fecha') or e.fecha or '',
        'evaluador':field_values.get('Evaluador') or '',
        'puesto':meta.get('puesto') or e.puesto or '',
        'trabajador':meta.get('trabajador') or e.trabajador or '',
        'actividad':field_values.get('Actividad') or field_values.get('Actividad / tarea') or '',
        'descripcion':field_values.get('Descripción de actividad') or field_values.get('Descripcion de actividad') or '',
    }
    if e.metodo=='APENDICE_I':
        labels=[
          ('Peso de la carga / frecuencia de transporte','ai2_peso','ai3_peso','ai4_peso'),
          ('Distancia horizontal entre las manos y la parte inferior de la espalda','ai2_distancia','ai3_distancia','ai4_distancia'),
          ('Región de levantamiento vertical','ai2_vertical',None,'ai4_vertical'),
          ('Torsión y flexión lateral del torso / Carga asimétrica sobre el torso','ai2_torsion','ai3_asimetria','ai4_torsion'),
          ('Restricciones posturales','ai2_restriccion','ai3_restriccion','ai4_restriccion'),
          ('Acoplamiento mano-carga (elementos de sujeción)','ai2_agarre','ai3_agarre','ai4_agarre'),
          ('Superficie de trabajo','ai2_superficie','ai3_superficie','ai4_superficie'),
          ('Otros factores ambientales','ai2_ambiente','ai3_ambiente','ai4_ambiente'),
          ('Distancia de transporte',None,'ai3_distancia_transporte',None),
          ('Obstáculos en la ruta',None,'ai3_obstaculos',None),
          ('Comunicación, coordinación y control',None,None,'ai4_coordinacion')]
        values=(payload.get('evaluation') or {}).get('values') or {}
        rows=[]; just=[]
        for label,k2,k3,k4 in labels:
            cells=[]
            for sec,key in [('ai2',k2),('ai3',k3),('ai4',k4)]:
                if not key: cells.append({'color':'','color_class':'c-empty','value':None,'condition':''}); continue
                val=(values.get(sec) or {}).get(key)
                sel=sel_by.get(key) or {}
                color,cls=_color_for(key,val,'APENDICE_I')
                cells.append({'color':color,'color_class':cls,'value':val,'condition':sel.get('selection','')})
                sk=_safe_key(key); jf=field_by_name.get('justificacion_'+sk) or {}
                photos=uploads_by.get('evidencia_'+sk,[])
                if val is not None or sel or jf.get('value') or photos:
                    just.append({'title':label+' · '+sec.upper(),'condition':sel.get('selection',''),'value':val,'justification':jf.get('value',''),'photos':photos})
            rows.append({'label':label,'cells':cells})
        scores=(payload.get('evaluation') or {}).get('scores') or {}
        return {'kind':'APENDICE_I','title':'EVALUACIÓN DE RIESGO (LEVANTAMIENTO/DESCENSO, TRANSPORTE INDIVIDUAL Y EN EQUIPO)','folio':f'NOM036-I-{e.id:05d}','meta':base_meta,'photos':uploads,'factor_rows':rows,'scores':{'ai2':scores.get('ai2',0),'ai3':scores.get('ai3',0),'ai4':scores.get('ai4',0)},'levels':{'ai2':_risk_level(scores.get('ai2',0)),'ai3':_risk_level(scores.get('ai3',0)),'ai4':_risk_level(scores.get('ai4',0))},'justification_rows':just}
    values=(payload.get('evaluation') or {}).get('values') or {}
    factor_labels={'weight':'Peso / tipo de desplazamiento','postura':'Postura','agarre':'Acoplamiento mano-carga','patron':'Patrón de trabajo','distancia':'Distancia por viaje','equipoCond':'Condición del equipo auxiliar','superficie':'Superficie de trabajo','obstaculos':'Obstáculos','otros':'Otros factores'}
    factors=[]; just=[]
    for key,label in factor_labels.items():
        val=values.get(key)
        sel=sel_by.get(key) or {}
        color,cls=_color_for(key,val,'APENDICE_II')
        sk=_safe_key(key); jf=field_by_name.get('justificacion_'+sk) or {}
        photos=uploads_by.get('evidencia_'+sk,[])
        factors.append({'title':label,'condition':sel.get('selection','Valor automático según datos capturados' if key=='weight' else ''),'value':val,'color':color,'color_class':cls,'justification':jf.get('value',''),'photos':photos})
        if val is not None or sel or jf.get('value') or photos:
            just.append({'title':label,'condition':sel.get('selection','Valor automático según datos capturados' if key=='weight' else ''),'value':val,'justification':jf.get('value',''),'photos':photos})
    return {'kind':'APENDICE_II','title':'EVALUACIÓN DE RIESGO · EMPUJE, JALADO Y ARRASTRE · APÉNDICE II NOM-036-1','folio':f'NOM036-II-{e.id:05d}','meta':base_meta,'photos':uploads,'factors':factors,'final_score':e.final_score,'risk_level':e.risk_level,'justification_rows':just}

def _reba_matrix(e,payload,result):
    ev=payload.get('evaluation') or {}; photos=[]
    for seg,items in (payload.get('photos') or {}).items():
        for p in items or []:
            if p.get('src'): photos.append({'name':p.get('name',seg),'data':p.get('src'),'field':seg})
    labels={'neck':'Cuello','trunk':'Tronco','legs':'Piernas','upper_arm':'Brazo','forearm':'Antebrazo','wrist':'Muñeca'}
    factors=[]
    for key,title in labels.items():
        s=(result.get('segments') or {}).get(key,{})
        if key=='legs': cond=f"{s.get('condition','')} · rodilla {s.get('knee_angle','—')}°"
        else: cond=f"{s.get('angle','—')}° {s.get('direction','')} · rango {s.get('range','')}"
        score=s.get('final_score',s.get('score','—'))
        factors.append({'title':title,'condition':cond,'score':score})
    factors += [
        {'title':'Fuerza / Carga','condition':f"{(result.get('load_data') or {}).get('value','—')} {(result.get('load_data') or {}).get('unit','')}" ,'score':result.get('load_score','—')},
        {'title':'Acoplamiento','condition':(result.get('coupling_data') or {}).get('type','—'),'score':result.get('coupling_score','—')},
        {'title':'Actividad','condition':'Factores adicionales de actividad','score':result.get('activity_score','—')}]
    meta=payload.get('meta') or {}
    return {'kind':'REBA','title':'MATRIZ DE EVALUACIÓN REBA','folio':f'REBA-{e.id:05d}','meta':{'empresa':'','area':e.area or meta.get('area',''),'subarea':'','fecha':e.fecha or meta.get('fecha',''),'evaluador':e.evaluador or meta.get('evaluador',''),'puesto':e.puesto,'trabajador':e.trabajador,'actividad':e.tarea or meta.get('tarea',''),'tarea':e.tarea or meta.get('tarea',''),'descripcion':''},'photos':photos,'reba_factors':factors,'score_a':e.score_a,'score_b':e.score_b,'score_c':e.score_c,'activity_score':e.activity_score,'final_score':e.final_score,'risk_level':e.risk_level,'justification_rows':[]}

@bp_main.route('/evaluaciones/<int:evaluation_id>/matriz')
@login_required
def evaluacion_matriz(evaluation_id):
    e=_evaluation_or_403(evaluation_id)
    if not e:return jsonify({'status':'error','message':'No autorizado'}),403
    payload,result=_json_data(e)
    return render_template('matriz_imprimible.html',matrix=_reba_matrix(e,payload,result))

@bp_main.route('/evaluaciones/nom/<int:evaluation_id>/matriz')
@login_required
def evaluacion_nom_matriz(evaluation_id):
    from models.generic_evaluation import GenericEvaluation
    e=GenericEvaluation.query.get_or_404(evaluation_id)
    if e.usuario != session.get('usuario',''):return jsonify({'status':'error','message':'No autorizado'}),403
    if e.metodo not in ('APENDICE_I','APENDICE_II'):return redirect(f'/evaluaciones/nom/{e.id}')
    payload,result=_json_data(e)
    return render_template('matriz_imprimible.html',matrix=_generic_matrix(e,payload,result))

# Se conservan estas rutas por compatibilidad con enlaces antiguos, pero la interfaz nueva usa matrices imprimibles.
@bp_main.route('/evaluaciones/<int:evaluation_id>/reporte')
@login_required
def evaluacion_reporte(evaluation_id): return redirect(f'/evaluaciones/{evaluation_id}/matriz')

@bp_main.route('/evaluaciones/<int:evaluation_id>/pdf')
@login_required
def evaluacion_pdf(evaluation_id): return redirect(f'/evaluaciones/{evaluation_id}/matriz')

@bp_main.route('/metodos')
@login_required
def metodos(): return jsonify({'métodos':[{'nombre':'REBA','url':'/reba/nueva'},{'nombre':'Ley Silla','url':'/ley-silla/nueva'},{'nombre':'LEST','url':'/lest/nueva'},{'nombre':'Apéndice I','url':'/apendice-i/nueva'},{'nombre':'Apéndice II','url':'/apendice-ii/nueva'},{'nombre':'Kuorinka','url':'/cuestionario-nordico/nueva'}]})
