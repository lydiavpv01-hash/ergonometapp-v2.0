"""
models/apendice_i.py - APÉNDICE I: LEVANTAMIENTO DE CARGAS
Evaluación de tareas de levantamiento manual según NOM-036-1-STPS-2018
Extractor de app.py, refactorizado para v2
"""

import math


def calculate_apendice_i(data: dict) -> dict:
    """
    Calcula índice de levantamiento según ACGIH (NOM-036 Apéndice I)
    
    Fórmula: LI (Lifting Index) = Carga / RWL (Recommended Weight Limit)
    
    Args:
        data: Dict con parámetros de la tarea
        {
            'peso': float (kg),              # Peso de la carga
            'altura_origen': float (cm),    # Altura de inicio
            'altura_destino': float (cm),   # Altura de final
            'distancia_horizontal': float (cm),  # Distancia horizontal
            'angulo_giro': float (grados),  # Ángulo de giro
            'frecuencia': float (lev/min),  # Levantamientos por minuto
            'duracion': float (horas),      # Duración de la tarea
            'agarre': str,                  # 'bueno', 'aceptable', 'pobre'
        }
    
    Returns:
        Dict con scores, análisis y recomendaciones
    """
    
    # ════════════════════════════════════════════════════════════════════════════════
    # EXTRACCIÓN DE PARÁMETROS
    # ════════════════════════════════════════════════════════════════════════════════
    
    peso = float(data.get('peso', 15))              # kg
    altura_origen = float(data.get('altura_origen', 75))      # cm desde piso
    altura_destino = float(data.get('altura_destino', 115))   # cm desde piso
    distancia_horizontal = float(data.get('distancia_horizontal', 30))  # cm desde cuerpo
    angulo_giro = float(data.get('angulo_giro', 0))           # grados
    frecuencia = float(data.get('frecuencia', 2))             # lev/min
    duracion = float(data.get('duracion', 1))                 # horas
    agarre = str(data.get('agarre', 'aceptable')).lower()    # bueno/aceptable/pobre
    
    # Altura promedio del levantamiento
    altura_promedio = (altura_origen + altura_destino) / 2
    distancia_vertical = abs(altura_destino - altura_origen)
    
    # ════════════════════════════════════════════════════════════════════════════════
    # CÁLCULO DEL RWL (RECOMMENDED WEIGHT LIMIT)
    # RWL = LC × HM × VM × DM × AM × FM × CM
    # ════════════════════════════════════════════════════════════════════════════════
    
    # 1. LC - Load Constant = 23 kg (constante)
    LC = 23
    
    # 2. HM - Horizontal Multiplier = 25 / H
    # H = distancia horizontal en cm (rango: 25-63 cm)
    H = max(25, min(distancia_horizontal, 63))
    HM = 25 / H
    
    # 3. VM - Vertical Multiplier = 1 - 0.003 × (V - 75)
    # V = altura del origen en cm (rango: 0-175 cm)
    V = max(0, min(altura_origen, 175))
    VM = 1 - (0.003 * abs(V - 75))
    VM = max(0, VM)  # No puede ser negativo
    
    # 4. DM - Distance Multiplier = 0.82 + 4.5 / D
    # D = distancia vertical en cm (rango: 25-175 cm)
    D = max(25, min(distancia_vertical, 175))
    DM = 0.82 + (4.5 / D)
    DM = min(1, DM)  # Máximo 1.0
    
    # 5. AM - Asymmetric Angle Multiplier = 1 - 0.0032 × A
    # A = ángulo de giro en grados (rango: 0-135°)
    A = max(0, min(angulo_giro, 135))
    AM = 1 - (0.0032 * A)
    AM = max(0, AM)
    
    # 6. FM - Frequency Multiplier (tabla)
    FM = get_frequency_multiplier(frecuencia, duracion)
    
    # 7. CM - Coupling/Agarre Multiplier (tabla)
    CM = get_coupling_multiplier(agarre, altura_promedio)
    
    # RWL final
    RWL = LC * HM * VM * DM * AM * FM * CM
    
    # ════════════════════════════════════════════════════════════════════════════════
    # ÍNDICE DE LEVANTAMIENTO (LI)
    # ════════════════════════════════════════════════════════════════════════════════
    
    if RWL > 0:
        LI = peso / RWL
    else:
        LI = 999  # Error
    
    # ════════════════════════════════════════════════════════════════════════════════
    # CLASIFICACIÓN DE RIESGO
    # ════════════════════════════════════════════════════════════════════════════════
    
    if LI <= 0.75:
        nivel_riesgo = 'BAJO'
        color = '#27ae60'
        badge = 'success'
        descripcion = 'Riesgo aceptable - El 99% de los trabajadores pueden realizar esta tarea'
        accion = 'Mantenimiento'
    elif LI <= 1.0:
        nivel_riesgo = 'LIGERO'
        color = '#2ecc71'
        badge = 'info'
        descripcion = 'Riesgo ligero - El 99% de las mujeres pueden realizar esta tarea'
        accion = 'Vigilancia'
    elif LI <= 1.5:
        nivel_riesgo = 'MODERADO'
        color = '#f39c12'
        badge = 'warning'
        descripcion = 'Riesgo moderado - Algunos trabajadores pueden sufrir lesiones'
        accion = 'Intervención recomendada'
    else:
        nivel_riesgo = 'ALTO'
        color = '#e74c3c'
        badge = 'danger'
        descripcion = 'Riesgo elevado - Muchos trabajadores pueden sufrir lesiones'
        accion = 'Intervención inmediata'
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RECOMENDACIONES
    # ════════════════════════════════════════════════════════════════════════════════
    
    recomendaciones = []
    
    if HM < 0.9:
        recomendaciones.append(
            '📏 DISTANCIA HORIZONTAL: Acercar la carga al cuerpo (aumentar HM: %.2f)' % HM
        )
    
    if VM < 0.9:
        recomendaciones.append(
            '📊 ALTURA: Optimizar altura de origen/destino (aumentar VM: %.2f)' % VM
        )
    
    if DM < 0.9:
        recomendaciones.append(
            '📐 DISTANCIA VERTICAL: Reducir distancia de levantamiento (aumentar DM: %.2f)' % DM
        )
    
    if AM < 0.9:
        recomendaciones.append(
            '🔄 ROTACIÓN: Minimizar ángulo de giro (aumentar AM: %.2f)' % AM
        )
    
    if FM < 0.9:
        recomendaciones.append(
            '⏱️ FRECUENCIA: Reducir número de levantamientos o duración (aumentar FM: %.2f)' % FM
        )
    
    if CM < 0.9:
        recomendaciones.append(
            '🤝 AGARRE: Mejorar agarre de la carga (aumentar CM: %.2f)' % CM
        )
    
    if LI > 1:
        recomendaciones.append(
            '🔴 ACCIÓN INMEDIATA: El peso excede el límite recomendado (LI: %.2f)' % LI
        )
        recomendaciones.append(
            '💡 Opciones: Reducir peso, aumentar RWL, mecanizar, usar equipos de asistencia'
        )
    
    # ════════════════════════════════════════════════════════════════════════════════
    # RESULTADO FINAL
    # ════════════════════════════════════════════════════════════════════════════════
    
    return {
        # Datos de entrada
        'peso': peso,
        'altura_origen': altura_origen,
        'altura_destino': altura_destino,
        'distancia_horizontal': distancia_horizontal,
        'angulo_giro': angulo_giro,
        'frecuencia': frecuencia,
        'duracion': duracion,
        'agarre': agarre,
        
        # Cálculos intermedios
        'altura_promedio': round(altura_promedio, 2),
        'distancia_vertical': round(distancia_vertical, 2),
        
        # Multiplicadores
        'multiplicadores': {
            'LC': LC,
            'HM': round(HM, 4),
            'VM': round(VM, 4),
            'DM': round(DM, 4),
            'AM': round(AM, 4),
            'FM': round(FM, 4),
            'CM': round(CM, 4),
        },
        
        # Resultados
        'RWL': round(RWL, 2),
        'LI': round(LI, 2),
        'nivel_riesgo': nivel_riesgo,
        'color': color,
        'badge': badge,
        'descripcion': descripcion,
        'accion': accion,
        
        # Recomendaciones
        'recomendaciones': recomendaciones if recomendaciones else [
            '✓ Tarea dentro de límites aceptables - Mantener vigilancia'
        ],
    }


