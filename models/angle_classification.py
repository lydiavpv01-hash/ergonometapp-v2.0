"""
models/angle_classification.py - Clasificación de ángulos con dirección

Convierte mediciones angulares + dirección → puntaje base según tablas REBA.

Regla crítica: El ángulo SOLO no es suficiente.
Se requiere DIRECCIÓN: flexion, extension, neutral

Estructura de entrada:
{
    'angle': 32.4,
    'direction': 'flexion'  # 'flexion', 'extension', 'neutral'
}

Estructura de salida (para cada segmento):
{
    'angle': 32.4,
    'direction': 'flexion',
    'range': '20-45°',
    'base_score': 2,
    'adjustments': {...},
    'final_score': 3
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CUELLO
# ═══════════════════════════════════════════════════════════════════════════════
# Flexión 0-20°: base 1
# Flexión >20°: base 2
# Extensión: base 2
# Ajustes: torcido +1, inclinación lateral +1

def classify_neck(angle: float, direction: str) -> dict:
    """
    Clasifica posición de cuello.
    
    Args:
        angle: Ángulo en grados
        direction: 'flexion', 'extension', 'neutral'
    
    Returns:
        dict con base_score, range, description
    """
    if direction == 'neutral':
        # Neutral = entre -20° y +20° flexión
        if angle <= 20:
            return {
                'base_score': 1,
                'range': '0-20° flexión',
                'description': 'Flexión 0-20°'
            }
        else:
            return {
                'base_score': 2,
                'range': '>20° flexión',
                'description': 'Flexión >20°'
            }
    
    elif direction == 'flexion':
        if angle <= 20:
            return {
                'base_score': 1,
                'range': '0-20° flexión',
                'description': 'Flexión 0-20°'
            }
        else:
            return {
                'base_score': 2,
                'range': '>20° flexión',
                'description': 'Flexión >20°'
            }
    
    elif direction == 'extension':
        # Cualquier extensión = base 2
        return {
            'base_score': 2,
            'range': 'extensión',
            'description': f'Extensión {angle}°'
        }
    
    return {
        'base_score': 1,
        'range': 'desconocido',
        'description': 'Error en clasificación'
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TORSO
# ═══════════════════════════════════════════════════════════════════════════════
# Posición neutra 0°: base 1
# Extensión 0-20°: base 2
# Flexión 0-20°: base 2
# Flexión 20-60°: base 3
# Extensión >20°: base 3
# Flexión >60°: base 4
# Ajustes: torcido +1, inclinado lateralmente +1

def classify_trunk(angle: float, direction: str) -> dict:
    """
    Clasifica posición de torso.
    
    Args:
        angle: Ángulo en grados
        direction: 'flexion', 'extension', 'neutral'
    
    Returns:
        dict con base_score, range, description
    """
    if direction == 'neutral':
        if angle == 0:
            return {
                'base_score': 1,
                'range': '0° neutro',
                'description': 'Posición neutra'
            }
        elif angle <= 20:
            return {
                'base_score': 2,
                'range': '0-20° flexión/extensión',
                'description': f'Pequeño movimiento {angle}°'
            }
        elif angle <= 60:
            return {
                'base_score': 3,
                'range': '20-60° flexión',
                'description': f'Flexión {angle}°'
            }
        else:
            return {
                'base_score': 4,
                'range': '>60° flexión',
                'description': f'Flexión {angle}°'
            }
    
    elif direction == 'flexion':
        if angle <= 20:
            return {
                'base_score': 2,
                'range': '0-20° flexión',
                'description': f'Flexión {angle}°'
            }
        elif angle <= 60:
            return {
                'base_score': 3,
                'range': '20-60° flexión',
                'description': f'Flexión {angle}°'
            }
        else:
            return {
                'base_score': 4,
                'range': '>60° flexión',
                'description': f'Flexión {angle}°'
            }
    
    elif direction == 'extension':
        if angle <= 20:
            return {
                'base_score': 2,
                'range': '0-20° extensión',
                'description': f'Extensión {angle}°'
            }
        else:
            return {
                'base_score': 3,
                'range': '>20° extensión',
                'description': f'Extensión {angle}°'
            }
    
    return {
        'base_score': 1,
        'range': 'desconocido',
        'description': 'Error en clasificación'
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PIERNAS
# ═══════════════════════════════════════════════════════════════════════════════
# Ambas apoyadas: base 1
# Levantada/unilateral: base 2
# Ajustes por flexión rodilla: 30-60°=+1, >60°=+2

def classify_legs(condition: str, knee_angle: float = None) -> dict:
    """
    Clasifica posición de piernas.
    
    Args:
        condition: 'both_supported', 'unilateral', 'unstable'
        knee_angle: Ángulo de flexión de rodilla (opcional)
    
    Returns:
        dict con base_score, range, knee_adjustment, description
    """
    base_score = 1
    knee_adjustment = 0
    description = ''
    
    if condition == 'both_supported':
        base_score = 1
        description = 'Ambas piernas apoyadas'
    elif condition == 'unilateral' or condition == 'one_lifted':
        base_score = 2
        description = 'Una pierna levantada o soporte unilateral'
    elif condition == 'unstable':
        base_score = 2
        description = 'Soporte inestable'
    
    # Ajuste por flexión de rodilla
    if knee_angle is not None:
        if 30 <= knee_angle <= 60:
            knee_adjustment = 1
            description += f', flexión rodilla {knee_angle}° (+1)'
        elif knee_angle > 60:
            knee_adjustment = 2
            description += f', flexión rodilla {knee_angle}° (+2)'
    
    return {
        'base_score': base_score,
        'knee_adjustment': knee_adjustment,
        'condition': condition,
        'knee_angle': knee_angle,
        'description': description
    }


# ═══════════════════════════════════════════════════════════════════════════════
# BRAZO
# ═══════════════════════════════════════════════════════════════════════════════
# Extensión >20° o Flexión 0-20°: base 1
# Flexión 20-45°: base 2
# Flexión 45-90°: base 3
# Flexión >90°: base 4
# Ajustes: hombro levantado +1, abducción +1, apoyado -1

def classify_upper_arm(angle: float, direction: str) -> dict:
    """
    Clasifica posición de brazo.
    
    Args:
        angle: Ángulo en grados
        direction: 'flexion', 'extension', 'neutral'
    
    Returns:
        dict con base_score, range, description
    """
    if direction == 'neutral':
        # Neutral = pequeño movimiento
        if -20 <= angle <= 20:
            return {
                'base_score': 1,
                'range': '-20° a 20°',
                'description': 'Posición neutra o pequeño movimiento'
            }
        elif 20 < angle <= 45:
            return {
                'base_score': 2,
                'range': '20-45° flexión',
                'description': f'Flexión {angle}°'
            }
        elif 45 < angle <= 90:
            return {
                'base_score': 3,
                'range': '45-90° flexión',
                'description': f'Flexión {angle}°'
            }
        else:
            return {
                'base_score': 4,
                'range': '>90° flexión',
                'description': f'Flexión {angle}°'
            }
    
    elif direction == 'flexion':
        if angle <= 20:
            return {
                'base_score': 1,
                'range': '0-20° flexión',
                'description': f'Flexión {angle}°'
            }
        elif angle <= 45:
            return {
                'base_score': 2,
                'range': '20-45° flexión',
                'description': f'Flexión {angle}°'
            }
        elif angle <= 90:
            return {
                'base_score': 3,
                'range': '45-90° flexión',
                'description': f'Flexión {angle}°'
            }
        else:
            return {
                'base_score': 4,
                'range': '>90° flexión',
                'description': f'Flexión {angle}°'
            }
    
    elif direction == 'extension':
        if angle <= 20:
            return {
                'base_score': 1,
                'range': '0-20° extensión',
                'description': f'Extensión {angle}°'
            }
        else:
            return {
                'base_score': 1,
                'range': '>20° extensión',
                'description': f'Extensión {angle}°'
            }
    
    return {
        'base_score': 1,
        'range': 'desconocido',
        'description': 'Error en clasificación'
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ANTEBRAZO
# ═══════════════════════════════════════════════════════════════════════════════
# 60-100°: score 1
# <60°: score 2
# >100°: score 2

def classify_forearm(angle: float) -> dict:
    """
    Clasifica posición de antebrazo.
    
    Args:
        angle: Ángulo en grados
    
    Returns:
        dict con score, range, description
    """
    if 60 <= angle <= 100:
        return {
            'score': 1,
            'range': '60-100°',
            'description': f'Ángulo óptimo {angle}°'
        }
    elif angle < 60:
        return {
            'score': 2,
            'range': '<60°',
            'description': f'Ángulo bajo {angle}°'
        }
    else:  # angle > 100
        return {
            'score': 2,
            'range': '>100°',
            'description': f'Ángulo alto {angle}°'
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MUÑECA
# ═══════════════════════════════════════════════════════════════════════════════
# -15° a +15°: score 1
# Flexión >15°: score 2
# Extensión >15°: score 2
# Ajuste: desviada +1

def classify_wrist(angle: float, direction: str) -> dict:
    """
    Clasifica posición de muñeca.
    
    Args:
        angle: Ángulo en grados
        direction: 'flexion', 'extension', 'neutral'
    
    Returns:
        dict con base_score, range, description
    """
    if direction == 'neutral':
        if abs(angle) <= 15:
            return {
                'base_score': 1,
                'range': '-15° a +15°',
                'description': 'Posición neutra'
            }
        elif angle > 15:
            return {
                'base_score': 2,
                'range': '>15° flexión',
                'description': f'Flexión {angle}°'
            }
        else:
            return {
                'base_score': 2,
                'range': '>15° extensión',
                'description': f'Extensión {abs(angle)}°'
            }
    
    elif direction == 'flexion':
        if angle <= 15:
            return {
                'base_score': 1,
                'range': '0-15° flexión',
                'description': f'Flexión {angle}°'
            }
        else:
            return {
                'base_score': 2,
                'range': '>15° flexión',
                'description': f'Flexión {angle}°'
            }
    
    elif direction == 'extension':
        if angle <= 15:
            return {
                'base_score': 1,
                'range': '0-15° extensión',
                'description': f'Extensión {angle}°'
            }
        else:
            return {
                'base_score': 2,
                'range': '>15° extensión',
                'description': f'Extensión {angle}°'
            }
    
    return {
        'base_score': 1,
        'range': 'desconocido',
        'description': 'Error en clasificación'
    }
