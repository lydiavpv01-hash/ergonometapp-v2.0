"""
models/calculadores.py - Funciones de cálculo de todos los métodos
Extraído de app.py original, refactorizado para v2
"""

# ═══════════════════════════════════════════════════════════════════════════════════
# REBA - FUNCIONES DE CÁLCULO
# ═══════════════════════════════════════════════════════════════════════════════════

def score_neck(angle_deg: float, lateral_bending: bool = False) -> int:
    """
    Calcula puntuación del cuello - REBA
    
    Args:
        angle_deg: Ángulo del cuello en grados (respecto a vertical)
        lateral_bending: Si hay inclinación lateral o torsión
    
    Returns:
        Puntuación (1-4)
    """
    if angle_deg <= 20:
        score = 1
    elif angle_deg <= 45:
        score = 2
    else:
        score = 3
    if lateral_bending:
        score += 1
    return score


def score_trunk(angle_deg: float, lateral_bending: bool = False, twisting: bool = False) -> int:
    """
    Calcula puntuación del torso/tronco - REBA
    
    Args:
        angle_deg: Ángulo de flexión del tronco en grados
        lateral_bending: Si hay inclinación lateral
        twisting: Si hay torsión
    
    Returns:
        Puntuación (1-5)
    """
    if angle_deg <= 5:
        score = 1
    elif angle_deg <= 20:
        score = 2
    elif angle_deg <= 60:
        score = 3
    else:
        score = 4
    if lateral_bending or twisting:
        score += 1
    return score


def score_legs(knee_angle: float, bilateral_weight: bool = True) -> int:
    """
    Calcula puntuación de piernas/soporte - REBA
    
    Args:
        knee_angle: Ángulo de flexión de rodilla en grados
        bilateral_weight: Si hay soporte bilateral del peso
    
    Returns:
        Puntuación (1-4)
    """
    # Base: bipedestación bilateral = 1, unilateral = 2
    score = 1 if bilateral_weight else 2
    
    # Flexión de rodilla
    if 30 < knee_angle <= 60:
        score += 1
    elif knee_angle > 60:
        score += 2
    
    return score


def score_upper_arm(angle_deg: float, shoulder_raised: bool = False, 
                    abducted: bool = False, gravity_assist: bool = False) -> int:
    """
    Calcula puntuación del brazo/hombro - REBA
    
    Args:
        angle_deg: Ángulo del brazo en grados
        shoulder_raised: Si el hombro está elevado (+1)
        abducted: Si el brazo está abducido (+1)
        gravity_assist: Si hay asistencia de gravedad (-1)
    
    Returns:
        Puntuación (1-5)
    """
    if angle_deg <= 20:
        score = 1
    elif angle_deg <= 45:
        score = 2
    elif angle_deg <= 90:
        score = 3
    else:
        score = 4
    
    if shoulder_raised:
        score += 1
    if abducted:
        score += 1
    if gravity_assist:
        score -= 1
    
    return max(1, score)


def score_forearm(angle_deg: float) -> int:
    """
    Calcula puntuación del antebrazo - REBA
    
    Args:
        angle_deg: Ángulo del antebrazo en grados (ideal: 60-100)
    
    Returns:
        Puntuación (1-2)
    """
    if 60 <= angle_deg <= 100:
        return 1
    return 2


def score_wrist(angle_deg: float, lateral_deviation: bool = False) -> int:
    """
    Calcula puntuación de la muñeca - REBA
    
    Args:
        angle_deg: Ángulo de flexión/extensión de muñeca
        lateral_deviation: Si hay desviación lateral (radial/cubital)
    
    Returns:
        Puntuación (1-3)
    """
    score = 1 if angle_deg <= 15 else 2
    if lateral_deviation:
        score += 1
    return score


# ═══════════════════════════════════════════════════════════════════════════════════
# REBA - TABLAS DE BÚSQUEDA
# ═══════════════════════════════════════════════════════════════════════════════════

# Tabla A: Combinación de Tronco + Cuello + Piernas
TABLE_A = [
    # Cuello=1
    [[1, 2, 3, 4], [1, 2, 3, 4], [3, 3, 5, 6]],
    # Cuello=2
    [[2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7]],
    # Cuello=3
    [[2, 4, 5, 6], [4, 5, 6, 7], [5, 6, 7, 8]],
]

# Tabla B: Combinación de Brazo + Antebrazo + Muñeca
TABLE_B = [
    # Antebrazo=1
    [[1, 2, 2], [1, 2, 3]],
    # Antebrazo=2
    [[1, 2, 3], [2, 3, 4]],
]

