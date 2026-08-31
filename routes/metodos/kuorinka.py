"""
routes/metodos/kuorinka.py - Rutas para Cuestionario Nórdico
Evaluación de síntomas musculoesqueléticos en 9 zonas
"""

import json
import uuid
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from models_kuorinka import calculate_kuorinka, listar_zonas

# ════════════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ════════════════════════════════════════════════════════════════════════════════════

bp_kuorinka = Blueprint('kuorinka', __name__, url_prefix='/cuestionario-nordico')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_db():
    db = sqlite3.connect('database/ergonometapp.db')
    db.row_factory = sqlite3.Row
    return db


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 1: DATOS GENERALES
# ════════════════════════════════════════════════════════════════════════════════════

@bp_kuorinka.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_evaluacion():
    """Paso 1: Crear nueva evaluación Cuestionario Nórdico"""
    
    if request.method == 'POST':
        datos = request.get_json()
        eval_uuid = str(uuid.uuid4())
        
        db = get_db()
        db.execute('''
            INSERT INTO evaluaciones 
            (uuid, user_id, tipo, trabajador, puesto, area, empresa, razon_social, fecha, sector, estado, datos_generales)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            eval_uuid, session['user_id'], 'kuorinka',
            datos.get('trabajador'), datos.get('puesto'), datos.get('area'),
            datos.get('empresa'), datos.get('razon_social'),
            datos.get('fecha', datetime.now().strftime('%Y-%m-%d')),
            datos.get('sector'), 'en_progreso', json.dumps(datos),
        ))
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'eval_uuid': eval_uuid,
            'redirect': url_for('kuorinka.paso_preguntas', eval_uuid=eval_uuid)
        })
    
    db = get_db()
    trabajadores = db.execute(
        'SELECT * FROM trabajadores WHERE user_id=? ORDER BY nombre',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    return render_template(
        'metodos/kuorinka/paso1_datos.html',
        trabajadores=[dict(t) for t in trabajadores]
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 2: PREGUNTAS Y RESULTADO
# ════════════════════════════════════════════════════════════════════════════════════

@bp_kuorinka.route('/<eval_uuid>/paso2', methods=['GET', 'POST'])
@login_required
def paso_preguntas(eval_uuid):
    """Paso 2: Preguntas del Cuestionario Nórdico"""
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('kuorinka.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar respuestas
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['respuestas'] = datos.get('respuestas', {})
        
        # Calcular resultado
        resultado = calculate_kuorinka(datos.get('respuestas', {}))
        
        # Guardar en BD
        db.execute('''
            UPDATE evaluaciones 
            SET datos_evaluacion=?, datos_calculo=?, resultado_final=?, estado='completada', completada_at=?
            WHERE uuid=?
        ''', (
            json.dumps(current_data),
            json.dumps(resultado),
            json.dumps(resultado),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            eval_uuid
        ))
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'resultado': resultado,
            'redirect': url_for('kuorinka.paso_resultado', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar preguntas
    zonas = listar_zonas()
    return render_template(
        'metodos/kuorinka/paso2_preguntas.html',
        eval_uuid=eval_uuid,
        zonas=zonas
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 3: RESULTADO FINAL
# ════════════════════════════════════════════════════════════════════════════════════

@bp_kuorinka.route('/<eval_uuid>/resultado', methods=['GET'])
@login_required
def paso_resultado(eval_uuid):
    """Paso 3: Mostrar resultado del análisis"""
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return redirect(url_for('kuorinka.nueva_evaluacion'))
    
    resultado = json.loads(ev['resultado_final'] or '{}')
    
    return render_template(
        'metodos/kuorinka/paso3_resultado.html',
        eval_uuid=eval_uuid,
        resultado=resultado
    )


# ════════════════════════════════════════════════════════════════════════════════════
# ENDPOINT DE REPORTE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_kuorinka.route('/<eval_uuid>/reporte', methods=['GET'])
@login_required
def descargar_reporte_kuorinka(eval_uuid):
    """Descargar reporte Cuestionario Nórdico"""
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return redirect(url_for('kuorinka.nueva_evaluacion'))
    
    return jsonify({'message': 'Reporte en construcción', 'evaluacion_uuid': eval_uuid})
