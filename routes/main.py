from flask import Blueprint, render_template, jsonify

bp_main = Blueprint('main', __name__)

@bp_main.route('/')
def index():
    """Página principal"""
    return jsonify({
        'mensaje': 'Bienvenido a ErgonometApp v2.0',
        'versión': '2.0',
        'métodos': ['REBA', 'Ley SILLA', 'LEST', 'Apéndice I', 'Apéndice II', 'Kuorinka'],
        'endpoints': {
            'dashboard': '/dashboard',
            'reba': '/reba/nueva',
            'ley_silla': '/ley-silla/nueva',
            'lest': '/lest/nueva',
            'apendice_i': '/apendice-i/nueva',
            'apendice_ii': '/apendice-ii/nueva',
            'kuorinka': '/cuestionario-nordico/nueva'
        }
    })

@bp_main.route('/metodos')
def metodos():
    """Listar métodos disponibles"""
    return jsonify({
        'métodos': [
            {'nombre': 'REBA', 'url': '/reba/nueva'},
            {'nombre': 'Ley SILLA', 'url': '/ley-silla/nueva'},
            {'nombre': 'LEST', 'url': '/lest/nueva'},
            {'nombre': 'Apéndice I', 'url': '/apendice-i/nueva'},
            {'nombre': 'Apéndice II', 'url': '/apendice-ii/nueva'},
            {'nombre': 'Cuestionario Nórdico', 'url': '/cuestionario-nordico/nueva'}
        ]
    })

@bp_main.route('/health')
def health():
    """Health check para Render"""
    return jsonify({'status': 'ok', 'app': 'ErgonometApp v2.0'})
