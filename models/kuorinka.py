"""
models/kuorinka.py - CUESTIONARIO NÓRDICO (Kuorinka)
Evaluación de síntomas musculoesqueléticos en 9 zonas del cuerpo
Standard para prevalencia de síntomas en extremidades y espalda
"""


# Definición de zonas
ZONAS = [
    {
        'id': 'cuello',
        'nombre': 'Cuello',
        'icono': '🧠',
        'descripcion': 'Área cervical (cuello)',
        'orden': 1,
    },
    {
        'id': 'hombro_izq',
        'nombre': 'Hombro Izquierdo',
        'icono': '💪',
        'descripcion': 'Articulación del hombro izquierdo',
        'orden': 2,
    },
    {
        'id': 'hombro_der',
        'nombre': 'Hombro Derecho',
        'icono': '💪',
        'descripcion': 'Articulación del hombro derecho',
        'orden': 3,
    },
    {
        'id': 'codo_izq',
        'nombre': 'Codo Izquierdo',
        'icono': '🦾',
        'descripcion': 'Codo y antebrazo izquierdo',
        'orden': 4,
    },
    {
        'id': 'codo_der',
        'nombre': 'Codo Derecho',
        'icono': '🦾',
        'descripcion': 'Codo y antebrazo derecho',
        'orden': 5,
    },
    {
        'id': 'muñeca_izq',
        'nombre': 'Muñeca Izquierda',
        'icono': '🤚',
        'descripcion': 'Muñeca y mano izquierda',
        'orden': 6,
    },
    {
        'id': 'muñeca_der',
        'nombre': 'Muñeca Derecha',
        'icono': '🤚',
        'descripcion': 'Muñeca y mano derecha',
        'orden': 7,
    },
    {
        'id': 'espalda_baja',
        'nombre': 'Espalda Baja',
        'icono': '🫀',
        'descripcion': 'Región lumbar (espalda baja)',
        'orden': 8,
    },
    {
        'id': 'cadera_rodilla',
        'nombre': 'Cadera/Rodilla',
        'icono': '🦵',
        'descripcion': 'Cadera, muslo y rodilla',
        'orden': 9,
    },
]