def get_frequency_multiplier(freq: float, duracion: float) -> float:
    """
    Devuelve FM según frecuencia y duración
    
    Tabla ACGIH:
    freq/min  ≤1h   >1-2h  >2-8h
    0.2       1.00  0.95   0.85
    0.5       0.97  0.92   0.81
    1         0.94  0.88   0.75
    2         0.91  0.84   0.65
    3         0.88  0.79   0.55
    4         0.84  0.72   0.45
    5         0.80  0.60   0.35
    6         0.75  0.50   0.27
    7         0.70  0.42   0.22
    8         0.60  0.30   0.14
    9         0.52  0.26   0.10
    10        0.45  0.23   0.06
    12        0.41  0.21   0.03
    >15       0.27  0.00   0.00
    """
    
    tabla_fm = {
        0.2: (1.00, 0.95, 0.85),
        0.5: (0.97, 0.92, 0.81),
        1: (0.94, 0.88, 0.75),
        2: (0.91, 0.84, 0.65),
        3: (0.88, 0.79, 0.55),
        4: (0.84, 0.72, 0.45),
        5: (0.80, 0.60, 0.35),
        6: (0.75, 0.50, 0.27),
        7: (0.70, 0.42, 0.22),
        8: (0.60, 0.30, 0.14),
        9: (0.52, 0.26, 0.10),
        10: (0.45, 0.23, 0.06),
        12: (0.41, 0.21, 0.03),
        15: (0.27, 0.00, 0.00),
    }
    
    # Determinar categoría de duración
    if duracion <= 1:
        duracion_cat = 0
    elif duracion <= 2:
        duracion_cat = 1
    else:
        duracion_cat = 2
    
    # Encontrar FM más cercano
    freq = min(freq, 15)
    for f, (fm1, fm2, fm3) in tabla_fm.items():
        if freq <= f:
            valores = (fm1, fm2, fm3)
            return valores[duracion_cat]
    
    return 0.27


