"""
routes/metodos/reba.py - Rutas para evaluación REBA (5 pasos)
Integrated Kinovea para medición de ángulos en Grupo A y B
"""

import json
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

from models_calculadores import calculate_reba
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

# ════════════════════════════════════════════════════════════════════════════════════
# BLUEPRINT SETUP
# ════════════════════════════════════════════════════════════════════════════════════

bp_reba = Blueprint('reba', __name__, url_prefix='/reba')


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

@bp_reba.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva_evaluacion():
    """
    Paso 1: Crear nueva evaluación REBA - Datos generales
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
            'reba',
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
            'redirect': url_for('reba.paso_grupo_a', eval_uuid=eval_uuid)
        })
    
    # GET: Renderizar formulario paso 1
    db = get_db()
    trabajadores = db.execute(
        'SELECT * FROM trabajadores WHERE user_id=? ORDER BY nombre',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    return render_template(
        'metodos/reba/paso1_datos.html',
        trabajadores=[dict(t) for t in trabajadores]
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 2: GRUPO A (Cuello, Torso, Piernas)
# ════════════════════════════════════════════════════════════════════════════════════

@bp_reba.route('/<eval_uuid>/paso2', methods=['GET', 'POST'])
@login_required
def paso_grupo_a(eval_uuid):
    """
    Paso 2: Evaluación Grupo A (Cuello, Torso, Piernas)
    Incluye integración con Kinovea para medición de ángulos
    """
    # Verificar que la evaluación existe y pertenece al usuario
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('reba.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar datos de Grupo A
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['grupo_a'] = datos.get('grupo_a', {})
        
        db.execute(
            'UPDATE evaluaciones SET datos_evaluacion=? WHERE uuid=?',
            (json.dumps(current_data), eval_uuid)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('reba.paso_grupo_b', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar formulario paso 2
    return render_template(
        'metodos/reba/paso2_grupoA.html',
        eval_uuid=eval_uuid
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 3: GRUPO B (Brazo, Antebrazo, Muñeca)
# ════════════════════════════════════════════════════════════════════════════════════

@bp_reba.route('/<eval_uuid>/paso3', methods=['GET', 'POST'])
@login_required
def paso_grupo_b(eval_uuid):
    """
    Paso 3: Evaluación Grupo B (Brazo, Antebrazo, Muñeca)
    También con Kinovea integrado
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('reba.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar datos de Grupo B
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['grupo_b'] = datos.get('grupo_b', {})
        
        db.execute(
            'UPDATE evaluaciones SET datos_evaluacion=? WHERE uuid=?',
            (json.dumps(current_data), eval_uuid)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('reba.paso_carga_agarre', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar formulario paso 3
    return render_template(
        'metodos/reba/paso3_grupoB.html',
        eval_uuid=eval_uuid
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 4: CARGA Y AGARRE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_reba.route('/<eval_uuid>/paso4', methods=['GET', 'POST'])
@login_required
def paso_carga_agarre(eval_uuid):
    """
    Paso 4: Análisis de Carga (peso) y Agarre (tipo de agarre)
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('reba.nueva_evaluacion'))
    
    if request.method == 'POST':
        datos = request.get_json()
        
        # Guardar datos de carga y agarre
        current_data = json.loads(ev['datos_evaluacion'] or '{}')
        current_data['carga'] = datos.get('carga', {})
        current_data['agarre'] = datos.get('agarre', {})
        
        db.execute(
            'UPDATE evaluaciones SET datos_evaluacion=? WHERE uuid=?',
            (json.dumps(current_data), eval_uuid)
        )
        db.commit()
        db.close()
        
        return jsonify({
            'success': True,
            'redirect': url_for('reba.paso_resultado', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar formulario paso 4
    return render_template(
        'metodos/reba/paso4_carga_agarre.html',
        eval_uuid=eval_uuid
    )


# ════════════════════════════════════════════════════════════════════════════════════
# PASO 5: RESULTADO FINAL
# ════════════════════════════════════════════════════════════════════════════════════

@bp_reba.route('/<eval_uuid>/paso5', methods=['GET', 'POST'])
@login_required
def paso_resultado(eval_uuid):
    """
    Paso 5: Calcular resultado REBA y mostrar conclusiones
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    
    if not ev:
        db.close()
        return redirect(url_for('reba.nueva_evaluacion'))
    
    # Obtener datos de evaluación y calcular
    datos_eval = json.loads(ev['datos_evaluacion'] or '{}')
    resultado = calculate_reba(datos_eval)
    
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
            'redirect': url_for('descargar_reporte_reba', eval_uuid=eval_uuid)
        })
    
    db.close()
    
    # GET: Renderizar resultado
    return render_template(
        'metodos/reba/paso5_resultado.html',
        eval_uuid=eval_uuid,
        resultado=resultado
    )


# ════════════════════════════════════════════════════════════════════════════════════
# ENDPOINTS DE SOPORTE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_reba.route('/<eval_uuid>/api/subir-imagen', methods=['POST'])
@login_required
def subir_imagen(eval_uuid):
    """
    Subir imagen para REBA (posturas de referencia)
    """
    # Verificar que la evaluación existe
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return jsonify({'error': 'Evaluación no encontrada'}), 404
    
    # Obtener archivo
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se subió archivo'}), 400
    
    file = request.files['imagen']
    if file.filename == '':
        return jsonify({'error': 'Archivo vacío'}), 400
    
    # Validar extensión
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    # Crear carpeta para la evaluación
    eval_folder = UPLOAD_FOLDER / eval_uuid
    eval_folder.mkdir(exist_ok=True)
    
    # Guardar archivo con nombre seguro
    filename = secure_filename(file.filename)
    filepath = eval_folder / filename
    file.save(str(filepath))
    
    # Registrar en BD
    db = get_db()
    db.execute('''
        INSERT INTO imagenes_evaluacion 
        (evaluacion_uuid, tipo_imagen, ruta_archivo, nombre_original, descripcion)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        eval_uuid,
        request.form.get('tipo', 'general'),
        f'/uploads/{eval_uuid}/{filename}',
        filename,
        request.form.get('descripcion', '')
    ))
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'ruta': f'/uploads/{eval_uuid}/{filename}'
    })


@bp_reba.route('/<eval_uuid>/api/kinovea-medicion', methods=['POST'])
@login_required
def guardar_medicion_kinovea(eval_uuid):
    """
    Guardar medición de ángulos de Kinovea
    Datos: {angulo, tipo_medicion, zona, imagen_base64}
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return jsonify({'error': 'Evaluación no encontrada'}), 404
    
    datos = request.get_json()
    
    # Guardar metadatos de medición en BD
    db = get_db()
    db.execute('''
        INSERT INTO imagenes_evaluacion 
        (evaluacion_uuid, tipo_imagen, ruta_archivo, metadata)
        VALUES (?, ?, ?, ?)
    ''', (
        eval_uuid,
        'medicion_angulo',
        f'/mediciones/{eval_uuid}/{uuid.uuid4().hex[:8]}.json',
        json.dumps({
            'angulo': datos.get('angulo'),
            'tipo': datos.get('tipo_medicion'),
            'zona': datos.get('zona'),
            'timestamp': datetime.now().isoformat()
        })
    ))
    db.commit()
    db.close()
    
    return jsonify({'success': True})


# ════════════════════════════════════════════════════════════════════════════════════
# ENDPOINT TEMPORAL PARA REPORTE
# ════════════════════════════════════════════════════════════════════════════════════

@bp_reba.route('/<eval_uuid>/reporte', methods=['GET'])
@login_required
def descargar_reporte_reba(eval_uuid):
    """
    Descargar reporte REBA en DOCX (placeholder - se implementa en reportes/reba_report.py)
    """
    db = get_db()
    ev = db.execute(
        'SELECT * FROM evaluaciones WHERE uuid=? AND user_id=?',
        (eval_uuid, session['user_id'])
    ).fetchone()
    db.close()
    
    if not ev:
        return redirect(url_for('reba.nueva_evaluacion'))
    
    # TODO: Generar DOCX y enviar
    # from reportes.reba_report import RebaReport
    # reporte = RebaReport(dict(ev))
    # return send_file(...)
    
    return jsonify({
        'message': 'Reporte en construcción',
        'evaluacion_uuid': eval_uuid,
        'resultado_final': dict(ev)['resultado_final']
    })
