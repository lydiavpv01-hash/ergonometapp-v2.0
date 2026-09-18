from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig, ProductionConfig
import os

db = SQLAlchemy()
app = Flask(__name__, template_folder='templates')
if os.environ.get('FLASK_ENV') == 'production': app.config.from_object(ProductionConfig)
else: app.config.from_object(DevelopmentConfig)
db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):
    relative_db = db_uri.replace('sqlite:///', '', 1); db_parent = os.path.dirname(os.path.join(app.instance_path, relative_db))
    if db_parent: os.makedirs(db_parent, exist_ok=True)
db.init_app(app)
with app.app_context():
    try:
        import routes.main as main_routes
        extra_login_user=os.environ.get('EXTRA_LOGIN_USER','').strip(); extra_login_password=os.environ.get('EXTRA_LOGIN_PASSWORD','')
        if extra_login_user and extra_login_password: main_routes.DEMO_USERS[extra_login_user]=extra_login_password
        from models.app_user import AppUser
        from models.access_log import AccessLog
        from models.revoked_user import RevokedUser
        from routes.main import bp_main
        from routes.admin import bp_admin
        from routes.dashboard import bp_dashboard
        from routes.generic_evaluations import bp_generic_evaluations
        from routes.metodos.reba import bp_reba
        from routes.metodos.ley_silla import bp_ley_silla
        from routes.metodos.lest import bp_lest
        from routes.metodos.apendice_i import bp_apendice_i
        from routes.metodos.apendice_ii import bp_apendice_ii
        from routes.metodos.kuorinka import bp_kuorinka
        from services.matrix_enrichment import install_matrix_enrichment
        install_matrix_enrichment(main_routes)
        for bp in (bp_main,bp_admin,bp_dashboard,bp_generic_evaluations,bp_reba,bp_ley_silla,bp_lest,bp_apendice_i,bp_apendice_ii,bp_kuorinka): app.register_blueprint(bp)
        print('✅ Todos los blueprints registrados')
    except ImportError as exc: print(f'⚠️ Error cargando blueprints: {exc}')
    try: db.create_all(); print('✅ Base de datos inicializada')
    except Exception as exc: print(f'⚠️ Error creando tablas: {exc}')

@app.before_request
def database_and_admin_login():
    if request.path != '/login' or request.method != 'POST': return None
    usuario=(request.form.get('usuario') or '').strip(); password=request.form.get('password') or ''
    admin_user=os.environ.get('ADMIN_LOGIN_USER','').strip(); admin_password=os.environ.get('ADMIN_LOGIN_PASSWORD','')
    if admin_user and usuario==admin_user:
        if password==admin_password:
            session.clear(); session.permanent=True; session['usuario']=usuario; session['rol']='admin'; session.modified=True; return redirect('/dashboard')
        return render_template('login.html',error='Usuario o contraseña incorrectos')
    if usuario=='admin': return render_template('login.html',error='Usuario o contraseña incorrectos')
    try:
        from models.revoked_user import RevokedUser
        revoked = RevokedUser.query.filter(db.func.lower(RevokedUser.usuario) == usuario.lower()).first()
        if revoked:
            return render_template('login.html',error='Usuario o contraseña incorrectos')
        from models.app_user import AppUser
        account=AppUser.query.filter(db.func.lower(AppUser.usuario) == usuario.lower()).first()
        if account:
            if account.activo and account.check_password(password):
                session.clear(); session.permanent=True; session['usuario']=account.usuario; session['rol']=account.rol or 'usuario'; session.modified=True; return redirect('/dashboard')
            return render_template('login.html',error='Usuario o contraseña incorrectos')
    except Exception as exc: print(f'⚠️ No se pudo consultar usuarios administrables: {exc}')
    return None

@app.after_request
def after_request(response):
    if request.path=='/login' and request.method=='POST' and 300 <= response.status_code < 400 and session.get('usuario'):
        try:
            from models.access_log import AccessLog
            db.session.add(AccessLog(usuario=session.get('usuario','')))
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            print(f'⚠️ No se pudo registrar el acceso: {exc}')
    if response.mimetype.startswith('text/'): response.headers['Content-Type']=f'{response.mimetype}; charset=utf-8'
    if response.mimetype=='text/html':
        response.headers['Cache-Control']='no-store, no-cache, must-revalidate, max-age=0'; response.headers['Pragma']='no-cache'; response.headers['Expires']='0'; html=response.get_data(as_text=True)
        if request.path=='/dashboard' and session.get('rol')=='admin' and 'href="/admin/"' not in html:
            html=html.replace('<a class="nav" href="#">Configuración</a>','<a class="nav" href="/admin/">Administración</a><a class="nav" href="#">Configuración</a>')
        if request.path=='/reba/nueva':
            old_style="background-image:url('${SPRITE}');background-size:400% 600%;background-position:${col*100/3}% ${row*100/5}%"; new_style="background-image:url('/static/img/reba/${img}.png?v=original-hq');background-size:contain;background-position:center;background-repeat:no-repeat"
            if old_style in html: html=html.replace(old_style,new_style)
        if request.path=='/apendice-i/nueva':
            refinement=render_template('apendice_i_refinements_v6.html')
            if 'factor-evidence-title' not in html: html=html.replace('</body>',refinement+'</body>')
        if request.path=='/apendice-ii/nueva':
            norm_images=render_template('apendice_ii_norm_images_v2.html')
            if 'data-nom-ref' not in html: html=html.replace('</body>',norm_images+'</body>')
        if request.path in ('/apendice-i/nueva','/apendice-ii/nueva'):
            matrix_meta=render_template('nom_matrix_metadata.html')
            if 'matrixClientData' not in html: html=html.replace('</body>',matrix_meta+'</body>')
        if request.path in ('/apendice-i/nueva','/apendice-ii/nueva','/cuestionario-nordico/nueva'):
            script='<script src="/static/js/nom_persistence.js?v=7"></script>'
            if script not in html: html=html.replace('</body>',script+'</body>')
        if request.path.endswith('/matriz'):
            print_css='<link rel="stylesheet" href="/static/css/matrix_print_tabloid.css?v=7">'
            pagination='<script src="/static/js/matrix_print_pagination.js?v=1"></script>'
            if 'matrix_print_tabloid.css' not in html: html=html.replace('</head>',print_css+'</head>')
            if 'matrix_print_pagination.js' not in html: html=html.replace('</body>',pagination+'</body>')
        response.set_data(html)
    return response

@app.errorhandler(404)
def not_found(error): return render_template('error.html',error='Página no encontrada',codigo=404),404
@app.errorhandler(500)
def server_error(error): return render_template('error.html',error='Error del servidor',codigo=500),500
if __name__=='__main__': app.run(debug=True)