# Tabla C: Combinación final de Score A + Score B
TABLE_C = [
    [1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 7, 7],
    [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 8],
    [2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 8, 8],
    [3, 4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9],
    [4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9],
    [6, 6, 6, 7, 8, 8, 9, 9, 10, 10, 10, 10],
    [7, 7, 7, 8, 9, 9, 9, 10, 10, 11, 11, 11],
    [8, 8, 8, 9, 10, 10, 10, 10, 10, 11, 11, 11],
    [9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12],
    [10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 12],
    [11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12],
    [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
]


def lookup_table_a(trunk: int, neck: int, legs: int) -> int:
    """
    Busca puntuación en Tabla A (Grupo A: Tronco + Cuello + Piernas)
    
    Args:
        trunk: Puntuación tronco (1-4)
        neck: Puntuación cuello (1-3)
        legs: Puntuación piernas (1-4)
    
    Returns:
        Score Grupo A (1-8)
    """
    t = min(max(trunk - 1, 0), 3)
    n = min(max(neck - 1, 0), 2)
    l = min(max(legs - 1, 0), 3)
    
    if n < len(TABLE_A) and t < len(TABLE_A[n]) and l < len(TABLE_A[n][t]):
        return TABLE_A[n][t][l]
    return 6


def lookup_table_b(upper_arm: int, forearm: int, wrist: int) -> int:
    """
    Busca puntuación en Tabla B (Grupo B: Brazo + Antebrazo + Muñeca)
    
    Args:
        upper_arm: Puntuación brazo (1-5)
        forearm: Puntuación antebrazo (1-2)
        wrist: Puntuación muñeca (1-3)
    
    Returns:
        Score Grupo B (1-4)
    """
    fa = min(max(forearm - 1, 0), 1)
    wr = min(max(wrist - 1, 0), 1)
    ua = min(max(upper_arm - 1, 0), 2)
    
    if fa < len(TABLE_B) and wr < len(TABLE_B[fa]) and ua < len(TABLE_B[fa][wr]):
        return TABLE_B[fa][wr][ua]
    return 4


def lookup_table_c(score_a: int, score_b: int) -> int:
    """
    Busca puntuación final en Tabla C (Score A + Score B)
    
    Args:
        score_a: Score Grupo A (1-8)
        score_b: Score Grupo B (1-4)
    
    Returns:
        Score final antes de carga/agarre (1-12)
    """
    r = min(max(score_a - 1, 0), 11)
    c = min(max(score_b - 1, 0), 11)
    return TABLE_C[r][c]


def reba_action_level(score: int) -> dict:
    """
    Devuelve nivel de acción y recomendaciones basado en score REBA
    
    Args:
        score: Score REBA final (1-15)
    
    Returns:
        Dict con nivel, acción, color, badge
    """
    if score == 1:
        return {
            'nivel': 'INAPRECIABLE',
            'accion': 'No necesaria',
            'color': '#27ae60',
            'badge': 'success',
            'prioridad': 1,
        }
    elif score <= 3:
        return {
            'nivel': 'BAJO',
            'accion': 'Puede ser necesaria',
            'color': '#f39c12',
            'badge': 'warning',
            'prioridad': 2,
        }
    elif score <= 7:
        return {
            'nivel': 'MEDIO',
            'accion': 'Necesaria',
            'color': '#e67e22',
            'badge': 'warning',
            'prioridad': 3,
        }
    elif score <= 10:
        return {
            'nivel': 'ALTO',
            'accion': 'Necesaria pronto',
            'color': '#e74c3c',
            'badge': 'danger',
            'prioridad': 4,
        }
    else:
        return {
            'nivel': 'MUY ALTO',
            'accion': 'Inmediata',
            'color': '#8e44ad',
            'badge': 'critical',
            'prioridad': 5,
        }


def calculate_reba(data: dict) -> dict:
    """
    Calcula REBA completo desde datos de formulario
    
    Args:
        data: Dict con ángulos y ajustes
        Ejemplo:
        {
            'grupo_a': {
                'cuello': {'posicion': 'normal_0-20', 'giro': False, 'inclinacion': False},
                'torso': {'posicion': 'recto', 'giro': False, 'inclinacion': False},
                'piernas': {'posicion': 'bipedestacion', 'soporte': 'bilateral'}
            },
            'grupo_b': {
                'brazo': {'posicion': '20-45', 'hombro_elevado': False, 'abducido': False},
                'antebrazo': {'posicion': '60-100'},
                'muñeca': {'posicion': 'neutra', 'torsion': False}
            },
            'carga': {'peso_kg': 5},
            'agarre': {'tipo': 'aceptable'}
        }
    
    Returns:
        Dict con todos los scores y análisis
    """
    
    # Extraer datos de Grupo A
    grupo_a = data.get('grupo_a', {})
    
    # Cuello
    neck_data = grupo_a.get('cuello', {})
    neck_angle = 15  # Default
    if neck_data.get('posicion') == '0-20':
        neck_angle = 10
    elif neck_data.get('posicion') == '20+':
        neck_angle = 30
    elif neck_data.get('posicion') == 'extension':
        neck_angle = 5
    
    neck_score = score_neck(
        neck_angle,
        lateral_bending=neck_data.get('giro') or neck_data.get('inclinacion', False)
    )
    
    # Tronco
    trunk_data = grupo_a.get('torso', {})
    trunk_angle = 10  # Default
    if trunk_data.get('posicion') == 'recto':
        trunk_angle = 0
    elif trunk_data.get('posicion') == 'inclinado_0-20':
        trunk_angle = 10
    elif trunk_data.get('posicion') == 'inclinado_20-60':
        trunk_angle = 40
    elif trunk_data.get('posicion') == 'muy_inclinado':
        trunk_angle = 70
    elif trunk_data.get('posicion') == 'extension':
        trunk_angle = -10
    
    trunk_score = score_trunk(
        abs(trunk_angle),
        lateral_bending=trunk_data.get('giro', False),
        twisting=trunk_data.get('inclinacion', False)
    )
    
    # Piernas
    legs_data = grupo_a.get('piernas', {})
    knee_angle = 175  # Default: bipedestación sin flexión
    bilateral = legs_data.get('soporte') == 'bilateral'
    
    legs_score = score_legs(knee_angle, bilateral_weight=bilateral)
    
    # Extraer datos de Grupo B
    grupo_b = data.get('grupo_b', {})
    
    # Brazo
    arm_data = grupo_b.get('brazo', {})
    arm_angle = 20  # Default
    if arm_data.get('posicion') == '0-20':
        arm_angle = 10
    elif arm_data.get('posicion') == '20-45':
        arm_angle = 30
    elif arm_data.get('posicion') == '45-90':
        arm_angle = 60
    elif arm_data.get('posicion') == '90+':
        arm_angle = 120
    
    arm_score = score_upper_arm(
        arm_angle,
        shoulder_raised=arm_data.get('hombro_elevado', False),
        abducted=arm_data.get('abducido', False),
        gravity_assist=arm_data.get('asistido', False)
    )
    
    # Antebrazo
    forearm_data = grupo_b.get('antebrazo', {})
    forearm_angle = 80  # Default
    if forearm_data.get('posicion') == '60-100':
        forearm_angle = 80
    else:
        forearm_angle = 120
    
    forearm_score = score_forearm(forearm_angle)
    
    # Muñeca
    wrist_data = grupo_b.get('muñeca', {})
    wrist_angle = 10  # Default
    if wrist_data.get('posicion') == 'neutra':
        wrist_angle = 5
    elif wrist_data.get('posicion') == '0-15':
        wrist_angle = 10
    elif wrist_data.get('posicion') == '15+':
        wrist_angle = 20
    
    wrist_score = score_wrist(
        wrist_angle,
        lateral_deviation=wrist_data.get('torsion', False)
    )
    
    # Tablas de búsqueda
    score_a = lookup_table_a(trunk_score, neck_score, legs_score)
    
    # Carga/Fuerza (0-3 puntos)
    carga_data = data.get('carga', {})
    peso_kg = carga_data.get('peso_kg', 0)
    if peso_kg < 5:
        force_score = 0
    elif peso_kg < 10:
        force_score = 1
    else:
        force_score = 2
    
    score_a_force = min(score_a + force_score, 12)
    
    # Score B
    score_b = lookup_table_b(arm_score, forearm_score, wrist_score)
    
    # Agarre (0-3 puntos)
    agarre_data = data.get('agarre', {})
    agarre_tipo = agarre_data.get('tipo', 'aceptable')
    if agarre_tipo == 'bueno':
        coupling_score = 0
    elif agarre_tipo == 'aceptable':
        coupling_score = 1
    else:
        coupling_score = 2
    
    score_b_coupling = min(score_b + coupling_score, 12)
    
    # Score C (final)
    score_c = lookup_table_c(score_a_force, score_b_coupling)
    
    # Actividad (0-3)
    activity_score = 0  # Implementar si es necesario
    
    final_score = min(score_c + activity_score, 15)
    
    # Nivel de acción
    action = reba_action_level(final_score)
    
    return {
        'grupo_a': {
            'cuello': neck_score,
            'torso': trunk_score,
            'piernas': legs_score,
            'score': score_a,
        },
        'grupo_b': {
            'brazo': arm_score,
            'antebrazo': forearm_score,
            'muñeca': wrist_score,
            'score': score_b,
        },
        'carga_agarre': {
            'fuerza': force_score,
            'agarre': coupling_score,
        },
        'scores': {
            'score_a': score_a,
            'score_a_force': score_a_force,
            'score_b': score_b,
            'score_b_coupling': score_b_coupling,
            'score_c': score_c,
            'score_final': final_score,
        },
        'resultado': {
            'puntaje': final_score,
            'nivel': action['nivel'],
            'accion': action['accion'],
            'color': action['color'],
            'prioridad': action['prioridad'],
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════════
# LEY SILLA - FUNCIONES (PLACEHOLDER)
# ═══════════════════════════════════════════════════════════════════════════════════

def evaluar_ley_silla(data: dict) -> dict:
    """Evaluar Ley SILLA - Placeholder"""
    return {
        'puntaje': 0,
        'nivel': 'ACEPTABLE',
        'silla_recomendada': {}
    }


# ═══════════════════════════════════════════════════════════════════════════════════
# LEST - FUNCIONES (PLACEHOLDER)
# ═══════════════════════════════════════════════════════════════════════════════════

def calculate_lest(data: dict) -> dict:
    """Calcular LEST - Placeholder"""
    return {
        'puntaje': 0,
        'nivel': 'BAJO',
        'dimensiones': {}
    }
