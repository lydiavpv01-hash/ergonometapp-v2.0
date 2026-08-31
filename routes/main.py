"""
routes/main.py - Rutas principales
"""

from flask import Blueprint, render_template, redirect, url_for

bp_main = Blueprint('main', __name__)


@bp_main.route('/')
@bp_main.route('/index')
def index():
    """Página principal"""
    return render_template('index.html')


@bp_main.route('/metodos')
def listar_metodos():
    """Listar todos los métodos disponibles"""
    metodos = [
        {
            'id': 'reba',
            'nombre': 'REBA',
            'descripcion': 'Rapid Entire Body Assessment',
            'pasos': 5,
            'icon': '🏃'
        },
        {
            'id': 'ley_silla',
            'nombre': 'Ley SILLA',
            'descripcion': 'Evaluación de Bipedestación',
            'pasos': 3,
            'icon': '🪑'
        },
        {
            'id': 'lest',
            'nombre': 'LEST',
            'descripcion': 'List of Ergonomic Tasks',
            'pasos': 4,
            'icon': '📋'
        },
        {
            'id': 'apendice_i',
            'nombre': 'Apéndice I',
            'descripcion': 'Levantamiento de Cargas',
            'pasos': 3,
            'icon': '💪'
        },
        {
            'id': 'apendice_ii',
            'nombre': 'Apéndice II',
            'descripcion': 'Empuje y Arrastre',
            'pasos': 3,
            'icon': '🚀'
        },
        {
            'id': 'kuorinka',
            'nombre': 'Cuestionario Nórdico',
            'descripcion': 'Síntomas Musculoesqueléticos',
            'pasos': 2,
            'icon': '🫀'
        }
    ]
    
    return render_template('metodos.html', metodos=metodos)


@bp_main.route('/trabajadores')
def listar_trabajadores():
    """Listar trabajadores"""
    return render_template('trabajadores.html')


@bp_main.route('/trabajadores/nuevo')
def nuevo_trabajador():
    """Crear nuevo trabajador"""
    return render_template('trabajador_nuevo.html')


@bp_main.route('/help')
def ayuda():
    """Página de ayuda"""
    return render_template('help.html')
