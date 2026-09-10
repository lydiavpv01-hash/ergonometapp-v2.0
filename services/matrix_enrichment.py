import re
import unicodedata


def _safe_key(text):
    text = unicodedata.normalize('NFD', str(text or '')).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'(^_|_$)', '', re.sub(r'[^a-z0-9]+', '_', text))[:70]


def _band_from_color(color):
    c = (color or '').strip().lower()
    if c == 'verde': return 'Bajo · Aceptable'
    if c in ('amarillo', 'naranja'): return 'Medio · Posible'
    if c == 'rojo': return 'Alto · Significativo'
    if c in ('magenta', 'morado'): return 'Muy Alto · Inaceptable'
    return '—'


def _snapshot_fields(payload):
    snap = payload.get('snapshot') or {}
    fields = snap.get('fields') or []
    by_name = {f.get('name', ''): f for f in fields if f.get('name')}
    by_label = {_safe_key(f.get('label', '')): f for f in fields if f.get('label')}
    return fields, by_name, by_label


def _snapshot_selections(payload):
    selections = (payload.get('snapshot') or {}).get('selections') or []
    return {s.get('factor', ''): s for s in selections if s.get('factor')}


def _value_from(by_name, by_label, *names):
    for name in names:
        item = by_name.get(name) or {}
        value = str(item.get('value', '') or '').strip()
        if value: return value
    for name in names:
        item = by_label.get(_safe_key(name)) or {}
        value = str(item.get('value', '') or '').strip()
        if value: return value
    return ''


def _numeric(value):
    if value is None or value == '': return None
    try:
        n = float(value)
        return int(n) if n.is_integer() else n
    except Exception:
        return None


AI1_KEYS = [
    ('Peso de la carga / frecuencia de transporte', 'ai2_peso', 'ai3_peso', 'ai4_peso'),
    ('Distancia horizontal entre las manos y la parte inferior de la espalda', 'ai2_distancia', 'ai3_distancia', 'ai4_distancia'),
    ('Región de levantamiento vertical', 'ai2_vertical', None, 'ai4_vertical'),
    ('Torsión y flexión lateral del torso / Carga asimétrica sobre el torso', 'ai2_torsion', 'ai3_asimetria', 'ai4_torsion'),
    ('Restricciones posturales', 'ai2_restriccion', 'ai3_restriccion', 'ai4_restriccion'),
    ('Acoplamiento mano-carga (elementos de sujeción)', 'ai2_agarre', 'ai3_agarre', 'ai4_agarre'),
    ('Superficie de trabajo', 'ai2_superficie', 'ai3_superficie', 'ai4_superficie'),
    ('Otros factores ambientales', 'ai2_ambiente', 'ai3_ambiente', 'ai4_ambiente'),
    ('Distancia de transporte', None, 'ai3_distancia_transporte', None),
    ('Obstáculos en la ruta', None, 'ai3_obstaculos', None),
    ('Comunicación, coordinación y control', None, None, 'ai4_coordinacion'),
]


