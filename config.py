"""
Configuración de ErgonometApp v2.0
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Aplicación
    APP_NAME = "ErgonometApp v2.0"
    VERSION = "2.0.0"
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ergonometapp-dev-secret-key-2026'
    DEBUG = os.environ.get('FLASK_DEBUG') or True
    TESTING = False
    
    # Base de datos
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'ergonometapp.db')
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Servidor
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Sesión
    SESSION_COOKIE_SECURE = False  # True en producción
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload de archivos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # Configuración de reportes
    REPORTES_FOLDER = os.path.join(BASE_DIR, 'reportes')
    
    # Métodos soportados
    METODOS_SOPORTADOS = [
        'reba',
        'ley_silla', 
        'lest',
        'apendice_i',
        'apendice_ii',
        'kuorinka'
    ]
    
    # Niveles de riesgo
    NIVELES_RIESGO = {
        'bajo': {'min': 0, 'max': 0.75, 'color': '#28A745'},
        'ligero': {'min': 0.75, 'max': 1.5, 'color': '#FFC107'},
        'moderado': {'min': 1.5, 'max': 3, 'color': '#FF9800'},
        'alto': {'min': 3, 'max': float('inf'), 'color': '#DC3545'}
    }


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Seleccionar configuración según variable de entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env=None):
    """Obtener configuración según entorno"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
