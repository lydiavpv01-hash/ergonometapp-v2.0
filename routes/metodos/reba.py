from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import json

from app import db
from models.reba_calculator import calculate_reba
from models.reba_evaluation import RebaEvaluation

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
        try:
            data = request.get_json(silent=True) or {}
            meta = data.get('meta') or {}
            evaluation = data.get('evaluation') or {}
            result = data.get('result') or {}

            if not meta.get('trabajador') or not meta.get('puesto'):
                return jsonify({'status': 'error', 'message': 'Trabajador y puesto son obligatorios'}), 400
            if not evaluation or not result:
                return jsonify({'status': 'error', 'message': 'La evaluación debe estar calculada antes de guardar'}), 400

            row = RebaEvaluation(
                usuario=session.get('usuario', ''),
                trabajador=meta.get('trabajador', ''),
                puesto=meta.get('puesto', ''),
                area=meta.get('area', ''),
                tarea=meta.get('tarea', ''),
                evaluador=meta.get('evaluador', ''),
                fecha=meta.get('fecha', ''),
                score_a=result.get('score_a'),
                score_b=result.get('score_b'),
                score_c=result.get('score_c'),
                activity_score=result.get('activity_score'),
                final_score=result.get('final_score'),
                risk_level=result.get('risk_level', ''),
                payload_json=json.dumps(data, ensure_ascii=False),
                result_json=json.dumps(result, ensure_ascii=False),
            )
            db.session.add(row)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'mensaje': 'Evaluación REBA guardada',
                'id': row.id,
                'puntuacion': row.final_score,
            })
        except Exception as exc:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    html = render_template('reba_workspace.html')
    script = f'<script src="{url_for("static", filename="js/reba_workspace_functional.js")}?v=1"></script>'
    return html.replace('</body>', script + '</body>')


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
    row = RebaEvaluation.query.get_or_404(id)
    if row.usuario != session.get('usuario', ''):
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
    return jsonify({
        'id': row.id,
        'metodo': 'REBA',
        'puntuacion': row.final_score,
        'riesgo': row.risk_level,
        'trabajador': row.trabajador,
        'puesto': row.puesto,
        'resultado': json.loads(row.result_json),
    })
