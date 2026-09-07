"""
models/reba_calculator.py - Calculadora central REBA

Función única: calculateREBA(evaluation_data)

Integra:
  - Clasificación angular (ángulo + dirección → puntaje base)
  - Tablas A, B, C (matrices centralizadas)
  - Modificadores (fuerza, acoplamiento, actividad)
  - Cálculo de puntaje final
  - Clasificación de riesgo

Retorna objeto estructurado con trazabilidad completa.
"""

from models.reba_tables import get_table_a, get_table_b, get_table_c, get_risk_classification
from models.angle_classification import (
    classify_neck,
    classify_trunk,
    classify_legs,
    classify_upper_arm,
    classify_forearm,
    classify_wrist
)


def calculate_reba(evaluation_data: dict) -> dict:
    """
    Calcula puntaje REBA completo con trazabilidad.
    
    Args:
        evaluation_data: dict con estructura completa
        {
            'neck': {'angle': float, 'direction': 'flexion'|'extension'|'neutral', 'twisted': bool, 'tilted': bool},
            'trunk': {'angle': float, 'direction': str, 'twisted': bool, 'tilted': bool},
            'legs': {'condition': str, 'knee_angle': float},
            'upper_arm': {'angle': float, 'direction': str, 'shoulder_raised': bool, 'abducted': bool, 'supported': bool},
            'forearm': {'angle': float},
            'wrist': {'angle': float, 'direction': str, 'deviated': bool},
            'load': {'value': float, 'unit': 'kg'|'lb'},
            'shock': bool,
            'coupling': 'good'|'regular'|'poor'|'unacceptable',
            'activity': {'static': bool, 'repetitive': bool, 'rapid_change': bool}
        }
    
    Returns:
        dict: Resultado estructurado con trazabilidad completa
    """
    
    result = {
        'segments': {},
        'posture_a_calculation': {},
        'load_score': 0,
        'score_a': 0,
        'posture_b_calculation': {},
        'coupling_score': 0,
        'score_b': 0,
        'score_c': 0,
        'activity_score': 0,
        'final_score': 0,
        'risk_level': '',
        'action': '',
        'trace': []  # Trazabilidad completa
    }
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # GRUPO A: CUELLO, TORSO, PIERNAS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # CUELLO
    neck_classification = classify_neck(
        evaluation_data['neck']['angle'],
        evaluation_data['neck']['direction']
    )
    neck_base = neck_classification['base_score']
    neck_adjustments = 0
    
    if evaluation_data['neck'].get('twisted', False):
        neck_adjustments += 1
    if evaluation_data['neck'].get('tilted', False):
        neck_adjustments += 1
    
    neck_final = neck_base + neck_adjustments
    
    result['segments']['neck'] = {
        'angle': evaluation_data['neck']['angle'],
        'direction': evaluation_data['neck']['direction'],
        'range': neck_classification['range'],
        'base_score': neck_base,
        'twisted': evaluation_data['neck'].get('twisted', False),
        'tilted': evaluation_data['neck'].get('tilted', False),
        'adjustments': neck_adjustments,
        'final_score': neck_final
    }
    result['trace'].append(f"Cuello: {evaluation_data['neck']['angle']}° {evaluation_data['neck']['direction']} → base {neck_base} + ajustes {neck_adjustments} = {neck_final}")
    
    # TORSO
    trunk_classification = classify_trunk(
        evaluation_data['trunk']['angle'],
        evaluation_data['trunk']['direction']
    )
    trunk_base = trunk_classification['base_score']
    trunk_adjustments = 0
    
    if evaluation_data['trunk'].get('twisted', False):
        trunk_adjustments += 1
    if evaluation_data['trunk'].get('tilted', False):
        trunk_adjustments += 1
    
    trunk_final = trunk_base + trunk_adjustments
    
    result['segments']['trunk'] = {
        'angle': evaluation_data['trunk']['angle'],
        'direction': evaluation_data['trunk']['direction'],
        'range': trunk_classification['range'],
        'base_score': trunk_base,
        'twisted': evaluation_data['trunk'].get('twisted', False),
        'tilted': evaluation_data['trunk'].get('tilted', False),
        'adjustments': trunk_adjustments,
        'final_score': trunk_final
    }
    result['trace'].append(f"Torso: {evaluation_data['trunk']['angle']}° {evaluation_data['trunk']['direction']} → base {trunk_base} + ajustes {trunk_adjustments} = {trunk_final}")
    
    # PIERNAS
    legs_classification = classify_legs(
        evaluation_data['legs']['condition'],
        evaluation_data['legs'].get('knee_angle', None)
    )
    legs_base = legs_classification['base_score']
    legs_knee_adjustment = legs_classification.get('knee_adjustment', 0)
    legs_final = legs_base + legs_knee_adjustment
    
    result['segments']['legs'] = {
        'condition': evaluation_data['legs']['condition'],
        'knee_angle': evaluation_data['legs'].get('knee_angle', None),
        'base_score': legs_base,
        'knee_adjustment': legs_knee_adjustment,
        'final_score': legs_final
    }
    result['trace'].append(f"Piernas: {evaluation_data['legs']['condition']} → base {legs_base} + ajuste rodilla {legs_knee_adjustment} = {legs_final}")
    
    # TABLA A
    try:
        posture_a = get_table_a(legs_final, trunk_final, neck_final)
        result['posture_a_calculation'] = {
            'piernas': legs_final,
            'torso': trunk_final,
            'cuello': neck_final,
            'posture_a': posture_a
        }
        result['trace'].append(f"Tabla A[piernas={legs_final}, torso={trunk_final}, cuello={neck_final}] = {posture_a}")
    except ValueError as e:
        result['posture_a_calculation'] = {'error': str(e)}
        result['trace'].append(f"ERROR en Tabla A: {e}")
        return result
    
    # FUERZA/CARGA
    load_data = evaluation_data.get('load', {})
    load_value = load_data.get('value', 0)
    load_unit = load_data.get('unit', 'kg')
    
    # Normalizar a lbs si es necesario
    if load_unit == 'kg':
        load_lbs = load_value * 2.20462
    else:
        load_lbs = load_value
    
    load_score = 0
    if load_lbs < 11:
        load_score = 0
    elif load_lbs <= 22:
        load_score = 1
    else:
        load_score = 2
    
    if evaluation_data.get('shock', False):
        load_score += 1
    
    result['load_score'] = load_score
    result['load_data'] = {
        'value': load_value,
        'unit': load_unit,
        'normalized_lbs': load_lbs,
        'base_score': load_score if not evaluation_data.get('shock', False) else load_score - 1,
        'shock': evaluation_data.get('shock', False),
        'final_score': load_score
    }
    result['trace'].append(f"Fuerza/Carga: {load_value} {load_unit} ({load_lbs:.1f} lbs) → {load_score}")
    
    # PUNTAJE A
    score_a = posture_a + load_score
    result['score_a'] = score_a
    result['trace'].append(f"Puntaje A: {posture_a} (postura) + {load_score} (carga) = {score_a}")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # GRUPO B: BRAZO, ANTEBRAZO, MUÑECA
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # BRAZO
    arm_classification = classify_upper_arm(
        evaluation_data['upper_arm']['angle'],
        evaluation_data['upper_arm']['direction']
    )
    arm_base = arm_classification['base_score']
    arm_adjustments = 0
    
    if evaluation_data['upper_arm'].get('shoulder_raised', False):
        arm_adjustments += 1
    if evaluation_data['upper_arm'].get('abducted', False):
        arm_adjustments += 1
    if evaluation_data['upper_arm'].get('supported', False):
        arm_adjustments -= 1
    
    arm_final = arm_base + arm_adjustments
    
    result['segments']['upper_arm'] = {
        'angle': evaluation_data['upper_arm']['angle'],
        'direction': evaluation_data['upper_arm']['direction'],
        'range': arm_classification['range'],
        'base_score': arm_base,
        'shoulder_raised': evaluation_data['upper_arm'].get('shoulder_raised', False),
        'abducted': evaluation_data['upper_arm'].get('abducted', False),
        'supported': evaluation_data['upper_arm'].get('supported', False),
        'adjustments': arm_adjustments,
        'final_score': arm_final
    }
    result['trace'].append(f"Brazo: {evaluation_data['upper_arm']['angle']}° {evaluation_data['upper_arm']['direction']} → base {arm_base} + ajustes {arm_adjustments} = {arm_final}")
    
    # ANTEBRAZO
    forearm_classification = classify_forearm(evaluation_data['forearm']['angle'])
    forearm_score = forearm_classification['score']
    
    result['segments']['forearm'] = {
        'angle': evaluation_data['forearm']['angle'],
        'range': forearm_classification['range'],
        'score': forearm_score
    }
    result['trace'].append(f"Antebrazo: {evaluation_data['forearm']['angle']}° → {forearm_score}")
    
    # MUÑECA
    wrist_classification = classify_wrist(
        evaluation_data['wrist']['angle'],
        evaluation_data['wrist']['direction']
    )
    wrist_base = wrist_classification['base_score']
    wrist_adjustment = 1 if evaluation_data['wrist'].get('deviated', False) else 0
    wrist_final = wrist_base + wrist_adjustment
    
    result['segments']['wrist'] = {
        'angle': evaluation_data['wrist']['angle'],
        'direction': evaluation_data['wrist']['direction'],
        'range': wrist_classification['range'],
        'base_score': wrist_base,
        'deviated': evaluation_data['wrist'].get('deviated', False),
        'adjustments': wrist_adjustment,
        'final_score': wrist_final
    }
    result['trace'].append(f"Muñeca: {evaluation_data['wrist']['angle']}° {evaluation_data['wrist']['direction']} → base {wrist_base} + ajustes {wrist_adjustment} = {wrist_final}")
    
    # TABLA B
    try:
        posture_b = get_table_b(arm_final, forearm_score, wrist_final)
        result['posture_b_calculation'] = {
            'brazo': arm_final,
            'antebrazo': forearm_score,
            'muñeca': wrist_final,
            'posture_b': posture_b
        }
        result['trace'].append(f"Tabla B[brazo={arm_final}, antebrazo={forearm_score}, muñeca={wrist_final}] = {posture_b}")
    except ValueError as e:
        result['posture_b_calculation'] = {'error': str(e)}
        result['trace'].append(f"ERROR en Tabla B: {e}")
        return result
    
    # ACOPLAMIENTO
    coupling_map = {
        'good': 0,
        'regular': 1,
        'poor': 2,
        'unacceptable': 3
    }
    coupling_score = coupling_map.get(evaluation_data.get('coupling', 'regular'), 1)
    
    result['coupling_score'] = coupling_score
    result['coupling_data'] = {
        'type': evaluation_data.get('coupling', 'regular'),
        'score': coupling_score
    }
    result['trace'].append(f"Acoplamiento: {evaluation_data.get('coupling', 'regular')} → {coupling_score}")
    
    # PUNTAJE B
    score_b = posture_b + coupling_score
    result['score_b'] = score_b
    result['trace'].append(f"Puntaje B: {posture_b} (postura) + {coupling_score} (acoplamiento) = {score_b}")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # TABLA C
    # ═══════════════════════════════════════════════════════════════════════════════
    
    # Score A es fila, Score B es columna
    # Pero ambos están limitados a rango 1-12
    score_a_bounded = min(score_a, 12)
    score_b_bounded = min(score_b, 12)
    
    try:
        score_c = get_table_c(score_a_bounded, score_b_bounded)
        result['score_c'] = score_c
        result['table_c_lookup'] = {
            'score_a': score_a_bounded,
            'score_b': score_b_bounded,
            'score_c': score_c
        }
        result['trace'].append(f"Tabla C[A={score_a_bounded}, B={score_b_bounded}] = {score_c}")
    except ValueError as e:
        result['score_c'] = 0
        result['trace'].append(f"ERROR en Tabla C: {e}")
        return result
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # ACTIVIDAD
    # ═══════════════════════════════════════════════════════════════════════════════
    
    activity_score = 0
    activity_data = evaluation_data.get('activity', {})
    
    if activity_data.get('static', False):
        activity_score += 1
    if activity_data.get('repetitive', False):
        activity_score += 1
    if activity_data.get('rapid_change', False):
        activity_score += 1
    
    result['activity_score'] = activity_score
    result['activity_data'] = {
        'static': activity_data.get('static', False),
        'repetitive': activity_data.get('repetitive', False),
        'rapid_change': activity_data.get('rapid_change', False),
        'total_score': activity_score
    }
    result['trace'].append(f"Actividad: estática={activity_data.get('static', False)} repetida={activity_data.get('repetitive', False)} rápida={activity_data.get('rapid_change', False)} → {activity_score}")
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # PUNTAJE REBA FINAL
    # ═══════════════════════════════════════════════════════════════════════════════
    
    final_score = score_c + activity_score
    
    # Limitar a máximo 12 (aunque puede ser >12 en teoría)
    final_score_display = min(final_score, 12)
    
    result['final_score'] = final_score
    result['final_score_display'] = final_score_display
    
    # CLASIFICACIÓN DE RIESGO
    risk_info = get_risk_classification(final_score)
    result['risk_level'] = risk_info['level']
    result['action'] = risk_info['action']
    
    result['trace'].append(f"Puntaje REBA Final: {score_c} (C) + {activity_score} (actividad) = {final_score}")
    result['trace'].append(f"Clasificación: {result['risk_level']} → {result['action']}")
    
    return result
