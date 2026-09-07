from flask import Blueprint, render_template, request, jsonify, session, redirect
from functools import wraps
from models.reba_calculator import calculate_reba

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
    """Espacio profesional para una nueva evaluación REBA."""
    if request.method == 'POST':
        return jsonify({'status': 'success', 'mensaje': 'Evaluación REBA guardada', 'puntuacion': 0})
    return render_template('reba_workspace.html')

@bp_reba.route('/medicion', methods=['GET'])
@login_required
def medicion():
    return render_template('reba_medicion_v1.html')

@bp_reba.route('/medicion_v2', methods=['GET'])
@login_required
def medicion_v2():
    return render_template('reba_medicion_v2.html')

@bp_reba.route('/test', methods=['GET'])
def test():
    return render_template('test_medidor_angular.html')

@bp_reba.route('/api/calculate', methods=['POST'])
@login_required
def api_calculate():
    """API central para cálculo REBA."""
    try:
        data = request.get_json()
        result = calculate_reba(data)
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp_reba.route('/resultado/<int:id>')
@login_required
def resultado(id):
    return jsonify({'id': id, 'metodo': 'REBA', 'puntuacion': 0, 'resultado': 'en desarrollo'})
