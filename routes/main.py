from flask import Blueprint, render_template, request, redirect, session, jsonify, send_file
from functools import wraps
import json

bp_main = Blueprint('main', __name__)
DEMO_USERS = {'admin': 'password123', 'lydia': 'ergonometapp2025'}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session: return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@bp_main.route('/')
def index(): return redirect('/dashboard') if 'usuario' in session else redirect('/login')

@bp_main.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        usuario=request.form.get('usuario'); password=request.form.get('password')
        if usuario in DEMO_USERS and DEMO_USERS[usuario] == password:
            session['usuario']=usuario; return redirect('/dashboard')
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
def reportes(): return render_template('reportes.html', usuario=session.get('usuario'), evaluaciones=_evaluaciones())

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

@bp_main.route('/evaluaciones/<int:evaluation_id>/reporte')
@login_required
def evaluacion_reporte(evaluation_id):
    e=_evaluation_or_403(evaluation_id)
    if not e: return jsonify({'status':'error','message':'No autorizado'}),403
    payload,result=_json_data(e)
    return render_template('reporte_reba.html',e=e,payload=payload,result=result)

@bp_main.route('/evaluaciones/<int:evaluation_id>/pdf')
@login_required
def evaluacion_pdf(evaluation_id):
    e=_evaluation_or_403(evaluation_id)
    if not e: return jsonify({'status':'error','message':'No autorizado'}),403
    from services.reba_report import build_reba_pdf
    pdf=build_reba_pdf(e)
    return send_file(pdf,mimetype='application/pdf',as_attachment=True,download_name=f'RFRANYUTTI_REBA_{e.id:05d}.pdf')

@bp_main.route('/metodos')
@login_required
def metodos(): return jsonify({'métodos':[{'nombre':'REBA','url':'/reba/nueva'},{'nombre':'Ley SILLA','url':'/ley-silla/nueva'},{'nombre':'LEST','url':'/lest/nueva'},{'nombre':'Apéndice I','url':'/apendice-i/nueva'},{'nombre':'Apéndice II','url':'/apendice-ii/nueva'},{'nombre':'Kuorinka','url':'/cuestionario-nordico/nueva'}]})

@bp_main.route('/health')
def health(): return jsonify({'status':'ok','app':'ErgonometApp v2.0'})
