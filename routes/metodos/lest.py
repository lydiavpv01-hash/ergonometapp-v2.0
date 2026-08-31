"""
routes/metodos/lest.py - Rutas para evaluación LEST (4 pasos)
Método multidimensional de 5 dimensiones
"""

import json
import uuid
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from models_lest import calculate_lest, get_lest_nivel, get_escala_opciones

# ════════════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ════════════════════════════════════════════════════════════════════════════════════

bp_lest = Blueprint('lest', __name__, url_prefix='/lest')


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

@bp_lest.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_evaluacion():
    """
    Paso 1: Crear nueva evaluación LEST - Datos generales
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
            'lest',
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
            'redirect': url_for('lest.paso_carga_entorno', eval_uuid=eval_uuid)
        })
    
    # GET: Renderizar formulario paso 1
    db = get_db()
    trabajadores = db.execute(
        'SELECT * FROM trabajadores WHERE user_id=? ORDER BY nombre',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    return render_template(
        'metodos/lest/paso1_datos.html',
        trabajadores=[dict(t) for t in trabajadores]
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 2: CARGA FÍSICA + ENTORNO
# ════════════════════════════════════════════════════════════════════════════════════

@bp_lest.route('/<eval_uuid>/paso2', methods=['GET', 'POST'])
@login_required
def paso_carga_entorno(eval_uuid):
    """
    Paso 2: Dimensiones 1 y 2 de LEST
    - Carga Física (3 factores: postura, esfuerzo, manipulación)
    - Entorno Físico (4 factores: temperatura, ruido, iluminación, vibraciones)
    """
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('lest.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar datos de paso 2
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['paso2'] = datos.get('paso2', {})
        
        db.execute(
            'UPDATE evaluaciones SET datos_evaluacion=? WHERE uuid=?',
            (json.dumps(current_data), eval_uuid)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('lest.paso_mental_psico', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar paso 2
    return render_template(
        'metodos/lest/paso2_carga_entorno.html',
        eval_uuid=eval_uuid,
        escala_6=get_escala_opciones(5)[:6],  # 0-5
        escala_4=get_escala_opciones(4)       # 0-4
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 3: CARGA MENTAL + PSICOSOCIAL
# ════════════════════════════════════════════════════════════════════════════════════

@bp_lest.route('/<eval_uuid>/paso3', methods=['GET', 'POST'])
@login_required
def paso_mental_psico(eval_uuid):
    """
    Paso 3: Dimensiones 3 y 4 de LEST
    - Carga Mental (3 factores: atención, complejidad, minuciosidad)
    - Aspectos Psicosociales (4 factores: iniciativa, comunicación, relaciones, cooperación)
    """
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('lest.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar datos de paso 3
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['paso3'] = datos.get('paso3', {})
        
        db.execute(
            'UPDATE evaluaciones SET datos_evaluacion=? WHERE uuid=?',
            (json.dumps(current_data), eval_uuid)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('lest.paso_tiempo_resultado', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar paso 3
    return render_template(
        'metodos/lest/paso3_mental_psico.html',
        eval_uuid=eval_uuid,
        escala_6=get_escala_opciones(5)[:6],
        escala_4=get_escala_opciones(4)
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 4: TIEMPO DE TRABAJO + RESULTADO
# ════════════════════════════════════════════════════════════════════════════════════

@bp_lest.route('/<eval_uuid>/paso4', methods=['GET', 'POST'])
@login_required
def paso_tiempo_resultado(eval_uuid):
    """
    Paso 4: Dimensión 5 + Resultado final
    - Tiempo de Trabajo (4 factores: pausas, horario, rotación, ritmo)
    - Resultado global
    """
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('lest.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Obtener todos los datos
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['paso4'] = datos.get('paso4', {})
        
        # Construir dict para calculate_lest
        lest_data = {
            # Paso 2: Carga Física
            'postura': int(current_data.get('paso2', {}).get('postura', 3)),
            'esfuerzo': int(current_data.get('paso2', {}).get('esfuerzo', 3)),
            'manipulacion': int(current_data.get('paso2', {}).get('manipulacion', 2)),
            
            # Paso 2: Entorno
            'temperatura': int(current_data.get('paso2', {}).get('temperatura', 2)),
            'ruido': int(current_data.get('paso2', {}).get('ruido', 2)),
            'iluminacion': int(current_data.get('paso2', {}).get('iluminacion', 2)),
            'vibraciones': int(current_data.get('paso2', {}).get('vibraciones', 1)),
            
            # Paso 3: Carga Mental
            'atencion': int(current_data.get('paso3', {}).get('atencion', 3)),
            'complejidad': int(current_data.get('paso3', {}).get('complejidad', 2)),
            'minuciosidad': int(current_data.get('paso3', {}).get('minuciosidad', 2)),
            
            # Paso 3: Psicosocial
            'iniciativa': int(current_data.get('paso3', {}).get('iniciativa', 2)),
            'comunicacion': int(current_data.get('paso3', {}).get('comunicacion', 2)),
            'relaciones': int(current_data.get('paso3', {}).get('relaciones', 2)),
            'cooperacion': int(current_data.get('paso3', {}).get('cooperacion', 2)),
            
            # Paso 4: Tiempo de Trabajo
            'pausas': int(current_data.get('paso4', {}).get('pausas', 2)),
            'horario': int(current_data.get('paso4', {}).get('horario', 2)),
            'rotacion': int(current_data.get('paso4', {}).get('rotacion', 1)),
            'ritmo': int(current_data.get('paso4', {}).get('ritmo', 3)),
        }
        
        # Calcular LEST
        resultado = calculate_lest(lest_data)
        
        # Guardar en BD
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
            'resultado': resultado,
            'redirect': url_for('descargar_reporte_lest', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar paso 4 (formulario + resultado si existe)
    return render_template(
        'metodos/lest/paso4_tiempo_resultado.html',
        eval_uuid=eval_uuid,
        escala_4=get_escala_opciones(4)
    )


# ════════════════════════════════════════════════════════════════════════════════════
# ENDPOINT DE REPORTE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_lest.route('/<eval_uuid>/reporte', methods=['GET'])
@login_required
def descargar_reporte_lest(eval_uuid):
    """
    Descargar reporte LEST en DOCX (placeholder)
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return redirect(url_for('lest.nueva_evaluacion'))
    
    # TODO: Generar DOCX y enviar
    # from reportes.lest_report import LeSTReport
    # reporte = LeSTReport(dict(ev))
    # return send_file(...)
    
    return jsonify({
        'message': 'Reporte en construcción',
        'evaluacion_uuid': eval_uuid,
    })
