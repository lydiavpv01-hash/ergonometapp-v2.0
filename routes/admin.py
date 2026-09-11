from flask import Blueprint, render_template, session, redirect, jsonify
from functools import wraps
import json

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect('/login')
        if session.get('usuario') != 'admin':
            return jsonify({'status': 'error', 'message': 'Acceso restringido a administradores'}), 403
        return f(*args, **kwargs)
    return decorated_function


def _extract_empresa(payload_json):
    try:
        payload = json.loads(payload_json or '{}')
    except Exception:
        return ''
    meta = payload.get('meta') or {}
    for key in ('razon_social', 'empresa', 'cliente'):
        if meta.get(key):
            return meta.get(key)
    snapshot = payload.get('snapshot') or {}
    for field in snapshot.get('fields') or []:
        label = (field.get('label') or '').strip().lower()
        if label in ('empresa', 'empresa:', 'razón social', 'razon social', 'cliente'):
            return field.get('value') or ''
    return ''


@bp_admin.route('/')
@admin_required
def panel():
    from routes.main import DEMO_USERS
    from models.reba_evaluation import RebaEvaluation
    from models.generic_evaluation import GenericEvaluation

    reba_rows = RebaEvaluation.query.order_by(RebaEvaluation.created_at.desc()).all()
    generic_rows = GenericEvaluation.query.order_by(GenericEvaluation.created_at.desc()).all()

    counts = {u: 0 for u in DEMO_USERS.keys()}
    trabajos = []

    for e in reba_rows:
        counts[e.usuario] = counts.get(e.usuario, 0) + 1
        trabajos.append({
            'tipo': 'REBA',
            'id': e.id,
            'usuario': e.usuario,
            'empresa': _extract_empresa(e.payload_json),
            'area': e.area or '',
            'puesto': e.puesto or '',
            'trabajador': e.trabajador or '',
            'fecha': e.fecha or '',
            'resultado': e.risk_level or (str(e.final_score) if e.final_score is not None else ''),
            'created_at': e.created_at,
        })

    for e in generic_rows:
        counts[e.usuario] = counts.get(e.usuario, 0) + 1
        trabajos.append({
            'tipo': e.metodo or 'Evaluación',
            'id': e.id,
            'usuario': e.usuario,
            'empresa': _extract_empresa(e.payload_json),
            'area': '',
            'puesto': e.puesto or '',
            'trabajador': e.trabajador or '',
            'fecha': e.fecha or '',
            'resultado': e.risk_level or (str(e.final_score) if e.final_score is not None else ''),
            'created_at': e.created_at,
        })

    trabajos.sort(key=lambda x: x['created_at'] or 0, reverse=True)

    usuarios = []
    for username in sorted(DEMO_USERS.keys(), key=lambda x: (x != 'admin', x.lower())):
        usuarios.append({
            'usuario': username,
            'rol': 'Administrador' if username == 'admin' else 'Usuario',
            'estado': 'Activo',
            'evaluaciones': counts.get(username, 0),
        })

    resumen = {
        'usuarios': len(usuarios),
        'evaluaciones': len(trabajos),
        'reba': sum(1 for t in trabajos if t['tipo'] == 'REBA'),
        'apendice_i': sum(1 for t in trabajos if t['tipo'] == 'APENDICE_I'),
        'apendice_ii': sum(1 for t in trabajos if t['tipo'] == 'APENDICE_II'),
        'kuorinka': sum(1 for t in trabajos if t['tipo'] == 'KUORINKA'),
    }

    return render_template(
        'admin_panel.html',
        usuario=session.get('usuario'),
        usuarios=usuarios,
        trabajos=trabajos,
        resumen=resumen,
    )
