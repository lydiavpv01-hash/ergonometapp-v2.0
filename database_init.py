"""
database_init.py - Inicialización de base de datos
"""

from app import app, db, Usuario, Trabajador, Evaluacion
from datetime import datetime
import uuid

def init_database():
    """Inicializar base de datos"""
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✓ Tablas creadas")
        
        # Crear usuario de demostración
        if not Usuario.query.first():
            usuario = Usuario(
                nombre='Auditor Demo',
                email='demo@ergonometapp.com',
                password='demo123',
                rol='admin'
            )
            db.session.add(usuario)
            print("✓ Usuario demo creado")
        
        # Crear trabajadores de demostración
        if not Trabajador.query.first():
            trabajadores = [
                Trabajador(
                    nombre='Juan García López',
                    puesto='Operario de línea',
                    departamento='Producción',
                    empresa='Empresa Ejemplo S.A.',
                    edad=35,
                    experiencia_anios=5
                ),
                Trabajador(
                    nombre='María López García',
                    puesto='Empaquetadora',
                    departamento='Empaque',
                    empresa='Empresa Ejemplo S.A.',
                    edad=28,
                    experiencia_anios=3
                ),
                Trabajador(
                    nombre='Carlos Ruiz Martínez',
                    puesto='Supervisor',
                    departamento='Producción',
                    empresa='Empresa Ejemplo S.A.',
                    edad=42,
                    experiencia_anios=10
                )
            ]
            for t in trabajadores:
                db.session.add(t)
            print(f"✓ {len(trabajadores)} trabajadores demo creados")
        
        db.session.commit()
        print("✓ Base de datos inicializada")

if __name__ == '__main__':
    init_database()
