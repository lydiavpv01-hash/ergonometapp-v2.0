"""
models/ley_silla.py - Evaluación de Bipedestación (DOF Ley Silla)
Implementa: NOM-036-1-STPS-2018 - Disposiciones sobre Ley Silla
Extractor de app.py, refactorizado para v2
"""


def evaluar_ley_silla(data: dict) -> dict:
    """
    Evaluación de bipedestación según DOF Ley Silla
    
    7 preguntas condicionales → clasificación de bipedestación → 
    cálculo de riesgo → recomendación de silla → medidas preventivas
    
    Args:
        data: Dict con respuestas del usuario
        {
            'tiempo_pie': float (horas),
            'espacio_desplazamiento': bool,
            'puede_cambiar_postura': bool,
            'molestias_reportadas': bool,
            'tipo_superficie': str ('concreto', 'madera', 'alfombra', 'metal', 'ceramica', 'goma', 'antifatiga'),
            'calzado_adecuado': bool,
            'tiene_pausas': bool,
        }
    
    Returns:
        Dict con:
        - tipo_bipedestacion: 'ESTÁTICA', 'DINÁMICA', 'ESTÁTICA PROLONGADA', 'DINÁMICA PROLONGADA'
        - nivel_riesgo: 'BAJO', 'MEDIO', 'ALTO'
        - puntos_riesgo: 0-15 (suma de factores)
        - tipo_asiento_recomendado: descripción de silla
        - medidas_preventivas: lista de recomendaciones
        - color_riesgo: hex color por nivel
    """
    
    # ════════════════════════════════════════════════════════════════════════════════
    # EXTRACCIÓN Y VALIDACIÓN DE DATOS
    # ════════════════════════════════════════════════════════════════════════════════
    
    tiempo_pie = float(data.get('tiempo_pie', 0))  # Horas
    espacio_desplazamiento = bool(data.get('espacio_desplazamiento', True))
    puede_cambiar_postura = bool(data.get('puede_cambiar_postura', True))
    molestias_reportadas = bool(data.get('molestias_reportadas', False))
    tipo_superficie = str(data.get('tipo_superficie', 'concreto')).lower()
    calzado_adecuado = bool(data.get('calzado_adecuado', True))
    tiene_pausas = bool(data.get('tiene_pausas', True))
    
    # ════════════════════════════════════════════════════════════════════════════════
    # PASO 1: CLASIFICAR TIPO DE BIPEDESTACIÓN
    # ════════════════════════════════════════════════════════════════════════════════
    
    # Determinar si es ESTÁTICA o DINÁMICA
    if not espacio_desplazamiento and tiempo_pie >= 1:
        tipo = 'ESTÁTICA'
        tipo_desc = 'Postura de pie prácticamente sin moverse o con desplazamientos mínimos'
    elif espacio_desplazamiento:
        tipo = 'DINÁMICA'
        tipo_desc = 'Postura de pie con posibilidad de realizar desplazamientos amplios'
    else:
        tipo = 'DINÁMICA'
        tipo_desc = 'Postura de pie con desplazamientos variables'
    
    # Verificar si es PROLONGADA (>= 3 horas)
    es_prolongada = tiempo_pie >= 3
    if es_prolongada:
        tipo = tipo + ' PROLONGADA'
        tipo_desc += ' — más de 3 horas continuas (PROLONGADA)'
    
    # ════════════════════════════════════════════════════════════════════════════════
    # PASO 2: CALCULAR PUNTUACIÓN DE RIESGO
    # ════════════════════════════════════════════════════════════════════════════════
    
    puntos_riesgo = 0
    
    # Factor 1: Tiempo de pie (0-4 puntos)
    if tiempo_pie >= 6:
        puntos_riesgo += 4
    elif tiempo_pie >= 3:
        puntos_riesgo += 3
    elif tiempo_pie >= 1:
        puntos_riesgo += 1
    
    # Factor 2: Imposibilidad de cambio postural (+2)
    if not puede_cambiar_postura:
        puntos_riesgo += 2
    
    # Factor 3: Espacio limitado para desplazamiento (+1)
    if not espacio_desplazamiento:
        puntos_riesgo += 1
    
    # Factor 4: Molestias musculoesqueléticas reportadas (+2)
    if molestias_reportadas:
        puntos_riesgo += 2
    
    # Factor 5: Tipo de superficie de trabajo (0-2)
    superficie_riesgo = {
        'concreto': 2,
        'metal': 2,
        'ceramica': 2,
        'madera': 1,
        'alfombra': 0,
        'goma': 0,
        'antifatiga': -1,  # Reduce riesgo
    }
    puntos_riesgo += superficie_riesgo.get(tipo_superficie, 1)
    
    # Factor 6: Calzado inadecuado (+1)
    if not calzado_adecuado:
        puntos_riesgo += 1
    
    # Factor 7: Falta de pausas de descanso (+2)
    if not tiene_pausas:
        puntos_riesgo += 2
    
    # Clampar puntos entre 0 y 15
    puntos_riesgo = max(0, min(puntos_riesgo, 15))
    
    # ════════════════════════════════════════════════════════════════════════════════
    # PASO 3: DETERMINAR NIVEL DE RIESGO Y RECOMENDACIONES
    # ════════════════════════════════════════════════════════════════════════════════
    
    if puntos_riesgo <= 2:
        nivel_riesgo = 'BAJO'
        color_riesgo = '#27ae60'  # Verde
        tipo_asiento = 'Banco alto o taburete sin respaldo'
        descripcion_riesgo = 'Riesgo ACEPTABLE. Proveer asiento o banco alto para pausas.'
        badge = 'success'
    elif puntos_riesgo <= 5:
        nivel_riesgo = 'MEDIO'
        color_riesgo = '#f39c12'  # Amarillo/Naranja
        tipo_asiento = 'Silla alta con respaldo medio o banco ergonómico'
        descripcion_riesgo = 'Riesgo MODERADO. Proveer silla con respaldo en puesto o área de descanso cercana.'
        badge = 'warning'
    else:
        nivel_riesgo = 'ALTO'
        color_riesgo = '#e74c3c'  # Rojo
        tipo_asiento = 'Silla ergonómica ajustable con soporte lumbar y reposabrazos'
        descripcion_riesgo = 'Riesgo ELEVADO. Proveer silla ergonómica en puesto de trabajo. Implementar pausas activas y rediseño del puesto.'
        badge = 'danger'
    
    # ════════════════════════════════════════════════════════════════════════════════
    # PASO 4: GENERAR MEDIDAS PREVENTIVAS (según DOF Disposiciones)
    # ════════════════════════════════════════════════════════════════════════════════
    
    medidas_preventivas = []
    
    # Medidas según factores de riesgo
    if not tiene_pausas:
        medidas_preventivas.append(
            'Implementar programa de pausas activas cada 60-90 minutos'
        )
    
    if not calzado_adecuado:
        medidas_preventivas.append(
            'Proporcionar o exigir calzado ergonómico con soporte de arco'
        )
    
    if tipo_superficie in ['concreto', 'metal', 'ceramica']:
        medidas_preventivas.append(
            'Colocar superficies antifatiga (tapetes ergonómicos) en el área de trabajo'
        )
    
    if not puede_cambiar_postura:
        medidas_preventivas.append(
            'Rediseñar el puesto para permitir alternancia entre postura sentado/parado'
        )
    
    if molestias_reportadas:
        medidas_preventivas.append(
            'Canalizar al trabajador a atención médica por molestias reportadas (DOF Disposiciones, inciso J)'
        )
    
    if tiempo_pie >= 3:
        medidas_preventivas.append(
            'Establecer rotación de tareas o cambios de actividad cada hora'
        )
    
    # Medidas administrativas finales
    medidas_preventivas.append(
        'Registrar la evaluación en actas de la Comisión de Seguridad e Higiene (NOM-030-STPS-2009)'
    )
    medidas_preventivas.append(
        'Informar al trabajador sobre los riesgos de bipedestación prolongada y medidas preventivas'
    )
    
    if nivel_riesgo == 'ALTO':
        medidas_preventivas.append(
            'Realizar seguimiento mensual y documentar mejoras implementadas'
        )
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RESULTADO FINAL
    # ════════════════════════════════════════════════════════════════════════════════
    
    return {
        # Clasificación
        'tipo_bipedestacion': tipo,
        'tipo_desc': tipo_desc,
        'es_prolongada': es_prolongada,
        
        # Puntuación y nivel
        'puntos_riesgo': puntos_riesgo,
        'nivel_riesgo': nivel_riesgo,
        'color_riesgo': color_riesgo,
        'badge': badge,
        
        # Recomendaciones
        'tipo_asiento_recomendado': tipo_asiento,
        'descripcion_riesgo': descripcion_riesgo,
        'medidas_preventivas': medidas_preventivas,
        
        # Detalles de factores (para mostrar en reporte)
        'factores': {
            'tiempo_pie': {
                'valor': tiempo_pie,
                'puntos': min(max(0, 
                    4 if tiempo_pie >= 6 else 
                    3 if tiempo_pie >= 3 else 
                    1 if tiempo_pie >= 1 else 0
                ), 4),
                'descripcion': f'Tiempo de pie: {tiempo_pie:.1f} horas'
            },
            'espacio_desplazamiento': {
                'valor': espacio_desplazamiento,
                'puntos': 0 if espacio_desplazamiento else 1,
                'descripcion': f'Espacio para desplazarse: {"Sí" if espacio_desplazamiento else "No"}'
            },
            'puede_cambiar_postura': {
                'valor': puede_cambiar_postura,
                'puntos': 0 if puede_cambiar_postura else 2,
                'descripcion': f'Puede cambiar postura: {"Sí" if puede_cambiar_postura else "No"}'
            },
            'molestias_reportadas': {
                'valor': molestias_reportadas,
                'puntos': 2 if molestias_reportadas else 0,
                'descripcion': f'Molestias reportadas: {"Sí" if molestias_reportadas else "No"}'
            },
            'tipo_superficie': {
                'valor': tipo_superficie,
                'puntos': superficie_riesgo.get(tipo_superficie, 1),
                'descripcion': f'Tipo de superficie: {tipo_superficie}'
            },
            'calzado_adecuado': {
                'valor': calzado_adecuado,
                'puntos': 0 if calzado_adecuado else 1,
                'descripcion': f'Calzado adecuado: {"Sí" if calzado_adecuado else "No"}'
            },
            'tiene_pausas': {
                'valor': tiene_pausas,
                'puntos': 0 if tiene_pausas else 2,
                'descripcion': f'Cuenta con pausas: {"Sí" if tiene_pausas else "No"}'
            }
        },
        
        # Datos originales (para guardar en BD)
        'datos_entrada': data,
    }


