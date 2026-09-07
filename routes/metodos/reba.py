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
    """Formulario REBA completo"""
    if request.method == 'POST':
        # Aquí iría la lógica para procesar la evaluación
        # Por ahora simplemente retorna un JSON
        return jsonify({
            'status': 'success',
            'mensaje': 'Evaluación REBA guardada',
            'puntuacion': 0
        })
    
    return render_template('reba_v5_pdf_profesional.html')

@bp_reba.route('/medicion', methods=['GET'])
@login_required
def medicion():
    """Herramienta de medición angular - FASE 1"""
    return render_template('reba_medicion_v1.html')

@bp_reba.route('/medicion_v2', methods=['GET'])
@login_required
def medicion_v2():
    """Interfaz guiada REBA FASE 2 - 8 pasos con cálculo integrado"""
    return render_template('reba_medicion_v2.html')

@bp_reba.route('/test', methods=['GET'])
def test():
    """Página de pruebas del cálculo angular (sin login requerido para desarrollo)"""
    return render_template('test_medidor_angular.html')

@bp_reba.route('/api/calculate', methods=['POST'])
@login_required
def api_calculate():
    """API para calcular REBA - Recibe datos completos y retorna resultado estructurado"""
    try:
        data = request.get_json()
        
        # Llamar a la función central de cálculo
        result = calculate_reba(data)
        
        return jsonify({
            'status': 'success',
            'result': result
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

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
