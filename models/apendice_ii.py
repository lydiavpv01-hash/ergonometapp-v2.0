"""
models/apendice_ii.py - APÉNDICE II: EMPUJE Y ARRASTRE DE CARGAS
Evaluación de tareas de empuje/arrastre según NOM-036-1-STPS-2018
"""


def calculate_apendice_ii(data: dict) -> dict:
    """
    Calcula índice de empuje/arrastre según ACGIH (NOM-036 Apéndice II)
    
    Fórmula: PSI (Push/Pull Strain Index) = 
      (Fuerza Inicial / RWL Inicial) × (Frecuencia / 2) × (Duración / 1)
    
    Args:
        data: Dict con parámetros de la tarea
        {
            'tipo': 'empuje' o 'arrastre',
            'fuerza_inicial': float (kg),     # Fuerza para iniciar movimiento
            'fuerza_sostenida': float (kg),   # Fuerza para mantener movimiento
            'distancia': float (metros),      # Distancia recorrida
            'altura_agarre': float (cm),      # Altura del agarre
            'frecuencia': float (acciones/min), # Acciones por minuto
            'duracion': float (horas),        # Duración de la tarea
            'superficie': str,                # 'lisa', 'moderada', 'rugosa'
        }
    
    Returns:
        Dict con scores, análisis y recomendaciones
    """
    
    # ════════════════════════════════════════════════════════════════════════════════
    # EXTRACCIÓN DE PARÁMETROS
    # ════════════════════════════════════════════════════════════════════════════════
    
    tipo = str(data.get('tipo', 'empuje')).lower()  # empuje/arrastre
    fuerza_inicial = float(data.get('fuerza_inicial', 20))      # kg
    fuerza_sostenida = float(data.get('fuerza_sostenida', 10))  # kg
    distancia = float(data.get('distancia', 3))                 # metros
    altura_agarre = float(data.get('altura_agarre', 100))       # cm
    frecuencia = float(data.get('frecuencia', 5))               # acciones/min
    duracion = float(data.get('duracion', 1))                   # horas
    superficie = str(data.get('superficie', 'moderada')).lower()  # lisa/moderada/rugosa
    
    # ════════════════════════════════════════════════════════════════════════════════
    # LÍMITES RECOMENDADOS (RWL)
    # ════════════════════════════════════════════════════════════════════════════════
    
    # Tabla de RWL según altura del agarre
    # Altura 65-95 cm (espalda baja), 95-125 cm (mano), 125-180 cm (hombro)
    
    if altura_agarre < 65:
        altura_cat = 'baja'
        rwl_inicial_lisa = 22.2      # kg
        rwl_inicial_moderada = 13.3
        rwl_inicial_rugosa = 8.9
        rwl_sostenida_lisa = 17.8
        rwl_sostenida_moderada = 11.1
        rwl_sostenida_rugosa = 8.9
    elif altura_agarre < 95:
        altura_cat = 'espalda_baja'
        rwl_inicial_lisa = 22.2
        rwl_inicial_moderada = 13.3
        rwl_inicial_rugosa = 8.9
        rwl_sostenida_lisa = 17.8
        rwl_sostenida_moderada = 11.1
        rwl_sostenida_rugosa = 8.9
    elif altura_agarre < 125:
        altura_cat = 'mano'
        rwl_inicial_lisa = 34.4
        rwl_inicial_moderada = 22.2
        rwl_inicial_rugosa = 11.1
        rwl_sostenida_lisa = 29.9
        rwl_sostenida_moderada = 20.0
        rwl_sostenida_rugosa = 11.1
    else:
        altura_cat = 'hombro'
        rwl_inicial_lisa = 13.3
        rwl_inicial_moderada = 8.9
        rwl_inicial_rugosa = 4.4
        rwl_sostenida_lisa = 11.1
        rwl_sostenida_moderada = 8.9
        rwl_sostenida_rugosa = 4.4
    
    # Seleccionar RWL según superficie
    if superficie == 'lisa':
        rwl_inicial = rwl_inicial_lisa
        rwl_sostenida = rwl_sostenida_lisa
    elif superficie == 'rugosa':
        rwl_inicial = rwl_inicial_rugosa
        rwl_sostenida = rwl_sostenida_rugosa
    else:  # moderada
        rwl_inicial = rwl_inicial_moderada
        rwl_sostenida = rwl_sostenida_moderada
    
    # ════════════════════════════════════════════════════════════════════════════════
    # CÁLCULO DE ÍNDICES DE ESFUERZO
    # ════════════════════════════════════════════════════════════════════════════════
    
    # Índice de esfuerzo inicial
    if rwl_inicial > 0:
        indice_inicial = fuerza_inicial / rwl_inicial
    else:
        indice_inicial = 999
    
    # Índice de esfuerzo sostenido
    if rwl_sostenida > 0:
        indice_sostenido = fuerza_sostenida / rwl_sostenida
    else:
        indice_sostenido = 999
    
    # Índice de frecuencia
    frecuencia_limite = get_frecuencia_limite(altura_agarre)
    indice_frecuencia = frecuencia / frecuencia_limite if frecuencia_limite > 0 else 0
    
    # Índice de duración
    if duracion <= 1:
        indice_duracion = 1.0
    elif duracion <= 4:
        indice_duracion = 1 + (duracion - 1) * 0.2
    else:
        indice_duracion = 1.6
    
    # Índice de distancia
    if distancia <= 1:
        indice_distancia = 1.0
    elif distancia <= 5:
        indice_distancia = 1 + (distancia - 1) * 0.1
    else:
        indice_distancia = 1.4
    
    # Índice compuesto de esfuerzo
    indice_esfuerzo = (indice_inicial + indice_sostenido) / 2 * indice_frecuencia * indice_duracion * indice_distancia
    
    # ════════════════════════════════════════════════════════════════════════════════
    # CLASIFICACIÓN DE RIESGO
    # ════════════════════════════════════════════════════════════════════════════════
    
    if indice_esfuerzo <= 1.0:
        nivel_riesgo = 'BAJO'
        color = '#27ae60'
        badge = 'success'
        descripcion = 'Tarea segura - Riesgo aceptable para la mayoría de trabajadores'
        accion = 'Mantener vigilancia'
    elif indice_esfuerzo <= 1.5:
        nivel_riesgo = 'LIGERO'
        color = '#2ecc71'
        badge = 'info'
        descripcion = 'Riesgo ligero - Algunos trabajadores pueden sufrir lesiones'
        accion = 'Vigilancia aumentada'
    elif indice_esfuerzo <= 2.5:
        nivel_riesgo = 'MODERADO'
        color = '#f39c12'
        badge = 'warning'
        descripcion = 'Riesgo moderado - Intervención recomendada'
        accion = 'Intervención necesaria'
    else:
        nivel_riesgo = 'ALTO'
        color = '#e74c3c'
        badge = 'danger'
        descripcion = 'Riesgo elevado - Intervención inmediata requerida'
        accion = 'Intervención urgente'
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RECOMENDACIONES
    # ════════════════════════════════════════════════════════════════════════════════
    
    recomendaciones = []
    
    if fuerza_inicial > rwl_inicial:
        recomendaciones.append(
            '💪 FUERZA INICIAL: Reducir fuerza de inicio (usar equipos, lubricantes, etc.)'
        )
    
    if fuerza_sostenida > rwl_sostenida:
        recomendaciones.append(
            '💪 FUERZA SOSTENIDA: Reducir fuerza de mantenimiento'
        )
    
    if frecuencia > frecuencia_limite:
        recomendaciones.append(
            '⏱️ FRECUENCIA: Reducir número de acciones por minuto'
        )
    
    if duracion > 1:
        recomendaciones.append(
            '⏳ DURACIÓN: Aumentar pausas o reducir tiempo de tarea'
        )
    
    if distancia > 3:
        recomendaciones.append(
            '📏 DISTANCIA: Si es posible, reducir distancia de recorrido'
        )
    
    if altura_agarre < 65 or altura_agarre > 125:
        recomendaciones.append(
            '📍 ALTURA: Optimizar altura del agarre (ideal: 95-125 cm)'
        )
    
    if indice_esfuerzo > 1:
        recomendaciones.append(
            '🔧 REDISEÑO: Considerar equipos de asistencia, rampas, rodillos, etc.'
        )
    
    if not recomendaciones:
        recomendaciones.append('✓ Tarea dentro de límites aceptables - Mantener vigilancia')
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RESULTADO FINAL
    # ════════════════════════════════════════════════════════════════════════════════
    
    return {
        # Datos de entrada
        'tipo': tipo,
        'fuerza_inicial': fuerza_inicial,
        'fuerza_sostenida': fuerza_sostenida,
        'distancia': distancia,
        'altura_agarre': altura_agarre,
        'frecuencia': frecuencia,
        'duracion': duracion,
        'superficie': superficie,
        
        # Categorización
        'altura_categoria': altura_cat,
        
        # Límites recomendados
        'rwl': {
            'inicial': round(rwl_inicial, 2),
            'sostenida': round(rwl_sostenida, 2),
        },
        
        # Índices
        'indices': {
            'inicial': round(indice_inicial, 2),
            'sostenido': round(indice_sostenido, 2),
            'frecuencia': round(indice_frecuencia, 2),
            'duracion': round(indice_duracion, 2),
            'distancia': round(indice_distancia, 2),
        },
        
        # Resultado
        'indice_esfuerzo': round(indice_esfuerzo, 2),
        'nivel_riesgo': nivel_riesgo,
        'color': color,
        'badge': badge,
        'descripcion': descripcion,
        'accion': accion,
        
        # Recomendaciones
        'recomendaciones': recomendaciones,
    }


def get_frecuencia_limite(altura_agarre: float) -> float:
    """
    Devuelve frecuencia límite según altura del agarre
    
    Altura (cm)     Frecuencia límite (acciones/min)
    65-95 (bajo)    2
    95-125 (mano)   5
    125-180 (alto)  3
    """
    
    if altura_agarre < 95:
        return 2
    elif altura_agarre < 125:
        return 5
    else:
        return 3
