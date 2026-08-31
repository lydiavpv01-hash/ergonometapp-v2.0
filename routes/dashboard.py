from flask import Blueprint, jsonify, render_template

bp_dashboard = Blueprint('dashboard', __name__)

@bp_dashboard.route('/dashboard')
def dashboard():
    return jsonify({
        'dashboard': 'ErgonometApp v2.0',
        'total_evaluaciones': 0,
        'métodos': ['REBA', 'Ley SILLA', 'LEST', 'Apéndice I', 'Apéndice II', 'Kuorinka']
    })
