from flask import Blueprint, render_template, request, jsonify, session, redirect
from functools import wraps

bp_reba = Blueprint('reba', __name__, url_prefix='/reba')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@bp_reba.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    """Formulario REBA completo"""
    if request.method == 'POST':
        # Aquí iría la lógica para procesar la evaluación
        # Por ahora simplemente retorna un JSON
        return jsonify({
            'status': 'success',
            'mensaje': 'Evaluación REBA guardada',
            'puntuacion': 0
        })
    
    return render_template('reba_v3_kinovea.html')

@bp_reba.route('/resultado/<int:id>')
@login_required
def resultado(id):
    """Muestra el resultado de una evaluación REBA"""
    return jsonify({
        'id': id,
        'metodo': 'REBA',
        'puntuacion': 0,
        'resultado': 'en desarrollo'
    })
