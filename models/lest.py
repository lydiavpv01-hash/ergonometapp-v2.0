"""
models/lest.py - LEST (List of Ergonomic Tasks)
Evaluación multidimensional de tareas ergonómicas
Extractor de app.py, refactorizado para v2
"""


# ════════════════════════════════════════════════════════════════════════════════════
# NIVELES DE LEST (escala 0-10)
# ════════════════════════════════════════════════════════════════════════════════════

LEST_NIVELES = [
    (2, 'Satisfactorio', '#27ae60', 'green'),              # Verde - OK
    (4, 'Débilmente molesto', '#2ecc71', 'success'),       # Verde claro
    (5, 'Medianamente molesto', '#f39c12', 'warning'),     # Amarillo
    (6, 'Muy molesto', '#e67e22', 'warning'),              # Naranja
    (8, 'Nocivo a largo plazo', '#e74c3c', 'danger'),      # Rojo
    (10, 'Nocivo a corto plazo', '#8e44ad', 'danger'),     # Púrpura
]


def get_lest_nivel(score: float) -> dict:
    """
    Clasifica una puntuación LEST en su correspondiente nivel
    
    Args:
        score: Puntuación (0-10)
    
    Returns:
        Dict con {label, color, badge, score}
    """
    for threshold, label, color, badge in LEST_NIVELES:
        if score <= threshold:
            return {
                'label': label,
                'color': color,
                'badge': badge,
                'score': round(score, 1)
            }
    return {
        'label': 'Nocivo a corto plazo',
        'color': '#8e44ad',
        'badge': 'danger',
        'score': round(score, 1)
    }


# ════════════════════════════════════════════════════════════════════════════════════
# ESCALA DE PREGUNTAS (0-4 o 0-5 por factor)
# ════════════════════════════════════════════════════════════════════════════════════

def get_escala_opciones(num_opciones: int = 4):
    """
    Devuelve opciones de escala para cada pregunta
    
    Args:
        num_opciones: 4 o 5 opciones
    
    Returns:
        Lista de tuplas (valor, descripción)
    """
    if num_opciones == 4:
        return [
            (0, 'No'),
            (2, 'Sí, a veces'),
            (4, 'Sí, frecuentemente'),
            (6, 'Sí, siempre'),
        ]
    else:  # 5 opciones
        return [
            (0, 'No/Excelente'),
            (1, 'Apenas'),
            (2, 'Moderadamente'),
            (3, 'Considerablemente'),
            (4, 'Extremadamente'),
        ]


# ════════════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL DE CÁLCULO
# ════════════════════════════════════════════════════════════════════════════════════

