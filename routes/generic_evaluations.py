from flask import Blueprint, request, jsonify, session, redirect, send_file
from functools import wraps
import json
from app import db
from models.generic_evaluation import GenericEvaluation

bp_generic_evaluations = Blueprint('generic_evaluations', __name__, url_prefix='/api/evaluaciones')


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({'status':'error','message':'Sesión no válida'}), 401
        return f(*args, **kwargs)
    return wrapped


@bp_generic_evaluations.route('', methods=['POST'])
@login_required
def guardar():
    try:
        data = request.get_json(silent=True) or {}
        metodo = (data.get('metodo') or '').strip()
        meta = data.get('meta') or {}
        result = data.get('result') or {}
        if metodo not in ('APENDICE_I','APENDICE_II','KUORINKA'):
            return jsonify({'status':'error','message':'Método no soportado'}), 400
        trabajador = (meta.get('trabajador') or '').strip()
        puesto = (meta.get('puesto') or '').strip()
        if not trabajador:
            trabajador = 'Grupo / trabajador no especificado'
        if not puesto:
            puesto = 'Puesto no especificado'
        row = GenericEvaluation(
            usuario=session.get('usuario',''),
            metodo=metodo,
            trabajador=trabajador,
            puesto=puesto,
            fecha=meta.get('fecha') or '',
            final_score=result.get('final_score'),
            risk_level=result.get('risk_level') or result.get('summary') or '',
            payload_json=json.dumps(data, ensure_ascii=False),
            result_json=json.dumps(result, ensure_ascii=False),
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({'status':'success','id':row.id,'mensaje':'Evaluación guardada correctamente'})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'status':'error','message':str(exc)}), 500


@bp_generic_evaluations.route('/<int:evaluation_id>/excel', methods=['GET'])
@login_required
def descargar_excel(evaluation_id):
    """Descarga la matriz cliente ya llenada con los datos guardados.

    El Excel es únicamente una salida documental: reutiliza los resultados
    persistidos y no vuelve a ejecutar ni modifica el motor de cálculo.
    """
    row = GenericEvaluation.query.get_or_404(evaluation_id)
    if row.usuario != session.get('usuario',''):
        return jsonify({'status':'error','message':'No autorizado'}), 403
    if row.metodo not in ('APENDICE_I','APENDICE_II'):
        return jsonify({'status':'error','message':'Este método todavía no tiene plantilla Excel configurada'}), 400
    try:
        payload = json.loads(row.payload_json or '{}')
    except Exception:
        payload = {}
    try:
        result = json.loads(row.result_json or '{}')
    except Exception:
        result = {}
    # Se reutiliza exactamente el mismo armado de datos que alimenta la matriz imprimible.
    from routes.main import _generic_matrix
    from services.matrix_excel import export_nom_excel
    matrix = _generic_matrix(row, payload, result)
    stream, filename = export_nom_excel(matrix, payload)
    return send_file(
        stream,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
