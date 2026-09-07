from flask import Blueprint, request, jsonify, session, redirect
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
