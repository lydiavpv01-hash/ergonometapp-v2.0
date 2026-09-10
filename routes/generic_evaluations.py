from flask import Blueprint, request, jsonify, session, send_file
from functools import wraps
import json
from app import db
from models.generic_evaluation import GenericEvaluation
from models.evaluation_upload import EvaluationUpload

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
        trabajador = (meta.get('trabajador') or '').strip() or 'Grupo / trabajador no especificado'
        puesto = (meta.get('puesto') or '').strip() or 'Puesto no especificado'

        # Las imágenes se almacenan en evaluation_uploads y nunca dentro del JSON principal.
        data.pop('uploads', None)
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


@bp_generic_evaluations.route('/<int:evaluation_id>/uploads', methods=['POST'])
@login_required
def guardar_upload(evaluation_id):
    try:
        row = GenericEvaluation.query.get_or_404(evaluation_id)
        if row.usuario != session.get('usuario',''):
            return jsonify({'status':'error','message':'No autorizado'}), 403
        data = request.get_json(silent=True) or {}
        field = (data.get('field') or 'archivo')[:180]
        name = (data.get('name') or 'imagen.jpg')[:255]
        mime_type = (data.get('type') or 'image/jpeg')[:100]
        encoded = data.get('data') or ''
        if not encoded.startswith('data:'):
            return jsonify({'status':'error','message':'Imagen no válida'}), 400
        # Cada evidencia ya llega optimizada desde el navegador; este límite evita cargas anómalas.
        if len(encoded) > 4 * 1024 * 1024:
            return jsonify({'status':'error','message':'La imagen sigue siendo demasiado grande después de optimizarse'}), 413
        upload = EvaluationUpload(
            evaluation_id=row.id,
            usuario=row.usuario,
            field=field,
            name=name,
            mime_type=mime_type,
            size=int(data.get('size') or 0),
            data=encoded,
            position=int(data.get('position') or 0),
        )
        db.session.add(upload)
        db.session.commit()
        return jsonify({'status':'success','id':upload.id})
    except Exception as exc:
        db.session.rollback()
        return jsonify({'status':'error','message':str(exc)}), 500


@bp_generic_evaluations.route('/<int:evaluation_id>/excel', methods=['GET'])
@login_required
def descargar_excel(evaluation_id):
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
    payload['uploads'] = [u.as_payload() for u in EvaluationUpload.query.filter_by(evaluation_id=row.id, usuario=row.usuario).order_by(EvaluationUpload.position.asc(), EvaluationUpload.id.asc()).all()]
    from routes.main import _generic_matrix
    from services.matrix_excel_sgc import export_nom_excel
    matrix = _generic_matrix(row, payload, result)
    stream, filename = export_nom_excel(matrix, payload)
    return send_file(
        stream,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
