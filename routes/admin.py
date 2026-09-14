from flask import Blueprint, render_template, session, redirect, jsonify, request, flash
from functools import wraps
from datetime import timezone
from zoneinfo import ZoneInfo
import json
import os

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')
MX_TZ = ZoneInfo('America/Mexico_City')


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


def _format_dt(value):
    if not value: return '—'
    try:
        if value.tzinfo is None: value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(MX_TZ).strftime('%d/%m/%Y %H:%M')
    except Exception: return '—'


def _extract_empresa(payload_json):
    try: payload = json.loads(payload_json or '{}')
    except Exception: return ''
    meta = payload.get('meta') or {}
    for key in ('razon_social', 'empresa', 'cliente'):
        if meta.get(key): return meta.get(key)
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
    from models.revoked_user import RevokedUser
    from routes.main import DEMO_USERS
    usuario = (request.form.get('usuario') or '').strip().lower()
    password = request.form.get('password') or ''
    admin_user = os.environ.get('ADMIN_LOGIN_USER', '').strip().lower()
    if not usuario or not password:
        flash('Debes capturar usuario y contraseña.', 'error'); return redirect('/admin/#usuarios')
    if len(usuario) > 180:
        flash('El usuario es demasiado largo.', 'error'); return redirect('/admin/#usuarios')
    if len(password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres.', 'error'); return redirect('/admin/#usuarios')
    if usuario == admin_user:
        flash('Ese usuario corresponde al administrador protegido.', 'error'); return redirect('/admin/#usuarios')
    revoked = RevokedUser.query.filter(db.func.lower(RevokedUser.usuario) == usuario).first()
    legacy_exists = usuario in {u.lower() for u in DEMO_USERS.keys()}
    if legacy_exists and not revoked:
        flash('Ese usuario ya tiene acceso a ErgonometApp.', 'error'); return redirect('/admin/#usuarios')
    if AppUser.query.filter(db.func.lower(AppUser.usuario) == usuario).first():
        flash('Ese usuario ya está registrado.', 'error'); return redirect('/admin/#usuarios')
    if revoked:
        db.session.delete(revoked)
    account = AppUser(usuario=usuario, rol='usuario', activo=True); account.set_password(password)
    db.session.add(account); db.session.commit()
    flash(f'Usuario {usuario} creado correctamente.', 'success')
    return redirect('/admin/#usuarios')


@bp_admin.route('/usuarios/<int:user_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_usuario(user_id):
    from app import db
    from models.app_user import AppUser
    account = AppUser.query.get_or_404(user_id)
    if account.rol == 'admin':
        flash('La cuenta de administrador no se puede eliminar.', 'error'); return redirect('/admin/#usuarios')
    usuario = account.usuario
    db.session.delete(account); db.session.commit()
    flash(f'Usuario {usuario} eliminado. Sus evaluaciones y su historial de accesos se conservaron.', 'success')
    return redirect('/admin/#usuarios')


@bp_admin.route('/usuarios/heredado/eliminar', methods=['POST'])
@admin_required
def eliminar_usuario_heredado():
    from app import db
    from models.revoked_user import RevokedUser
    from routes.main import DEMO_USERS
    usuario = (request.form.get('usuario') or '').strip()
    admin_user = os.environ.get('ADMIN_LOGIN_USER', '').strip()
    if not usuario or usuario == admin_user:
        flash('La cuenta de administrador no se puede eliminar.', 'error'); return redirect('/admin/#usuarios')
    legacy = {u.lower(): u for u in DEMO_USERS.keys() if u != 'admin'}
    if usuario.lower() not in legacy:
        flash('La cuenta indicada no es una cuenta heredada válida.', 'error'); return redirect('/admin/#usuarios')
    existing = RevokedUser.query.filter(db.func.lower(RevokedUser.usuario) == usuario.lower()).first()
    if not existing:
        db.session.add(RevokedUser(usuario=legacy[usuario.lower()]))
        db.session.commit()
    flash(f'Usuario {legacy[usuario.lower()]} eliminado. Ya no podrá iniciar sesión; sus evaluaciones e historial se conservaron.', 'success')
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
        row = RebaEvaluation.query.get_or_404(evaluation_id); db.session.delete(row)
    else:
        row = GenericEvaluation.query.get_or_404(evaluation_id)
        EvaluationUpload.query.filter_by(evaluation_id=evaluation_id).delete(synchronize_session=False)
        db.session.delete(row)
    db.session.commit(); flash('Evaluación eliminada correctamente.', 'success')
    return redirect('/admin/#trabajos')


@bp_admin.route('/')
@admin_required
def panel():
    from app import db
    from routes.main import DEMO_USERS
    from models.app_user import AppUser
    from models.access_log import AccessLog
    from models.revoked_user import RevokedUser
    from models.reba_evaluation import RebaEvaluation
    from models.generic_evaluation import GenericEvaluation

    reba_rows = RebaEvaluation.query.order_by(RebaEvaluation.created_at.desc()).all()
    generic_rows = GenericEvaluation.query.order_by(GenericEvaluation.created_at.desc()).all()
    db_users = AppUser.query.order_by(AppUser.usuario.asc()).all()
    access_rows = AccessLog.query.order_by(AccessLog.logged_at.desc()).limit(500).all()
    revoked = {r.usuario.lower() for r in RevokedUser.query.all()}

    admin_user = os.environ.get('ADMIN_LOGIN_USER', '').strip()
    visible_users = []
    if admin_user:
        visible_users.append({'usuario': admin_user, 'rol': 'Administrador', 'estado': 'Activo', 'db_id': None, 'eliminable': False, 'legacy': False})
    for username in DEMO_USERS.keys():
        if username == 'admin' or username.lower() == admin_user.lower() or username.lower() in revoked:
            continue
        visible_users.append({'usuario': username, 'rol': 'Usuario', 'estado': 'Activo', 'db_id': None, 'eliminable': True, 'legacy': True})
    existing = {u['usuario'].lower() for u in visible_users}
    for account in db_users:
        if account.usuario.lower() not in existing:
            visible_users.append({'usuario': account.usuario,'rol': 'Administrador' if account.rol == 'admin' else 'Usuario','estado': 'Activo' if account.activo else 'Inactivo','db_id': account.id,'eliminable': account.rol != 'admin','legacy': False})
            existing.add(account.usuario.lower())

    counts = {u['usuario']: 0 for u in visible_users}
    trabajos = []; latest_eval = {}
    for e in reba_rows:
        counts[e.usuario] = counts.get(e.usuario, 0) + 1
        trabajos.append({'tipo':'REBA','id':e.id,'usuario':e.usuario,'empresa':_extract_empresa(e.payload_json),'area':e.area or '','puesto':e.puesto or '','trabajador':e.trabajador or '','fecha':e.fecha or '','resultado':e.risk_level or (str(e.final_score) if e.final_score is not None else ''),'created_at':e.created_at})
        if e.usuario not in latest_eval or (e.created_at and e.created_at > latest_eval[e.usuario]): latest_eval[e.usuario] = e.created_at
    for e in generic_rows:
        counts[e.usuario] = counts.get(e.usuario, 0) + 1
        trabajos.append({'tipo':e.metodo or 'Evaluación','id':e.id,'usuario':e.usuario,'empresa':_extract_empresa(e.payload_json),'area':'','puesto':e.puesto or '','trabajador':e.trabajador or '','fecha':e.fecha or '','resultado':e.risk_level or (str(e.final_score) if e.final_score is not None else ''),'created_at':e.created_at})
        if e.usuario not in latest_eval or (e.created_at and e.created_at > latest_eval[e.usuario]): latest_eval[e.usuario] = e.created_at
    trabajos.sort(key=lambda x: x['created_at'] or 0, reverse=True)

    last_access = {}; historial_accesos = []
    for row in access_rows:
        if row.usuario not in last_access: last_access[row.usuario] = row.logged_at
        historial_accesos.append({'usuario': row.usuario, 'fecha_hora': _format_dt(row.logged_at)})

    usuarios = []
    for u in sorted(visible_users, key=lambda x: (x['rol'] != 'Administrador', x['usuario'].lower())):
        item = dict(u); item['evaluaciones'] = counts.get(u['usuario'], 0); item['ultimo_acceso'] = _format_dt(last_access.get(u['usuario'])); item['ultima_evaluacion'] = _format_dt(latest_eval.get(u['usuario'])); usuarios.append(item)

    resumen = {'usuarios':len(usuarios),'evaluaciones':len(trabajos),'reba':sum(1 for t in trabajos if t['tipo']=='REBA'),'apendice_i':sum(1 for t in trabajos if t['tipo']=='APENDICE_I'),'apendice_ii':sum(1 for t in trabajos if t['tipo']=='APENDICE_II'),'kuorinka':sum(1 for t in trabajos if t['tipo']=='KUORINKA')}
    return render_template('admin_panel.html', usuario=session.get('usuario'), usuarios=usuarios, trabajos=trabajos, historial_accesos=historial_accesos, resumen=resumen)
