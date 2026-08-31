"""
routes/dashboard.py - Dashboard principal
"""

from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import func
from datetime import datetime, timedelta

bp_dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp_dashboard.route('/')
def dashboard():
    """Dashboard principal"""
    # Aquí irían consultas a BD reales
    # Por ahora retorna template con datos de ejemplo
    return render_template('dashboard.html')


@bp_dashboard.route('/api/datos')
def api_datos():
    """API para obtener datos del dashboard"""
    datos = {
        'total_evaluaciones': 42,
        'riesgo_bajo': 28,
        'riesgo_moderado': 10,
        'riesgo_alto': 4,
        'por_metodo': {
            'REBA': 15,
            'Ley SILLA': 8,
            'LEST': 6,
            'Apéndice I': 7,
            'Apéndice II': 4,
            'Kuorinka': 2
        }
    }
    return jsonify(datos)


@bp_dashboard.route('/api/graficos/metodos')
def grafico_metodos():
    """Gráfico de evaluaciones por método"""
    return jsonify({
        'labels': ['REBA', 'Ley SILLA', 'LEST', 'Apéndice I', 'Apéndice II', 'Kuorinka'],
        'data': [15, 8, 6, 7, 4, 2]
    })


@bp_dashboard.route('/exportar/pdf')
def exportar_pdf():
    """Exportar dashboard a PDF"""
    return {'status': 'ok', 'mensaje': 'PDF generado'}


@bp_dashboard.route('/exportar/excel')
def exportar_excel():
    """Exportar datos a Excel"""
    return {'status': 'ok', 'mensaje': 'Excel generado'}
