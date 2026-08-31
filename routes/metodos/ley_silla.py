"""
routes/metodos/ley_silla.py - Rutas para evaluación Ley Silla (3 pasos)
Método simple de bipedestación según DOF Disposiciones
"""

import json
import uuid
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from models_ley_silla import evaluar_ley_silla, get_superficie_options, get_tiempo_pie_options

# ════════════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ════════════════════════════════════════════════════════════════════════════════════

bp_ley_silla = Blueprint('ley_silla', __name__, url_prefix='/ley-silla')


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

@bp_ley_silla.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_evaluacion():
    """
    Paso 1: Crear nueva evaluación Ley Silla - Datos generales
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
            'ley_silla',
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
            'redirect': url_for('ley_silla.paso_factores', eval_uuid=eval_uuid)
        })
    
    # GET: Renderizar formulario paso 1
    db = get_db()
    trabajadores = db.execute(
        'SELECT * FROM trabajadores WHERE user_id=? ORDER BY nombre',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    return render_template(
        'metodos/ley_silla/paso1_datos.html',
        trabajadores=[dict(t) for t in trabajadores]
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 2: FACTORES DE RIESGO (7 PREGUNTAS)
# ════════════════════════════════════════════════════════════════════════════════════

@bp_ley_silla.route('/<eval_uuid>/paso2', methods=['GET', 'POST'])
@login_required
def paso_factores(eval_uuid):
    """
    Paso 2: Evaluación de 7 factores de riesgo de bipedestación
    - Tiempo de pie
    - Espacio de desplazamiento
    - Posibilidad de cambio postural
    - Molestias reportadas
    - Tipo de superficie
    - Calzado adecuado
    - Pausas de descanso
    """
    
    # Verificar que la evaluación existe y pertenece al usuario
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('ley_silla.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar datos de evaluación
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['factores'] = datos.get('factores', {})
        
        db.execute(
            'UPDATE evaluaciones SET datos_evaluacion=? WHERE uuid=?',
            (json.dumps(current_data), eval_uuid)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('ley_silla.paso_resultado', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar formulario paso 2
    return render_template(
        'metodos/ley_silla/paso2_factores.html',
        eval_uuid=eval_uuid,
        tiempo_pie_options=get_tiempo_pie_options(),
        superficie_options=get_superficie_options()
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 3: RESULTADO FINAL
# ════════════════════════════════════════════════════════════════════════════════════

@bp_ley_silla.route('/<eval_uuid>/paso3', methods=['GET', 'POST'])
@login_required
def paso_resultado(eval_uuid):
    """
    Paso 3: Calcular resultado Ley Silla y mostrar recomendaciones
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('ley_silla.nueva_evaluacion'))
    
    # Obtener datos de evaluación y calcular
    datos_eval = json.loads(ev['datos_evaluacion'] or '{}')
    factores = datos_eval.get('factores', {})
    
    # Calcular resultado Ley Silla
    resultado = evaluar_ley_silla(factores)
    
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
            'redirect': url_for('descargar_reporte_ley_silla', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar resultado
    return render_template(
        'metodos/ley_silla/paso3_resultado.html',
        eval_uuid=eval_uuid,
        resultado=resultado
    )


# ════════════════════════════════════════════════════════════════════════════════════
# ENDPOINT DE REPORTE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_ley_silla.route('/<eval_uuid>/reporte', methods=['GET'])
@login_required
def descargar_reporte_ley_silla(eval_uuid):
    """
    Descargar reporte Ley Silla en DOCX (placeholder)
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return redirect(url_for('ley_silla.nueva_evaluacion'))
    
    # TODO: Generar DOCX y enviar
    # from reportes.ley_silla_report import LeySillaReport
    # reporte = LeySillaReport(dict(ev))
    # return send_file(...)
    
    return jsonify({
        'message': 'Reporte en construcción',
        'evaluacion_uuid': eval_uuid,
    })
