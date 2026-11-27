"""
Módulo de exportación de resúmenes de contratos a informes profesionales Word (.docx).
"""

import os
from typing import Dict, Any
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_cell_background(cell, fill_hex):
    """Aplica color de fondo a una celda de tabla en Word."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Ajusta padding interno de una celda."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def generate_contract_report_docx(analysis_data: Dict[str, Any], output_path: str, contract_name: str = "Contrato") -> str:
    """
    Genera un informe ejecutivo en formato Word (.docx) listo para presentación
    a directores, socios legales o contrapartes.
    """
    doc = docx.Document()
    
    # Configurar márgenes de página (2 cm estándar)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # 1. ENCABEZADO
    header_p = doc.add_paragraph()
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    h_run = header_p.add_run("AGENTE LEGALTECH | CONTRACT LIFECYCLE MANAGEMENT (CLM)")
    h_run.font.size = Pt(8.5)
    h_run.font.bold = True
    h_run.font.color.rgb = RGBColor(120, 144, 156)

    # TÍTULO PRINCIPAL
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(6)
    title_p.paragraph_format.space_after = Pt(4)
    title_run = title_p.add_run("INFORME DE AUDITORÍA CONTRACTUAL Y RESUMEN EJECUTIVO")
    title_run.font.size = Pt(17)
    title_run.font.bold = True
    title_run.font.name = "Calibri"
    title_run.font.color.rgb = RGBColor(24, 43, 73)

    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_after = Pt(14)
    sub_run = subtitle_p.add_run(f"Documento analizado: {contract_name} | Motor: {analysis_data.get('engine_used', 'Agente CLM')}")
    sub_run.font.size = Pt(10)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(90, 105, 120)

    # 2. FICHA TÉCNICA (TABLA)
    doc.add_heading("1. Ficha Técnica del Contrato", level=1)
    ficha = analysis_data.get("ficha_tecnica", {})
    
    table = doc.add_table(rows=6, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    data_ficha = [
        ("Tipo Contractual", ficha.get("tipo_contrato", "No especificado")),
        ("Partes Comparecientes", "\n".join([f"• {p.get('nombre')} ({p.get('rol', '')})" for p in ficha.get("partes", [])]) or "N/D"),
        ("Vigencia y Plazo", ficha.get("vigencia", "N/D")),
        ("Precio / Contraprestación", ficha.get("moneda_monto", "N/D")),
        ("Ley Aplicable", ficha.get("ley_aplicable", "N/D")),
        ("Resolución de Controversias", ficha.get("resolucion_conflictos", "N/D"))
    ]

    for i, (label, val) in enumerate(data_ficha):
        row = table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        
        set_cell_background(c0, "F0F4F8")
        set_cell_margins(c0, top=80, bottom=80, left=100, right=100)
        set_cell_margins(c1, top=80, bottom=80, left=100, right=100)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(label)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = RGBColor(30, 50, 75)
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(str(val))
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 3. RESUMEN EJECUTIVO
    doc.add_heading("2. Resumen Ejecutivo", level=1)
    resumen = analysis_data.get("resumen_ejecutivo", {})
    
    p_prop = doc.add_paragraph()
    r_prop_title = p_prop.add_run("Propósito General: ")
    r_prop_title.bold = True
    p_prop.add_run(resumen.get("proposito_general", ""))

    p_obj = doc.add_paragraph()
    r_obj_title = p_obj.add_run("Objeto Contractual: ")
    r_obj_title.bold = True
    p_obj.add_run(resumen.get("objeto_contractual", ""))

    doc.add_paragraph("Puntos Clave del Acuerdo:", style="List Bullet")
    for pt in resumen.get("puntos_clave", []):
        bp = doc.add_paragraph(pt, style="List Bullet")
        bp.paragraph_format.space_after = Pt(2)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 4. MATRIZ DE RIESGO Y ALERTAS
    doc.add_heading("3. Matriz de Riesgo y Semáforo Contractual", level=1)
    matriz = analysis_data.get("matriz_riesgos", {})
    
    p_risk = doc.add_paragraph()
    r_rlvl = p_risk.add_run(f"Nivel de Riesgo Global: {matriz.get('nivel_riesgo_global', 'MEDIO')} ")
    r_rlvl.bold = True
    r_rlvl.font.size = Pt(11)
    
    score = matriz.get("puntuacion_riesgo", 50)
    p_risk.add_run(f"(Puntuación de Riesgo: {score}/100)\n")
    p_risk.add_run(matriz.get("justificacion_riesgo", ""))

    alertas = matriz.get("alertas", [])
    if alertas:
        doc.add_paragraph("Alertas y Hallazgos Específicos:", style="List Bullet")
        table_alert = doc.add_table(rows=len(alertas) + 1, cols=4)
        table_alert.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        headers = ["Cláusula", "Nivel", "Hallazgo / Riesgo", "Recomendación"]
        col_widths = [Inches(1.5), Inches(0.8), Inches(2.2), Inches(2.2)]
        
        for j, h in enumerate(headers):
            cell = table_alert.rows[0].cells[j]
            cell.width = col_widths[j]
            set_cell_background(cell, "1E3A8A")
            p = cell.paragraphs[0]
            r = p.add_run(h)
            r.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            r.font.size = Pt(9)

        for i, a in enumerate(alertas):
            row = table_alert.rows[i + 1]
            lvl = a.get("nivel", "MEDIO").upper()
            
            # Colores de nivel
            bg = "FFFBEB" if lvl == "MEDIO" else ("FEF2F2" if lvl == "ALTO" else "F0FDF4")
            
            for j, val in enumerate([a.get("clausula", ""), lvl, a.get("hallazgo", ""), a.get("recomendacion", "")]):
                c = row.cells[j]
                c.width = col_widths[j]
                set_cell_background(c, bg)
                set_cell_margins(c, 60, 60, 80, 80)
                p = c.paragraphs[0]
                r = p.add_run(str(val))
                r.font.size = Pt(8.5)
                if j == 1:
                    r.bold = True
                    if lvl == "ALTO":
                        r.font.color.rgb = RGBColor(185, 28, 28)
                    elif lvl == "MEDIO":
                        r.font.color.rgb = RGBColor(180, 83, 9)
                    else:
                        r.font.color.rgb = RGBColor(21, 128, 61)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 5. OBLIGACIONES DE LAS PARTES
    doc.add_heading("4. Obligaciones Principales de las Partes", level=1)
    obligaciones = analysis_data.get("obligaciones_partes", [])
    for grupo in obligaciones:
        doc.add_paragraph(f"Obligaciones de: {grupo.get('parte', 'Parte')}", style="Heading 2")
        for obl in grupo.get("obligaciones", []):
            p = doc.add_paragraph(obl, style="List Bullet")
            p.paragraph_format.space_after = Pt(2)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 6. TÉRMINOS ECONÓMICOS Y PLAZOS
    doc.add_heading("5. Términos Económicos, Plazos y Terminación", level=1)
    term = analysis_data.get("terminos_economicos", {})
    plazos = analysis_data.get("plazos_y_terminacion", {})
    
    pe_p = doc.add_paragraph()
    pe_p.add_run("• Precio / Honorarios: ").bold = True
    pe_p.add_run(f"{term.get('precio_honorarios', 'N/D')}\n")
    pe_p.add_run("• Forma y Condiciones de Pago: ").bold = True
    pe_p.add_run(f"{term.get('forma_pago', 'N/D')}\n")
    pe_p.add_run("• Intereses Moratorios / Penalidades: ").bold = True
    pe_p.add_run(f"{term.get('intereses_mora', 'N/D')}\n")
    pe_p.add_run("• Duración y Prórrogas: ").bold = True
    pe_p.add_run(f"{plazos.get('plazo_duracion', 'N/D')} (Renovación automática: {'SÍ' if plazos.get('renovacion_automatica') else 'NO'})\n")
    pe_p.add_run("• Preaviso de No Renovación: ").bold = True
    pe_p.add_run(f"{plazos.get('preaviso_no_renovacion', 'N/D')}")

    # 7. RECOMENDACIONES DE NEGOCIACIÓN
    recom = analysis_data.get("recomendaciones_negociacion", [])
    if recom:
        doc.add_heading("6. Recomendaciones Estratégicas de Negociación", level=1)
        for r in recom:
            doc.add_paragraph(r, style="List Bullet")

    # Guardar documento
    doc.save(output_path)
    return output_path
