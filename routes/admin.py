from flask import Blueprint, render_template, session, redirect, jsonify, request, flash
from functools import wraps
import json
import os

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect('/login')
        admin_user = os.environ.get('ADMIN_LOGIN_USER', '').strip()
        if session.get('rol') != 'admin' or session.get('usuario') != admin_user:
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


@bp_admin.route('/usuarios', methods=['POST'])
@admin_required
def crear_usuario():
    from app import db
    from models.app_user import AppUser
    from routes.main import DEMO_USERS

    usuario = (request.form.get('usuario') or '').strip().lower()
    password = request.form.get('password') or ''
    admin_user = os.environ.get('ADMIN_LOGIN_USER', '').strip().lower()

    if not usuario or not password:
        flash('Debes capturar usuario y contraseña.', 'error')
        return redirect('/admin/#usuarios')
    if len(usuario) > 180:
        flash('El usuario es demasiado largo.', 'error')
        return redirect('/admin/#usuarios')
    if len(password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres.', 'error')
        return redirect('/admin/#usuarios')
    if usuario == admin_user or usuario in {u.lower() for u in DEMO_USERS.keys()}:
        flash('Ese usuario ya tiene acceso a ErgonometApp.', 'error')
        return redirect('/admin/#usuarios')
    if AppUser.query.filter(db.func.lower(AppUser.usuario) == usuario).first():
        flash('Ese usuario ya está registrado.', 'error')
        return redirect('/admin/#usuarios')

    account = AppUser(usuario=usuario, rol='usuario', activo=True)
    account.set_password(password)
    db.session.add(account)
    db.session.commit()
    flash(f'Usuario {usuario} creado correctamente.', 'success')
    return redirect('/admin/#usuarios')


@bp_admin.route('/evaluaciones/<string:tipo>/<int:evaluation_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_evaluacion(tipo, evaluation_id):
    from app import db
    from models.reba_evaluation import RebaEvaluation
    from models.generic_evaluation import GenericEvaluation
    from models.evaluation_upload import EvaluationUpload

    tipo = (tipo or '').upper()
    if tipo == 'REBA':
        row = RebaEvaluation.query.get_or_404(evaluation_id)
        db.session.delete(row)
    else:
        row = GenericEvaluation.query.get_or_404(evaluation_id)
        EvaluationUpload.query.filter_by(evaluation_id=evaluation_id).delete(synchronize_session=False)
        db.session.delete(row)

    db.session.commit()
    flash('Evaluación eliminada correctamente.', 'success')
    return redirect('/admin/#trabajos')


@bp_admin.route('/')
@admin_required
def panel():
    from routes.main import DEMO_USERS
    from models.app_user import AppUser
    from models.reba_evaluation import RebaEvaluation
    from models.generic_evaluation import GenericEvaluation

    reba_rows = RebaEvaluation.query.order_by(RebaEvaluation.created_at.desc()).all()
    generic_rows = GenericEvaluation.query.order_by(GenericEvaluation.created_at.desc()).all()
    db_users = AppUser.query.order_by(AppUser.usuario.asc()).all()

    admin_user = os.environ.get('ADMIN_LOGIN_USER', '').strip()
    visible_users = []
    if admin_user:
        visible_users.append((admin_user, 'Administrador', 'Activo'))

    # Conserva las cuentas existentes mientras se completa su migración al panel.
    for username in DEMO_USERS.keys():
        if username == 'admin':
            continue
        if username.lower() != admin_user.lower():
            visible_users.append((username, 'Usuario', 'Activo'))

    existing = {u[0].lower() for u in visible_users}
    for account in db_users:
        if account.usuario.lower() not in existing:
            visible_users.append((
                account.usuario,
                'Administrador' if account.rol == 'admin' else 'Usuario',
                'Activo' if account.activo else 'Inactivo',
            ))
            existing.add(account.usuario.lower())

    counts = {u[0]: 0 for u in visible_users}
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
    for username, role, estado in sorted(visible_users, key=lambda x: (x[1] != 'Administrador', x[0].lower())):
        usuarios.append({
            'usuario': username,
            'rol': role,
            'estado': estado,
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
