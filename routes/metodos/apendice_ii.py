"""
routes/metodos/apendice_ii.py - Rutas para Apéndice II: Empuje y Arrastre
Evaluación según NOM-036-1-STPS-2018
"""

import json
import uuid
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from models_apendice_ii import calculate_apendice_ii

# ════════════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ════════════════════════════════════════════════════════════════════════════════════

bp_apendice_ii = Blueprint('apendice_ii', __name__, url_prefix='/apendice-ii')


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

@bp_apendice_ii.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_evaluacion():
    """Paso 1: Crear nueva evaluación Apéndice II"""
    
    if request.method == 'POST':
        datos = request.get_json()
        eval_uuid = str(uuid.uuid4())
        
        db = get_db()
        db.execute('''
            INSERT INTO evaluaciones 
            (uuid, user_id, tipo, trabajador, puesto, area, empresa, razon_social, fecha, sector, estado, datos_generales)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            eval_uuid, session['user_id'], 'apendice_ii',
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
            'redirect': url_for('apendice_ii.paso_parametros', eval_uuid=eval_uuid)
        })
    
    db = get_db()
    trabajadores = db.execute(
        'SELECT * FROM trabajadores WHERE user_id=? ORDER BY nombre',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    return render_template(
        'metodos/apendice_ii/paso1_datos.html',
        trabajadores=[dict(t) for t in trabajadores]
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 2: PARÁMETROS DEL EMPUJE/ARRASTRE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_apendice_ii.route('/<eval_uuid>/paso2', methods=['GET', 'POST'])
@login_required
def paso_parametros(eval_uuid):
    """Paso 2: Parámetros del empuje/arrastre"""
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('apendice_ii.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
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
            'redirect': url_for('apendice_ii.paso_resultado', eval_uuid=eval_uuid)
        })
    
    db.close()
    return render_template(
        'metodos/apendice_ii/paso2_parametros.html',
        eval_uuid=eval_uuid
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 3: RESULTADO FINAL
# ════════════════════════════════════════════════════════════════════════════════════

@bp_apendice_ii.route('/<eval_uuid>/paso3', methods=['GET', 'POST'])
@login_required
def paso_resultado(eval_uuid):
    """Paso 3: Calcular resultado y mostrar análisis"""
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('apendice_ii.nueva_evaluacion'))
    
    datos_eval = json.loads(ev['datos_evaluacion'] or '{}')
    parametros = datos_eval.get('parametros', {})
    resultado = calculate_apendice_ii(parametros)
    
    if request.method == 'POST':
        db.execute('''
            UPDATE evaluaciones 
            SET datos_calculo=?, resultado_final=?, estado='completada', completada_at=?
            WHERE uuid=?
        ''', (
            json.dumps(resultado), json.dumps(resultado),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            eval_uuid
        ))
        db.commit()
        db.close()
        
        return jsonify({'success': True, 'redirect': url_for('descargar_reporte_apendice_ii', eval_uuid=eval_uuid)})
    
    db.close()
    return render_template(
        'metodos/apendice_ii/paso3_resultado.html',
        eval_uuid=eval_uuid, resultado=resultado
    )


# ════════════════════════════════════════════════════════════════════════════════════
# ENDPOINT DE REPORTE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_apendice_ii.route('/<eval_uuid>/reporte', methods=['GET'])
@login_required
def descargar_reporte_apendice_ii(eval_uuid):
    """Descargar reporte Apéndice II"""
    
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return redirect(url_for('apendice_ii.nueva_evaluacion'))
    
    return jsonify({'message': 'Reporte en construcción', 'evaluacion_uuid': eval_uuid})