def calculate_kuorinka(data: dict) -> dict:
    """
    Analiza respuestas del Cuestionario Nórdico
    
    Args:
        data: Dict con respuestas
        {
            'zona_id': {
                'molestias_12m': bool,          # ¿Molestias últimos 12 meses?
                'molestias_7d': bool,           # ¿Molestias últimos 7 días?
                'consulta_medica': bool,        # ¿Consultó médico?
                'ausencia_trabajo': bool,       # ¿Faltó al trabajo?
            },
            ... (para cada zona)
        }
    
    Returns:
        Dict con análisis de prevalencia y zonas críticas
    """
    
    # ════════════════════════════════════════════════════════════════════════════════
    # PROCESAR RESPUESTAS
    # ════════════════════════════════════════════════════════════════════════════════
    
    resultados_zonas = {}
    total_zonas_con_sintomas = 0
    zonas_criticas = []
    
    for zona in ZONAS:
        zona_id = zona['id']
        respuestas = data.get(zona_id, {})
        
        # Extraer respuestas
        molestias_12m = respuestas.get('molestias_12m', False)
        molestias_7d = respuestas.get('molestias_7d', False)
        consulta_medica = respuestas.get('consulta_medica', False)
        ausencia_trabajo = respuestas.get('ausencia_trabajo', False)
        
        # Calcular prevalencia (1 punto por síntoma)
        puntos = 0
        if molestias_12m:
            puntos += 1
        if molestias_7d:
            puntos += 1
        if consulta_medica:
            puntos += 1
        if ausencia_trabajo:
            puntos += 1
        
        # Clasificación de severidad
        if puntos == 0:
            severidad = 'NORMAL'
            color = '#27ae60'
            badge = 'success'
            riesgo = 'Sin síntomas'
        elif puntos == 1:
            severidad = 'LEVE'
            color = '#2ecc71'
            badge = 'info'
            riesgo = 'Síntomas leves'
        elif puntos == 2:
            severidad = 'MODERADO'
            color = '#f39c12'
            badge = 'warning'
            riesgo = 'Síntomas moderados'
        else:
            severidad = 'SEVERO'
            color = '#e74c3c'
            badge = 'danger'
            riesgo = 'Síntomas severos'
        
        # Almacenar resultado de la zona
        resultado_zona = {
            'nombre': zona['nombre'],
            'icono': zona['icono'],
            'descripcion': zona['descripcion'],
            'puntos': puntos,
            'severidad': severidad,
            'color': color,
            'badge': badge,
            'riesgo': riesgo,
            'molestias_12m': molestias_12m,
            'molestias_7d': molestias_7d,
            'consulta_medica': consulta_medica,
            'ausencia_trabajo': ausencia_trabajo,
        }
        
        resultados_zonas[zona_id] = resultado_zona
        
        if puntos > 0:
            total_zonas_con_sintomas += 1
            if puntos >= 3:
                zonas_criticas.append({
                    'zona': zona['nombre'],
                    'puntos': puntos,
                    'color': color,
                })
    
    # ════════════════════════════════════════════════════════════════════════════════
    # ANÁLISIS GENERAL
    # ════════════════════════════════════════════════════════════════════════════════
    
    # Prevalencia general
    prevalencia_general = (total_zonas_con_sintomas / len(ZONAS)) * 100
    
    if prevalencia_general == 0:
        estado_general = 'ÓPTIMO'
        color_general = '#27ae60'
        badge_general = 'success'
        descripcion_general = 'Sin síntomas detectados - Condiciones ergonómicas aceptables'
    elif prevalencia_general <= 25:
        estado_general = 'BAJO'
        color_general = '#2ecc71'
        badge_general = 'info'
        descripcion_general = 'Baja prevalencia de síntomas - Vigilancia recomendada'
    elif prevalencia_general <= 50:
        estado_general = 'MODERADO'
        color_general = '#f39c12'
        badge_general = 'warning'
        descripcion_general = 'Prevalencia moderada - Intervención recomendada'
    else:
        estado_general = 'ALTO'
        color_general = '#e74c3c'
        badge_general = 'danger'
        descripcion_general = 'Alta prevalencia de síntomas - Acción inmediata requerida'
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RECOMENDACIONES
    # ════════════════════════════════════════════════════════════════════════════════
    
    recomendaciones = []
    
    if len(zonas_criticas) > 0:
        recomendaciones.append(
            f'🔴 ZONAS CRÍTICAS IDENTIFICADAS: {", ".join([z["zona"] for z in zonas_criticas])}'
        )
        recomendaciones.append(
            '→ Referencia médica recomendada para evaluación especializada'
        )
    
    if total_zonas_con_sintomas > 0:
        recomendaciones.append(
            f'⚠️ {total_zonas_con_sintomas} zona(s) con síntomas detectada(s)'
        )
        recomendaciones.append(
            '→ Evaluar y modificar factores ergonómicos en el puesto'
        )
    
    if any(z.get('ausencia_trabajo', False) for z in resultados_zonas.values()):
        recomendaciones.append(
            '🏥 AUSENCIA LABORAL: Trabajador ha faltado por molestias musculoesqueléticas'
        )
        recomendaciones.append(
            '→ Considerar adaptación temporal del puesto de trabajo'
        )
    
    # Regiones con más síntomas
    espalda_cuello = resultados_zonas.get('espalda_baja', {}).get('puntos', 0) + resultados_zonas.get('cuello', {}).get('puntos', 0)
    extremidades = sum(resultados_zonas[z].get('puntos', 0) for z in ['hombro_izq', 'hombro_der', 'codo_izq', 'codo_der', 'muñeca_izq', 'muñeca_der'])
    
    if espalda_cuello > extremidades:
        recomendaciones.append(
            '💡 Enfoque principal: Ajustar altura de escritorio, apoyapiés, postura sentada'
        )
    elif extremidades > espalda_cuello:
        recomendaciones.append(
            '💡 Enfoque principal: Mejorar diseño de herramientas, reposamuñecas, descansos'
        )
    
    if not recomendaciones:
        recomendaciones.append('✓ Sin síntomas detectados - Mantener vigilancia periódica')
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RESULTADO FINAL
    # ════════════════════════════════════════════════════════════════════════════════
    
    return {
        # Datos de cada zona
        'zonas': resultados_zonas,
        
        # Análisis general
        'total_zonas': len(ZONAS),
        'zonas_con_sintomas': total_zonas_con_sintomas,
        'prevalencia_general': round(prevalencia_general, 1),
        
        # Estado general
        'estado_general': estado_general,
        'color_general': color_general,
        'badge_general': badge_general,
        'descripcion_general': descripcion_general,
        
        # Zonas críticas
        'zonas_criticas': zonas_criticas,
        'numero_criticas': len(zonas_criticas),
        
        # Regiones
        'score_espalda_cuello': espalda_cuello,
        'score_extremidades': extremidades,
        
        # Recomendaciones
        'recomendaciones': recomendaciones,
    }


def get_zona_por_id(zona_id: str) -> dict:
    """Obtiene información de una zona por su ID"""
    for zona in ZONAS:
        if zona['id'] == zona_id:
            return zona
    return {}


def listar_zonas() -> list:
    """Devuelve lista de todas las zonas"""
    return ZONAS