# ════════════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ════════════════════════════════════════════════════════════════════════════════════

def get_superficie_options():
    """Devuelve opciones de tipo de superficie"""
    return [
        ('concreto', 'Concreto (riesgo alto)', 2),
        ('metal', 'Metal (riesgo alto)', 2),
        ('ceramica', 'Cerámica (riesgo alto)', 2),
        ('madera', 'Madera (riesgo medio)', 1),
        ('alfombra', 'Alfombra (riesgo bajo)', 0),
        ('goma', 'Goma (riesgo bajo)', 0),
        ('antifatiga', 'Tapete antifatiga (reduce riesgo)', -1),
    ]


def get_tiempo_pie_options():
    """Devuelve opciones de tiempo de pie"""
    return [
        (0, 'Menos de 1 hora'),
        (1, '1 a 3 horas'),
        (3, '3 a 6 horas'),
        (6, '6 a 8 horas'),
        (8, 'Más de 8 horas'),
    ]


def get_silla_especificaciones(tipo_asiento: str) -> dict:
    """Devuelve especificaciones técnicas de la silla recomendada"""
    
    especificaciones = {
        'Banco alto o taburete sin respaldo': {
            'altura': '60-80 cm',
            'respaldo': 'Sin respaldo',
            'reposabrazos': 'Sin reposabrazos',
            'material': 'Madera o metal',
            'caracteristicas': ['Permite apoyar peso alternativamente', 'Para pausas de corta duración'],
            'uso': 'Pausas activas, descansos rápidos',
        },
        'Silla alta con respaldo medio o banco ergonómico': {
            'altura': '50-70 cm',
            'respaldo': 'Respaldo medio (hasta omóplatos)',
            'reposabrazos': 'Reposabrazos opcionales',
            'material': 'Tapizado ergonómico',
            'caracteristicas': [
                'Soporte lumbar básico',
                'Rotación y ajuste de altura',
                'Adecuado para descansos de 5-15 minutos'
            ],
            'uso': 'Área de descanso, puesto secundario',
        },
        'Silla ergonómica ajustable con soporte lumbar y reposabrazos': {
            'altura': '40-55 cm',
            'respaldo': 'Respaldo alto con curva lumbar ajustable',
            'reposabrazos': 'Reposabrazos ajustables en altura y ángulo',
            'material': 'Malla transpirable o tapizado premium',
            'caracteristicas': [
                'Mecanismo multi-ajuste (altura, inclinación, profundidad)',
                'Soporte lumbar dinámico',
                'Base de 5 ruedas para movilidad',
                'Apoyacabeza opcional',
                'Cumple ISO 11228 y BIFMA'
            ],
            'uso': 'Puesto de trabajo principal, uso prolongado',
            'presupuesto_aproximado': '3,000 - 8,000 MXN por unidad',
        }
    }
    
    return especificaciones.get(tipo_asiento, {})
