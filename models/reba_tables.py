"""
models/reba_tables.py - Tablas REBA centralizadas (A, B, C)

Fuente única de verdad para el cálculo REBA.
Todas las matrices extraídas del PDF oficial REBA Worksheet - Spanish Version.

Estructura:
  - TABLE_A: Postura A (Cuello × Torso × Piernas)
  - TABLE_B: Postura B (Brazo × Antebrazo × Muñeca)
  - TABLE_C: Matriz final (Puntaje A × Puntaje B)
  - RISK_CLASSIFICATION: Clasificación de riesgo

NO usar if/else dispersos. Consultar SOLO estas matrices.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TABLA A: PUNTAJE DE POSTURA (Cuello + Torso + Piernas)
# ═══════════════════════════════════════════════════════════════════════════════
# Estructura: TABLE_A[piernas][torso][cuello] = puntaje_a
# 
# Índices:
#   piernas: 1-6 (convertir a índice 0-5)
#   torso: 1-5 (convertir a índice 0-4)
#   cuello: 1-3 (convertir a índice 0-2)
#
# Valores: 1-9

TABLE_A = {
    # PIERNAS = 1
    1: {
        1: [1, 2, 2],      # Torso 1: Cuello 1→1, 2→2, 3→2
        2: [3, 4, 4],      # Torso 2: Cuello 1→3, 2→4, 3→4
        3: [3, 4, 5],      # Torso 3
        4: [4, 5, 6],      # Torso 4
        5: [4, 6, 7],      # Torso 5
    },
    # PIERNAS = 2
    2: {
        1: [2, 3, 4],
        2: [3, 4, 5],
        3: [3, 4, 6],
        4: [5, 6, 7],
        5: [5, 7, 8],
    },
    # PIERNAS = 3
    3: {
        1: [2, 3, 4],
        2: [3, 4, 5],
        3: [4, 5, 6],
        4: [5, 6, 7],
        5: [6, 7, 8],
    },
    # PIERNAS = 4
    4: {
        1: [3, 4, 5],
        2: [4, 5, 6],
        3: [4, 5, 7],
        4: [5, 7, 8],
        5: [6, 8, 9],
    },
    # PIERNAS = 5
    5: {
        1: [4, 5, 6],
        2: [4, 6, 7],
        3: [5, 6, 8],
        4: [6, 7, 9],
        5: [7, 8, 9],
    },
    # PIERNAS = 6
    6: {
        1: [4, 6, 7],
        2: [5, 6, 8],
        3: [5, 7, 8],
        4: [6, 8, 9],
        5: [7, 9, 9],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# TABLA B: PUNTAJE DE POSTURA BRAZOS/MUÑECA
# ═══════════════════════════════════════════════════════════════════════════════
# Estructura: TABLE_B[brazo][antebrazo][muñeca] = puntaje_b
#
# Índices:
#   brazo: 1-6 (convertir a índice 0-5)
#   antebrazo: 1-2 (convertir a índice 0-1)
#   muñeca: 1-3 (convertir a índice 0-2)
#
# Valores: 1-9

TABLE_B = {
    # BRAZO = 1
    1: {
        1: [1, 2, 2],      # Antebrazo 1: Muñeca 1→1, 2→2, 3→2
        2: [1, 2, 3],      # Antebrazo 2
    },
    # BRAZO = 2
    2: {
        1: [1, 2, 3],
        2: [2, 3, 4],
    },
    # BRAZO = 3
    3: {
        1: [3, 4, 5],
        2: [4, 5, 5],
    },
    # BRAZO = 4
    4: {
        1: [4, 5, 5],
        2: [5, 6, 7],
    },
    # BRAZO = 5
    5: {
        1: [6, 7, 8],
        2: [7, 8, 8],
    },
    # BRAZO = 6
    6: {
        1: [7, 8, 8],
        2: [8, 9, 9],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# TABLA C: MATRIZ FINAL (Puntaje A × Puntaje B)
# ═══════════════════════════════════════════════════════════════════════════════
# Estructura: TABLE_C[puntaje_a][puntaje_b] = puntaje_c
#
# Índices:
#   puntaje_a: 1-12 (convertir a índice 0-11)
#   puntaje_b: 1-12 (convertir a índice 0-11)
#
# Valores: 1-12
# Nota: Puntaje A es FILA, Puntaje B es COLUMNA

TABLE_C = [
    # A1: [1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 7, 7]
    [1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 7, 7],
    # A2: [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 8]
    [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 8],
    # A3: [2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 8, 8]
    [2, 3, 3, 4, 5, 5, 6, 7, 7, 8, 8, 8],
    # A4: [3, 4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9]
    [3, 4, 4, 5, 6, 6, 7, 8, 8, 9, 9, 9],
    # A5: [4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9]
    [4, 5, 5, 6, 7, 7, 8, 9, 9, 9, 9, 9],
    # A6: [6, 6, 6, 7, 8, 8, 9, 9, 10, 10, 10, 10]
    [6, 6, 6, 7, 8, 8, 9, 9, 10, 10, 10, 10],
    # A7: [7, 7, 7, 8, 9, 9, 9, 10, 10, 11, 11, 11]
    [7, 7, 7, 8, 9, 9, 9, 10, 10, 11, 11, 11],
    # A8: [8, 8, 8, 9, 10, 10, 10, 10, 10, 11, 11, 11]
    [8, 8, 8, 9, 10, 10, 10, 11, 11, 12, 12, 12],
    # A9: [9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12]
    [9, 9, 9, 10, 11, 11, 11, 12, 12, 12, 12, 12],
    # A10: [10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 12]
    [10, 10, 10, 11, 12, 12, 12, 12, 12, 12, 12, 12],
    # A11: [11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12]
    [11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    # A12: [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]
    [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
]


# ═══════════════════════════════════════════════════════════════════════════════
# CLASIFICACIÓN DE RIESGO
# ═══════════════════════════════════════════════════════════════════════════════

RISK_CLASSIFICATION = {
    1: {
        'level': 'Riesgo mínimo',
        'action': 'No intervenir'
    },
    2: {
        'level': 'Riesgo bajo',
        'action': 'Podría requerir modificación'
    },
    3: {
        'level': 'Riesgo bajo',
        'action': 'Podría requerir modificación'
    },
    4: {
        'level': 'Riesgo medio',
        'action': 'Investigar más, modificar pronto'
    },
    5: {
        'level': 'Riesgo medio',
        'action': 'Investigar más, modificar pronto'
    },
    6: {
        'level': 'Riesgo medio',
        'action': 'Investigar más, modificar pronto'
    },
    7: {
        'level': 'Riesgo medio',
        'action': 'Investigar más, modificar pronto'
    },
    8: {
        'level': 'Riesgo alto',
        'action': 'Investigar e implementar modificación'
    },
    9: {
        'level': 'Riesgo alto',
        'action': 'Investigar e implementar modificación'
    },
    10: {
        'level': 'Riesgo alto',
        'action': 'Investigar e implementar modificación'
    },
}


def get_risk_classification(score: int) -> dict:
    """
    Obtiene la clasificación de riesgo para un puntaje REBA.
    
    Args:
        score: Puntaje REBA final (1-12+)
    
    Returns:
        dict: {'level': str, 'action': str}
    """
    if score >= 11:
        return {
            'level': 'Riesgo muy alto',
            'action': 'Implementar modificación'
        }
    
    return RISK_CLASSIFICATION.get(score, {
        'level': 'Desconocido',
        'action': 'Error en puntuación'
    })


def get_table_a(piernas: int, torso: int, cuello: int) -> int:
    """
    Consulta Tabla A.
    
    Args:
        piernas: 1-6
        torso: 1-5
        cuello: 1-3
    
    Returns:
        int: Puntaje A (1-9)
    """
    if not (1 <= piernas <= 6 and 1 <= torso <= 5 and 1 <= cuello <= 3):
        raise ValueError(f"Índices fuera de rango: piernas={piernas}, torso={torso}, cuello={cuello}")
    
    return TABLE_A[piernas][torso][cuello - 1]


def get_table_b(brazo: int, antebrazo: int, muñeca: int) -> int:
    """
    Consulta Tabla B.
    
    Args:
        brazo: 1-6
        antebrazo: 1-2
        muñeca: 1-3
    
    Returns:
        int: Puntaje B (1-9)
    """
    if not (1 <= brazo <= 6 and 1 <= antebrazo <= 2 and 1 <= muñeca <= 3):
        raise ValueError(f"Índices fuera de rango: brazo={brazo}, antebrazo={antebrazo}, muñeca={muñeca}")
    
    return TABLE_B[brazo][antebrazo][muñeca - 1]


def get_table_c(score_a: int, score_b: int) -> int:
    """
    Consulta Tabla C.
    
    Args:
        score_a: Puntaje A (1-12)
        score_b: Puntaje B (1-12)
    
    Returns:
        int: Puntaje C (1-12)
    """
    if not (1 <= score_a <= 12 and 1 <= score_b <= 12):
        raise ValueError(f"Puntajes fuera de rango: A={score_a}, B={score_b}")
    
    return TABLE_C[score_a - 1][score_b - 1]
