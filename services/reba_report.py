from io import BytesIO
import base64
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

OLIVE = colors.HexColor('#60752f')
DARK = colors.HexColor('#263126')
SOFT = colors.HexColor('#f1f5ea')
LINE = colors.HexColor('#dfe5dc')
MUTED = colors.HexColor('#69716c')


def _data_image(src, max_w=165*mm, max_h=105*mm):
    if not src or not src.startswith('data:image'):
        return None
    try:
        raw = base64.b64decode(src.split(',', 1)[1])
        bio = BytesIO(raw)
        img = Image(bio)
        ratio = min(max_w / img.imageWidth, max_h / img.imageHeight, 1)
        img.drawWidth = img.imageWidth * ratio
        img.drawHeight = img.imageHeight * ratio
        return img
    except Exception:
        return None


def build_reba_pdf(e):
    payload = json.loads(e.payload_json or '{}')
    result = json.loads(e.result_json or '{}')
    photos = payload.get('photos', {})
    options = payload.get('options', {})
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=17*mm, leftMargin=17*mm, topMargin=20*mm, bottomMargin=18*mm,
                            title=f'Evaluación REBA #{e.id} - RFRANYUTTI', author='RFRANYUTTI · ErgonometApp')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Brand', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=OLIVE, spaceAfter=3))
    styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=25, leading=29, textColor=DARK, spaceAfter=7))
    styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, textColor=DARK, spaceBefore=8, spaceAfter=8))
    styles.add(ParagraphStyle(name='Small', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=MUTED))
    styles.add(ParagraphStyle(name='Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9))
    story = []

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setStrokeColor(LINE); canvas.line(17*mm, 13*mm, 193*mm, 13*mm)
        canvas.setFont('Helvetica-Bold', 7.5); canvas.setFillColor(OLIVE); canvas.drawString(17*mm, 8.5*mm, 'RFRANYUTTI · ErgonometApp')
        canvas.setFont('Helvetica', 7.5); canvas.setFillColor(MUTED); canvas.drawRightString(193*mm, 8.5*mm, f'Folio REBA-{e.id:05d}  ·  Página {doc_.page}')
        canvas.restoreState()

    story += [Paragraph('RFRANYUTTI', styles['Brand']), Paragraph('Evaluación ergonómica REBA', styles['ReportTitle']),
              Paragraph(f'Expediente técnico · Folio REBA-{e.id:05d}', styles['Small']), Spacer(1, 8*mm)]
    score = e.final_score if e.final_score is not None else '—'
    risk = e.risk_level or 'Sin clasificar'
    hero = Table([[Paragraph('<b>RESULTADO REBA</b>', styles['Center']), Paragraph('<b>NIVEL DE RIESGO</b>', styles['Center'])],
                  [Paragraph(f'<font size="26"><b>{score}</b></font>', styles['Center']), Paragraph(f'<font size="14"><b>{risk}</b></font>', styles['Center'])]], colWidths=[55*mm, 105*mm])
    hero.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),SOFT),('BOX',(0,0),(-1,-1),0.7,LINE),('INNERGRID',(0,0),(-1,-1),0.4,LINE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story += [hero, Spacer(1, 8*mm), Paragraph('Datos de la evaluación', styles['Section'])]
    meta = [['Trabajador', e.trabajador or '—', 'Puesto', e.puesto or '—'], ['Área', e.area or '—', 'Tarea', e.tarea or '—'], ['Evaluador', e.evaluador or '—', 'Fecha', e.fecha or '—']]
    mt = Table(meta, colWidths=[24*mm,56*mm,24*mm,56*mm])
    mt.setStyle(TableStyle([('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8.5),('TEXTCOLOR',(0,0),(-1,-1),DARK),('BACKGROUND',(0,0),(-1,-1),colors.white),('BOX',(0,0),(-1,-1),0.6,LINE),('INNERGRID',(0,0),(-1,-1),0.35,LINE),('VALIGN',(0,0),(-1,-1),'TOP'),('PADDING',(0,0),(-1,-1),6)]))
    story += [mt, Spacer(1, 7*mm), Paragraph('Resumen de puntuaciones', styles['Section'])]
    scores = [['Puntaje A','Puntaje B','Puntaje C','Actividad','REBA final'], [e.score_a or '—',e.score_b or '—',e.score_c or '—',e.activity_score if e.activity_score is not None else '—',score]]
    st = Table(scores, colWidths=[32*mm]*5)
    st.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),DARK),('TEXTCOLOR',(0,0),(-1,0),colors.white),('BACKGROUND',(-1,1),(-1,1),SOFT),('TEXTCOLOR',(-1,1),(-1,1),OLIVE),('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold'),('ALIGN',(0,0),(-1,-1),'CENTER'),('FONTSIZE',(0,0),(-1,0),8),('FONTSIZE',(0,1),(-1,1),16),('BOX',(0,0),(-1,-1),0.6,LINE),('INNERGRID',(0,0),(-1,-1),0.35,LINE),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story += [st, PageBreak(), Paragraph('Análisis postural y evidencia', styles['Section']), Paragraph('Se presentan las mediciones y evidencias almacenadas durante la evaluación.', styles['Small']), Spacer(1, 4*mm)]

    for seg in ['Cuello','Tronco','Piernas','Brazo','Antebrazo','Muñeca','Carga','Acoplamiento','Actividad']:
        block = [Paragraph(seg, styles['Section'])]
        plist = photos.get(seg, []) or []
        if not plist:
            block.append(Paragraph('Sin fotografía asociada a este segmento.', styles['Small']))
        for idx, ph in enumerate(plist, 1):
            img = _data_image(ph.get('src'))
            if img: block += [img, Spacer(1, 2*mm)]
            ms = ph.get('measurements', []) or []
            if ms:
                rows = [['Medición','Ángulo','Dirección']]
                for n,m in enumerate(ms,1): rows.append([str(n), f"{float(m.get('angle',0)):.1f}°", 'Extensión' if m.get('direction')=='extension' else 'Flexión'])
                t=Table(rows,colWidths=[35*mm,45*mm,80*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),SOFT),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('BOX',(0,0),(-1,-1),0.5,LINE),('INNERGRID',(0,0),(-1,-1),0.3,LINE),('PADDING',(0,0),(-1,-1),5)])); block.append(t)
        if options.get(seg): block += [Spacer(1,2*mm), Paragraph(f'<b>Ajustes guardados:</b> {options.get(seg)}', styles['Small'])]
        story += [KeepTogether(block), Spacer(1, 4*mm)]

    story += [PageBreak(), Paragraph('Trazabilidad del cálculo', styles['Section'])]
    trace = result.get('trace', []) or []
    if trace:
        for item in trace: story.append(Paragraph(f'• {item}', styles['Small'])); story.append(Spacer(1,1.5*mm))
    else: story.append(Paragraph('La versión de esta evaluación no almacenó trazabilidad detallada.', styles['Small']))
    story += [Spacer(1,6*mm), Paragraph('Conclusión', styles['Section']), Paragraph(f'La evaluación mediante el método REBA obtuvo una puntuación final de <b>{score}</b>, clasificada como <b>{risk}</b>. Este reporte conserva la información registrada en el expediente digital de ErgonometApp y debe interpretarse junto con las condiciones observadas durante la evaluación.', styles['Normal']), Spacer(1,10*mm), Paragraph('RFRANYUTTI', styles['Brand']), Paragraph('Reporte generado mediante ErgonometApp.', styles['Small'])]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buf.seek(0)
    return buf
