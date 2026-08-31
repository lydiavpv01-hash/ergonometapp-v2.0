from flask import Flask, render_template
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
        
        print("✅ Todos los blueprints registrados")
    except ImportError as e:
        print(f"⚠️ Error cargando blueprints: {e}")
    
    # Crear tablas
    try:
        db.create_all()
        print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️ Error en BD: {e}")

@app.errorhandler(404)
def not_found(error):
    """Manejo de 404"""
    return render_template('error.html', 
                          error='Página no encontrada', 
                          codigo=404), 404

@app.errorhandler(500)
def server_error(error):
    """Manejo de 500"""
    return render_template('error.html',
                          error='Error del servidor',
                          codigo=500), 500

if __name__ == '__main__':
    app.run(debug=True)
