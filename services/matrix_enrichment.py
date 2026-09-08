import re
import unicodedata


def _safe_key(text):
    text = unicodedata.normalize('NFD', str(text or '')).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'(^_|_$)', '', re.sub(r'[^a-z0-9]+', '_', text))[:70]


def _band_from_color(color):
    c = (color or '').strip().lower()
    if c == 'verde':
        return 'Bajo · Aceptable'
    if c in ('amarillo', 'naranja'):
        return 'Medio · Posible'
    if c == 'rojo':
        return 'Alto · Significativo'
    if c in ('magenta', 'morado'):
        return 'Muy Alto · Inaceptable'
    return '—'


def _snapshot_fields(payload):
    snap = payload.get('snapshot') or {}
    fields = snap.get('fields') or []
    by_name = {f.get('name', ''): f for f in fields if f.get('name')}
    by_label = {_safe_key(f.get('label', '')): f for f in fields if f.get('label')}
    return fields, by_name, by_label


def _value_from(by_name, by_label, *names):
    for name in names:
        item = by_name.get(name) or {}
        value = str(item.get('value', '') or '').strip()
        if value:
            return value
    for name in names:
        item = by_label.get(_safe_key(name)) or {}
        value = str(item.get('value', '') or '').strip()
        if value:
            return value
    return ''


def install_matrix_enrichment(main_module):
    original = main_module._generic_matrix

    def enriched(e, payload, result):
        matrix = original(e, payload, result)
        _, by_name, by_label = _snapshot_fields(payload)
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

        # La condición seleccionada se presenta con contexto completo de la
        # puntuación sin alterar ningún valor calculado por el método.
        for item in matrix.get('justification_rows') or []:
            color = item.get('color') or ''
            if not color:
                value = item.get('value')
                title = item.get('title') or ''
                key = ''
                if 'AI2' in title:
                    key = 'ai2'
                elif 'AI3' in title:
                    key = 'ai3'
                elif 'AI4' in title:
                    key = 'ai4'
                try:
                    color, color_class = main_module._color_for(key, value, matrix.get('kind', 'APENDICE_I'))
                    item['color_class'] = color_class
                except Exception:
                    color = ''
            risk_level = _band_from_color(color)
            raw_condition = item.get('condition') or '—'
            item['color'] = color or '—'
            item['risk_level'] = risk_level
            item['condition_detail'] = raw_condition
            item['condition'] = f"{raw_condition} · Nivel: {risk_level} · Color: {color or '—'}"

        return matrix

    main_module._generic_matrix = enriched