def calculate_lest(data: dict) -> dict:
    """
    Calcula LEST completo con 5 dimensiones
    
    Args:
        data: Dict con scores de 16 preguntas
        {
            'postura': 1-6,           # Carga Física
            'esfuerzo': 1-6,
            'manipulacion': 1-6,
            
            'temperatura': 0-4,       # Entorno
            'ruido': 0-4,
            'iluminacion': 0-4,
            'vibraciones': 0-4,
            
            'atencion': 1-6,          # Carga Mental
            'complejidad': 1-6,
            'minuciosidad': 1-6,
            
            'iniciativa': 0-4,        # Psicosocial
            'comunicacion': 0-4,
            'relaciones': 0-4,
            'cooperacion': 0-4,
            
            'pausas': 0-4,            # Tiempo de Trabajo
            'horario': 0-4,
            'rotacion': 0-4,
            'ritmo': 0-4,
        }
    
    Returns:
        Dict con scores y niveles de cada dimensión + global
    """
    
    results = {}
    
    # ════════════════════════════════════════════════════════════════════════════════
    # DIMENSIÓN 1: CARGA FÍSICA (3 factores)
    # ════════════════════════════════════════════════════════════════════════════════
    
    postura_score = float(data.get('postura', 3))
    esfuerzo_score = float(data.get('esfuerzo', 3))
    manipulacion_score = float(data.get('manipulacion', 2))
    
    carga_fisica = (postura_score + esfuerzo_score + manipulacion_score) / 3
    carga_fisica = min(10, max(0, carga_fisica))  # Clamp 0-10
    
    results['carga_fisica'] = {
        'score': round(carga_fisica, 2),
        'factores': {
            'postura': {'valor': postura_score, 'peso': 0.33},
            'esfuerzo': {'valor': esfuerzo_score, 'peso': 0.33},
            'manipulacion': {'valor': manipulacion_score, 'peso': 0.34},
        },
        **get_lest_nivel(carga_fisica)
    }
    
    # ════════════════════════════════════════════════════════════════════════════════
    # DIMENSIÓN 2: ENTORNO FÍSICO (4 factores)
    # ════════════════════════════════════════════════════════════════════════════════
    
    temperatura_score = float(data.get('temperatura', 2))
    ruido_score = float(data.get('ruido', 2))
    iluminacion_score = float(data.get('iluminacion', 2))
    vibraciones_score = float(data.get('vibraciones', 1))
    
    # Convertir escala 0-4 a 0-10
    temperatura_score = (temperatura_score / 4) * 10
    ruido_score = (ruido_score / 4) * 10
    iluminacion_score = (iluminacion_score / 4) * 10
    vibraciones_score = (vibraciones_score / 4) * 10
    
    entorno = (temperatura_score + ruido_score + iluminacion_score + vibraciones_score) / 4
    entorno = min(10, max(0, entorno))
    
    results['entorno'] = {
        'score': round(entorno, 2),
        'factores': {
            'temperatura': {'valor': round(temperatura_score, 2), 'peso': 0.25},
            'ruido': {'valor': round(ruido_score, 2), 'peso': 0.25},
            'iluminacion': {'valor': round(iluminacion_score, 2), 'peso': 0.25},
            'vibraciones': {'valor': round(vibraciones_score, 2), 'peso': 0.25},
        },
        **get_lest_nivel(entorno)
    }
    
    # ════════════════════════════════════════════════════════════════════════════════
    # DIMENSIÓN 3: CARGA MENTAL (3 factores)
    # ════════════════════════════════════════════════════════════════════════════════
    
    atencion_score = float(data.get('atencion', 3))
    complejidad_score = float(data.get('complejidad', 2))
    minuciosidad_score = float(data.get('minuciosidad', 2))
    
    carga_mental = (atencion_score + complejidad_score + minuciosidad_score) / 3
    carga_mental = min(10, max(0, carga_mental))
    
    results['carga_mental'] = {
        'score': round(carga_mental, 2),
        'factores': {
            'atencion': {'valor': atencion_score, 'peso': 0.33},
            'complejidad': {'valor': complejidad_score, 'peso': 0.33},
            'minuciosidad': {'valor': minuciosidad_score, 'peso': 0.34},
        },
        **get_lest_nivel(carga_mental)
    }
    
    # ════════════════════════════════════════════════════════════════════════════════
    # DIMENSIÓN 4: ASPECTOS PSICOSOCIALES (4 factores)
    # ════════════════════════════════════════════════════════════════════════════════
    
    iniciativa_score = float(data.get('iniciativa', 2))
    comunicacion_score = float(data.get('comunicacion', 2))
    relaciones_score = float(data.get('relaciones', 2))
    cooperacion_score = float(data.get('cooperacion', 2))
    
    # Convertir escala 0-4 a 0-10
    iniciativa_score = (iniciativa_score / 4) * 10
    comunicacion_score = (comunicacion_score / 4) * 10
    relaciones_score = (relaciones_score / 4) * 10
    cooperacion_score = (cooperacion_score / 4) * 10
    
    psicosocial = (iniciativa_score + comunicacion_score + relaciones_score + cooperacion_score) / 4
    psicosocial = min(10, max(0, psicosocial))
    
    results['psicosocial'] = {
        'score': round(psicosocial, 2),
        'factores': {
            'iniciativa': {'valor': round(iniciativa_score, 2), 'peso': 0.25},
            'comunicacion': {'valor': round(comunicacion_score, 2), 'peso': 0.25},
            'relaciones': {'valor': round(relaciones_score, 2), 'peso': 0.25},
            'cooperacion': {'valor': round(cooperacion_score, 2), 'peso': 0.25},
        },
        **get_lest_nivel(psicosocial)
    }
    
    # ════════════════════════════════════════════════════════════════════════════════
    # DIMENSIÓN 5: TIEMPO DE TRABAJO (4 factores)
    # ════════════════════════════════════════════════════════════════════════════════
    
    pausas_score = float(data.get('pausas', 2))
    horario_score = float(data.get('horario', 2))
    rotacion_score = float(data.get('rotacion', 1))
    ritmo_score = float(data.get('ritmo', 3))
    
    # Convertir escala 0-4 a 0-10
    pausas_score = (pausas_score / 4) * 10
    horario_score = (horario_score / 4) * 10
    rotacion_score = (rotacion_score / 4) * 10
    ritmo_score = (ritmo_score / 4) * 10
    
    tiempo_trabajo = (pausas_score + horario_score + rotacion_score + ritmo_score) / 4
    tiempo_trabajo = min(10, max(0, tiempo_trabajo))
    
    results['tiempo_trabajo'] = {
        'score': round(tiempo_trabajo, 2),
        'factores': {
            'pausas': {'valor': round(pausas_score, 2), 'peso': 0.25},
            'horario': {'valor': round(horario_score, 2), 'peso': 0.25},
            'rotacion': {'valor': round(rotacion_score, 2), 'peso': 0.25},
            'ritmo': {'valor': round(ritmo_score, 2), 'peso': 0.25},
        },
        **get_lest_nivel(tiempo_trabajo)
    }
    
    # ════════════════════════════════════════════════════════════════════════════════
    # SCORE GLOBAL (promedio ponderado de 5 dimensiones)
    # ════════════════════════════════════════════════════════════════════════════════
    # Pesos según NOM-036-1-STPS-2018 y prioridades de bipedestación
    
    global_score = (
        carga_fisica * 0.30 +        # Carga Física: 30% (prioritaria)
        entorno * 0.15 +             # Entorno: 15%
        carga_mental * 0.15 +        # Carga Mental: 15%
        psicosocial * 0.15 +         # Psicosocial: 15%
        tiempo_trabajo * 0.25        # Tiempo: 25% (prioritaria)
    )
    global_score = min(10, max(0, global_score))
    global_nivel = get_lest_nivel(global_score)
    
    results['global'] = {
        'score': round(global_score, 2),
        'pesos': {
            'carga_fisica': 0.30,
            'entorno': 0.15,
            'carga_mental': 0.15,
            'psicosocial': 0.15,
            'tiempo_trabajo': 0.25,
        },
        **global_nivel
    }
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RECOMENDACIONES POR DIMENSIÓN
    # ════════════════════════════════════════════════════════════════════════════════
    
    recomendaciones = []
    
    # Por Carga Física
    if carga_fisica >= 6:
        recomendaciones.append('🏋️ CARGA FÍSICA: Rediseñar puesto, implementar descansos frecuentes')
    elif carga_fisica >= 4:
        recomendaciones.append('🏋️ CARGA FÍSICA: Optimizar posturas y ergonomía del puesto')
    
    # Por Entorno
    if entorno >= 6:
        recomendaciones.append('🌡️ ENTORNO: Mejorar condiciones (temperatura, ruido, luz, vibraciones)')
    elif entorno >= 4:
        recomendaciones.append('🌡️ ENTORNO: Realizar ajustes en ambiente de trabajo')
    
    # Por Carga Mental
    if carga_mental >= 6:
        recomendaciones.append('🧠 CARGA MENTAL: Reducir complejidad, mejorar claridad de tareas')
    elif carga_mental >= 4:
        recomendaciones.append('🧠 CARGA MENTAL: Organizar mejor el flujo de trabajo')
    
    # Por Psicosocial
    if psicosocial >= 6:
        recomendaciones.append('👥 PSICOSOCIAL: Mejorar comunicación y relaciones laborales')
    elif psicosocial >= 4:
        recomendaciones.append('👥 PSICOSOCIAL: Fortalecer aspectos de cooperación')
    
    # Por Tiempo
    if tiempo_trabajo >= 6:
        recomendaciones.append('⏰ TIEMPO: Implementar pausas, mejorar horario, reducir ritmo')
    elif tiempo_trabajo >= 4:
        recomendaciones.append('⏰ TIEMPO: Aumentar pausas y mejorar rotación de tareas')
    
    results['recomendaciones'] = recomendaciones
    
    return results


