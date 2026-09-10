from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig, ProductionConfig
import os

# Inicializar DB
db = SQLAlchemy()

# Crear app
app = Flask(__name__, template_folder='templates')

# Configuración
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Flask-SQLAlchemy resuelve rutas SQLite relativas dentro de instance/.
db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
if db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):
    relative_db = db_uri.replace('sqlite:///', '', 1)
    db_parent = os.path.dirname(os.path.join(app.instance_path, relative_db))
    if db_parent:
        os.makedirs(db_parent, exist_ok=True)

# Inicializar extensiones
db.init_app(app)

# Registrar blueprints
with app.app_context():
    try:
        import routes.main as main_routes
        extra_login_user = os.environ.get('EXTRA_LOGIN_USER', '').strip()
        extra_login_password = os.environ.get('EXTRA_LOGIN_PASSWORD', '')
        if extra_login_user and extra_login_password:
            main_routes.DEMO_USERS[extra_login_user] = extra_login_password
        from routes.main import bp_main
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

        app.register_blueprint(bp_main)
        app.register_blueprint(bp_dashboard)
        app.register_blueprint(bp_generic_evaluations)
        app.register_blueprint(bp_reba)
        app.register_blueprint(bp_ley_silla)
        app.register_blueprint(bp_lest)
        app.register_blueprint(bp_apendice_i)
        app.register_blueprint(bp_apendice_ii)
        app.register_blueprint(bp_kuorinka)
        print('✅ Todos los blueprints registrados')
    except ImportError as exc:
        print(f'⚠️ Error cargando blueprints: {exc}')

    try:
        db.create_all()
        print('✅ Base de datos inicializada')
    except Exception as exc:
        print(f'⚠️ Error creando tablas: {exc}')


@app.after_request
def after_request(response):
    if response.mimetype.startswith('text/'):
        response.headers['Content-Type'] = f'{response.mimetype}; charset=utf-8'

    if response.mimetype == 'text/html':
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        html = response.get_data(as_text=True)

        if request.path == '/reba/nueva':
            old_style = "background-image:url('${SPRITE}');background-size:400% 600%;background-position:${col*100/3}% ${row*100/5}%"
            new_style = "background-image:url('/static/img/reba/${img}.png?v=original-hq');background-size:contain;background-position:center;background-repeat:no-repeat"
            if old_style in html:
                html = html.replace(old_style, new_style)

        if request.path == '/apendice-i/nueva':
            refinement = render_template('apendice_i_refinements_v6.html')
            if 'factor-evidence-title' not in html:
                html = html.replace('</body>', refinement + '</body>')

        if request.path == '/apendice-ii/nueva':
            norm_images = render_template('apendice_ii_norm_images_v2.html')
            if 'data-nom-ref' not in html:
                html = html.replace('</body>', norm_images + '</body>')

        if request.path in ('/apendice-i/nueva','/apendice-ii/nueva'):
            matrix_meta = render_template('nom_matrix_metadata.html')
            if 'matrixClientData' not in html:
                html = html.replace('</body>', matrix_meta + '</body>')

        if request.path in ('/apendice-i/nueva','/apendice-ii/nueva','/cuestionario-nordico/nueva'):
            script = '<script src="/static/js/nom_persistence.js?v=6"></script>'
            if script not in html:
                html = html.replace('</body>', script + '</body>')

        if request.path.endswith('/matriz'):
            print_css = '<link rel="stylesheet" href="/static/css/matrix_print_tabloid.css?v=4">'
            if 'matrix_print_tabloid.css' not in html:
                html = html.replace('</head>', print_css + '</head>')

        response.set_data(html)

    return response


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Página no encontrada', codigo=404), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='Error del servidor', codigo=500), 500


if __name__ == '__main__':
    app.run(debug=True)
