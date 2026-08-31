from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig, ProductionConfig
import os

# Inicializar extensiones
db = SQLAlchemy()

def create_app(config_name='development'):
    """Factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Inicializar DB
    db.init_app(app)
    
    # Registrar blueprints
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
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