def get_coupling_multiplier(agarre: str, altura: float) -> float:
    """
    Devuelve CM según tipo de agarre y altura
    
    Tabla ACGIH:
    Agarre        Altura V    Altura V
                  <75cm       ≥75cm
    Bueno         1.00        1.00
    Aceptable     0.95        1.00
    Pobre         0.90        0.95
    """
    
    tabla_cm = {
        'bueno': (1.00, 1.00),
        'aceptable': (0.95, 1.00),
        'pobre': (0.90, 0.95),
    }
    
    agarre = agarre.lower()
    if agarre not in tabla_cm:
        agarre = 'aceptable'
    
    cm_bajo, cm_alto = tabla_cm[agarre]
    
    if altura < 75:
        return cm_bajo
    else:
        return cm_alto


def get_zona_segura(LI: float) -> dict:
    """Devuelve zona de seguridad según LI"""
    
    if LI <= 0.75:
        return {
            'zona': '🟢 ZONA VERDE',
            'descripcion': 'Completamente seguro',
            'limite_peso': 'Sin límite teórico',
        }
    elif LI <= 1.0:
        return {
            'zona': '🟡 ZONA AMARILLA',
            'descripcion': 'Seguro para mayoría',
            'limite_peso': 'Limitación para mujeres',
        }
    elif LI <= 1.5:
        return {
            'zona': '🟠 ZONA NARANJA',
            'descripcion': 'Requiere intervención',
            'limite_peso': 'Limitación importante',
        }
    else:
        return {
            'zona': '🔴 ZONA ROJA',
            'descripcion': 'Peligroso',
            'limite_peso': 'Intervención inmediata',
        }
