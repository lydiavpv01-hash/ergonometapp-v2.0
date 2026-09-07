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
# En Render esa carpeta puede no existir en un deploy limpio, provocando
# sqlite3.OperationalError: unable to open database file.
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
        from routes.main import bp_main
        from routes.dashboard import bp_dashboard
        from routes.metodos.reba import bp_reba
        from routes.metodos.ley_silla import bp_ley_silla
        from routes.metodos.lest import bp_lest
        from routes.metodos.apendice_i import bp_apendice_i
        from routes.metodos.apendice_ii import bp_apendice_ii
        from routes.metodos.kuorinka import bp_kuorinka

        app.register_blueprint(bp_main)
        app.register_blueprint(bp_dashboard)
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
    """Mantener UTF-8, evitar caché y servir las referencias REBA originales en alta resolución."""
    if response.mimetype.startswith('text/'):
        response.headers['Content-Type'] = f'{response.mimetype}; charset=utf-8'

    if response.mimetype == 'text/html':
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        # El workspace REBA antiguo recortaba un sprite rasterizado. Sustituimos ese
        # recorte por los 24 PNG originales para que el navegador reduzca desde la
        # resolución fuente y conserve líneas/textos nítidos.
        if request.path == '/reba/nueva':
            html = response.get_data(as_text=True)
            old_style = "background-image:url('${SPRITE}');background-size:400% 600%;background-position:${col*100/3}% ${row*100/5}%"
            new_style = "background-image:url('/static/img/reba/${img}.png?v=original-hq');background-size:contain;background-position:center;background-repeat:no-repeat"
            if old_style in html:
                html = html.replace(old_style, new_style)
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
