import os
from datetime import timedelta

class Config:
    """Configuración base"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_ECHO = True
    DATABASE_URL = 'sqlite:///database/ergonometapp.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SECRET_KEY = 'dev-key-change-in-production'
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configuración para producción (Render)"""
    DEBUG = False
    FLASK_ENV = 'production'
    SQLALCHEMY_ECHO = False
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database/ergonometapp.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'testing-key'
    SESSION_COOKIE_SECURE = False