def install_matrix_enrichment(main_module):
    original = main_module._generic_matrix

    def enriched(e, payload, result):
        payload = dict(payload or {})
        try:
            from models.evaluation_upload import EvaluationUpload
            saved = EvaluationUpload.query.filter_by(evaluation_id=e.id, usuario=e.usuario).order_by(EvaluationUpload.position.asc(), EvaluationUpload.id.asc()).all()
            if saved:
                payload['uploads'] = [u.as_payload() for u in saved]
        except Exception:
            pass

        matrix = original(e, payload, result)
        _, by_name, by_label = _snapshot_fields(payload)
        sel_by = _snapshot_selections(payload)
        meta = payload.get('meta') or {}

        matrix_meta = matrix.setdefault('meta', {})
        matrix_meta.update({
            'empresa': _value_from(by_name, by_label, 'empresa', 'razon_social', 'Razón Social', 'Empresa', 'Empresa:'),
            'area': _value_from(by_name, by_label, 'area', 'Área', 'Area'),
            'subarea': _value_from(by_name, by_label, 'subarea', 'Subárea', 'Subarea'),
            'fecha': _value_from(by_name, by_label, 'fecha', 'Fecha') or meta.get('fecha') or getattr(e, 'fecha', '') or '',
            'puesto': _value_from(by_name, by_label, 'puesto', 'Puesto de trabajo', 'Puesto') or meta.get('puesto') or getattr(e, 'puesto', '') or '',
            'trabajador': _value_from(by_name, by_label, 'trabajador', 'grupo', 'Trabajador / grupo', 'Trabajador') or meta.get('trabajador') or getattr(e, 'trabajador', '') or '',
            'actividad': _value_from(by_name, by_label, 'actividad', 'tarea', 'Actividad/tarea', 'Actividad / tarea', 'Actividad'),
            'descripcion': _value_from(by_name, by_label, 'descripcion', 'Descripción', 'Descripción de actividad', 'Descripcion de actividad'),
        })

        if matrix.get('kind') == 'APENDICE_I':
            key_by_title = {}
            for label, k2, k3, k4 in AI1_KEYS:
                key_by_title[(label, 'AI2')] = k2; key_by_title[(label, 'AI3')] = k3; key_by_title[(label, 'AI4')] = k4
            for row in matrix.get('factor_rows') or []:
                label = row.get('label') or ''
                keys = next(((k2,k3,k4) for lbl,k2,k3,k4 in AI1_KEYS if lbl==label),(None,None,None))
                for cell,key in zip(row.get('cells') or [],keys):
                    if not key: continue
                    sel=sel_by.get(key) or {}; value=_numeric(cell.get('value'))
                    if value is None:
                        value=_numeric(sel.get('value'))
                        if value is not None: cell['value']=value
                    if not cell.get('condition') and sel.get('selection'): cell['condition']=sel.get('selection')
                    if value is not None:
                        if key.endswith('_peso'):
                            color='Verde' if value==0 else 'Naranja' if value==4 else 'Rojo' if value==6 else 'Morado'
                            color_class='c-verde' if value==0 else 'c-naranja' if value==4 else 'c-rojo' if value==6 else 'c-morado'
                        else: color,color_class=main_module._color_for(key,value,'APENDICE_I')
                        cell['color']=color; cell['color_class']=color_class

            # La fila de información general toma exactamente los datos de la captura AI.2.
            # No se reconstruyen a partir de texto si el snapshot ya los conserva.
            ai2_cell = ((matrix.get('factor_rows') or [{}])[0].get('cells') or [{}])[0]
            count = _value_from(by_name, by_label, 'numero_levantamientos', 'liftCount', 'Número de levantamientos')
            interval = _value_from(by_name, by_label, 'cada_cuanto_tiempo', 'liftInterval', 'Cada cuánto tiempo', 'Cada')
            unit = _value_from(by_name, by_label, 'unidad_tiempo', 'liftUnit', 'Unidad de tiempo')
            if unit.lower() in ('minutos','minuto','mins'):
                unit = 'min'
            elif unit.lower() in ('segundos','segundo','secs','sec'):
                unit = 'seg'
            matrix['interpolation'] = {
                'color': ai2_cell.get('color') or '',
                'value': ai2_cell.get('value'),
                'color_class': ai2_cell.get('color_class') or 'c-empty',
                'count': count,
                'interval': interval,
                'unit': unit,
            }

            for item in matrix.get('justification_rows') or []:
                title=item.get('title') or ''; label,sec=title.rsplit(' · ',1) if ' · ' in title else (title,'')
                key=key_by_title.get((label,sec)); sel=sel_by.get(key) if key else {}; value=_numeric(item.get('value'))
                if value is None and sel:
                    value=_numeric(sel.get('value'))
                    if value is not None:item['value']=value
                if not item.get('condition') and sel:item['condition']=sel.get('selection','')
                if key and key.endswith('_peso') and value is not None:
                    color='Verde' if value==0 else 'Naranja' if value==4 else 'Rojo' if value==6 else 'Morado'; color_class='c-verde' if value==0 else 'c-naranja' if value==4 else 'c-rojo' if value==6 else 'c-morado'
                else: color,color_class=main_module._color_for(key or '',value,'APENDICE_I') if value is not None else ('','c-empty')
                item['color']=color or '—'; item['color_class']=color_class; item['risk_level']=_band_from_color(color)
                raw=item.get('condition') or '—'; item['condition_detail']=raw; item['condition']=f"{raw} · Nivel: {item['risk_level']} · Color: {color or '—'}"
                if key:
                    sk=_safe_key(key); item['conclusion']=_value_from(by_name,by_label,'conclusion_'+sk,'Conclusión · '+label,'Conclusión del inciso')
        else:
            for item in matrix.get('justification_rows') or []:
                value=_numeric(item.get('value')); color=item.get('color') or ''; color_class=item.get('color_class') or 'c-empty'
                if not color and value is not None: color,color_class=main_module._color_for('',value,matrix.get('kind','APENDICE_II'))
                item['color']=color or '—'; item['color_class']=color_class; item['risk_level']=_band_from_color(color)
                raw=item.get('condition') or '—'; item['condition_detail']=raw; item['condition']=f"{raw} · Nivel: {item['risk_level']} · Color: {color or '—'}"
        return matrix

    main_module._generic_matrix = enriched
