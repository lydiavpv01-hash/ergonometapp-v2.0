from flask import Blueprint, render_template, request, redirect, session, jsonify
from functools import wraps
import json

bp_main = Blueprint('main', __name__)

# Usuarios demo
DEMO_USERS = {
    'admin': 'password123',
    'lydia': 'ergonometapp2025'
}

def login_required(f):
    """Decorador para requerir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@bp_main.route('/')
def index():
    if 'usuario' in session:
        return redirect('/dashboard')
    return redirect('/login')

@bp_main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        if usuario in DEMO_USERS and DEMO_USERS[usuario] == password:
            session['usuario'] = usuario
            return redirect('/dashboard')
        error = 'Usuario o contraseña incorrectos'
        return render_template('login.html', error=error)
    return render_template('login.html')

@bp_main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@bp_main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', usuario=session.get('usuario'))

@bp_main.route('/evaluaciones')
@login_required
def evaluaciones_guardadas():
    from models.reba_evaluation import RebaEvaluation
    usuario = session.get('usuario', '')
    evaluaciones = (RebaEvaluation.query
                    .filter_by(usuario=usuario)
                    .order_by(RebaEvaluation.created_at.desc())
                    .all())
    return render_template('evaluaciones_guardadas.html', usuario=usuario, evaluaciones=evaluaciones)

@bp_main.route('/evaluaciones/<int:evaluation_id>')
@login_required
def evaluacion_detalle(evaluation_id):
    from models.reba_evaluation import RebaEvaluation
    e = RebaEvaluation.query.get_or_404(evaluation_id)
    if e.usuario != session.get('usuario', ''):
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    try:
        payload = json.loads(e.payload_json or '{}')
    except Exception:
        payload = {}
    try:
        result = json.loads(e.result_json or '{}')
    except Exception:
        result = {}
    return render_template('evaluacion_detalle.html', usuario=session.get('usuario'), e=e, payload=payload, result=result)

@bp_main.route('/metodos')
@login_required
def metodos():
    return jsonify({'métodos': [
        {'nombre': 'REBA', 'url': '/reba/nueva'},
        {'nombre': 'Ley SILLA', 'url': '/ley-silla/nueva'},
        {'nombre': 'LEST', 'url': '/lest/nueva'},
        {'nombre': 'Apéndice I', 'url': '/apendice-i/nueva'},
        {'nombre': 'Apéndice II', 'url': '/apendice-ii/nueva'},
        {'nombre': 'Kuorinka', 'url': '/cuestionario-nordico/nueva'}
    ]})

@bp_main.route('/health')
def health():
    return jsonify({'status': 'ok', 'app': 'ErgonometApp v2.0'})
