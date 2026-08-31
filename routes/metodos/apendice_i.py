"""
routes/metodos/apendice_i.py - Rutas para Apéndice I: Levantamiento de Cargas
Evaluación según NOM-036-1-STPS-2018
"""

import json
import uuid
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from models_apendice_i import calculate_apendice_i, get_zona_segura

# ════════════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ════════════════════════════════════════════════════════════════════════════════════

bp_apendice_i = Blueprint('apendice_i', __name__, url_prefix='/apendice-i')


def login_required(f):
    """Decorator para verificar que el usuario está logeado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_db():
    """Obtener conexión a BD"""
    db = sqlite3.connect('database/ergonometapp.db')
    db.row_factory = sqlite3.Row
    return db


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 1: DATOS GENERALES
# ════════════════════════════════════════════════════════════════════════════════════

@bp_apendice_i.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_evaluacion():
    """
    Paso 1: Crear nueva evaluación Apéndice I
    """
    if request.method == 'POST':
        datos = request.get_json()
        
        # Crear UUID para evaluación
        eval_uuid = str(uuid.uuid4())
        
        # Guardar en BD
        db = get_db()
        db.execute('''
            INSERT INTO evaluaciones 
            (uuid, user_id, tipo, trabajador, puesto, area, empresa, razon_social, fecha, sector, estado, datos_generales)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            eval_uuid,
            session['user_id'],
            'apendice_i',
            datos.get('trabajador'),
            datos.get('puesto'),
            datos.get('area'),
            datos.get('empresa'),
            datos.get('razon_social'),
            datos.get('fecha', datetime.now().strftime('%Y-%m-%d')),
            datos.get('sector'),
            'en_progreso',
            json.dumps(datos),
        ))
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'eval_uuid': eval_uuid,
            'redirect': url_for('apendice_i.paso_parametros', eval_uuid=eval_uuid)
        })
    
    # GET: Renderizar formulario
    db = get_db()
    trabajadores = db.execute(
        'SELECT * FROM trabajadores WHERE user_id=? ORDER BY nombre',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    return render_template(
        'metodos/apendice_i/paso1_datos.html',
        trabajadores=[dict(t) for t in trabajadores]
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 2: PARÁMETROS DEL LEVANTAMIENTO
# ════════════════════════════════════════════════════════════════════════════════════

@bp_apendice_i.route('/<eval_uuid>/paso2', methods=['GET', 'POST'])
@login_required
def paso_parametros(eval_uuid):
    """
    Paso 2: Parámetros del levantamiento
    - Peso de la carga (kg)
    - Altura de origen (cm)
    - Altura de destino (cm)
    - Distancia horizontal (cm)
    - Ángulo de giro (grados)
    - Frecuencia (levantamientos/min)
    - Duración (horas)
    - Tipo de agarre
    """
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('apendice_i.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar datos del paso 2
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['parametros'] = datos.get('parametros', {})
        
        db.execute(
            'UPDATE evaluaciones SET datos_evaluacion=? WHERE uuid=?',
            (json.dumps(current_data), eval_uuid)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('apendice_i.paso_resultado', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar paso 2
    return render_template(
        'metodos/apendice_i/paso2_parametros.html',
        eval_uuid=eval_uuid
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 3: RESULTADO FINAL
# ════════════════════════════════════════════════════════════════════════════════════

@bp_apendice_i.route('/<eval_uuid>/paso3', methods=['GET', 'POST'])
@login_required
def paso_resultado(eval_uuid):
    """
    Paso 3: Calcular resultado y mostrar análisis
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('apendice_i.nueva_evaluacion'))
    
    # Obtener datos y calcular
    datos_eval = json.loads(ev['datos_evaluacion'] or '{}')
    parametros = datos_eval.get('parametros', {})
    
    # Calcular Apéndice I
    resultado = calculate_apendice_i(parametros)
    resultado['zona'] = get_zona_segura(resultado['LI'])
    
    if request.method == 'POST':
        # Guardar resultado final
        db.execute('''
            UPDATE evaluaciones 
            SET datos_calculo=?, resultado_final=?, estado='completada', completada_at=?
            WHERE uuid=?
        ''', (
            json.dumps(resultado),
            json.dumps(resultado),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            eval_uuid
        ))
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('descargar_reporte_apendice_i', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar resultado
    return render_template(
        'metodos/apendice_i/paso3_resultado.html',
        eval_uuid=eval_uuid,
        resultado=resultado
    )


# ════════════════════════════════════════════════════════════════════════════════════
# ENDPOINT DE REPORTE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_apendice_i.route('/<eval_uuid>/reporte', methods=['GET'])
@login_required
def descargar_reporte_apendice_i(eval_uuid):
    """
    Descargar reporte Apéndice I en DOCX
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return redirect(url_for('apendice_i.nueva_evaluacion'))
    
    return jsonify({
        'message': 'Reporte en construcción',
        'evaluacion_uuid': eval_uuid,
    })