# ════════════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ════════════════════════════════════════════════════════════════════════════════════

def get_factor_descripcion(factor: str, valor: int) -> str:
    """
    Devuelve descripción según factor y valor
    
    Args:
        factor: Nombre del factor (ej: 'postura', 'ruido', etc)
        valor: Valor numérico (1-6 o 0-4)
    
    Returns:
        Descripción legible
    """
    descripciones = {
        'postura': {
            1: 'Postura neutral, sin riesgo',
            2: 'Postura aceptable',
            3: 'Postura incómoda',
            4: 'Postura muy incómoda',
            5: 'Postura extremadamente incómoda',
            6: 'Postura peligrosa',
        },
        'esfuerzo': {
            1: 'Sin esfuerzo significativo',
            2: 'Esfuerzo ligero',
            3: 'Esfuerzo moderado',
            4: 'Esfuerzo considerable',
            5: 'Esfuerzo muy alto',
            6: 'Esfuerzo extremo',
        },
        'temperatura': {
            0: 'Temperatura confortable',
            1: 'Temperatura ligeramente incómoda',
            2: 'Temperatura incómoda',
            3: 'Temperatura muy incómoda',
            4: 'Temperatura extremadamente incómoda',
        },
        'ruido': {
            0: 'Sin ruido molesto',
            1: 'Ruido ligero',
            2: 'Ruido moderado',
            3: 'Ruido alto',
            4: 'Ruido muy alto',
        },
    }
    
    if factor in descripciones:
        return descripciones[factor].get(valor, f'Valor {valor}')
    return f'{factor}: {valor}'
