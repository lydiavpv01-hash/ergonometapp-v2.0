from flask import Blueprint, render_template, request, redirect, session, jsonify
from functools import wraps

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
    """Redirigir a login o dashboard según sesión"""
    if 'usuario' in session:
        return redirect('/dashboard')
    return redirect('/login')

@bp_main.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        
        if usuario in DEMO_USERS and DEMO_USERS[usuario] == password:
            session['usuario'] = usuario
            return redirect('/dashboard')
        else:
            error = 'Usuario o contraseña incorrectos'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@bp_main.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect('/login')

@bp_main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html', usuario=session.get('usuario'))

@bp_main.route('/metodos')
@login_required
def metodos():
    """Listar métodos disponibles"""
    return jsonify({
        'métodos': [
            {'nombre': 'REBA', 'url': '/reba/nueva'},
            {'nombre': 'Ley SILLA', 'url': '/ley-silla/nueva'},
            {'nombre': 'LEST', 'url': '/lest/nueva'},
            {'nombre': 'Apéndice I', 'url': '/apendice-i/nueva'},
            {'nombre': 'Apéndice II', 'url': '/apendice-ii/nueva'},
            {'nombre': 'Kuorinka', 'url': '/cuestionario-nordico/nueva'}
        ]
    })

@bp_main.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'app': 'ErgonometApp v2.0'})
