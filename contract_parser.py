"""
Módulo de extracción y preprocesamiento de contratos multiformato.
Soporta: .pdf, .docx, .txt
"""

import os
import re
from typing import Dict, Any, List


def extract_text_from_pdf(file_path: str) -> Dict[str, Any]:
    """Extrae texto de un archivo PDF usando pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_text.append({"page_number": i + 1, "text": text.strip()})
        
        full_text = "\n\n".join([p["text"] for p in pages_text if p["text"]])
        is_scanned = len(full_text.strip()) == 0
        if is_scanned:
            full_text = f"[DOCUMENTO ESCANEADO / IMAGEN DETECTADO - {len(reader.pages)} PÁGINAS]\nEl archivo no contiene texto digital embebido, pero el Agente CLM activará automáticamente su visión multimodal por IA de Google Gemini para auditar las cláusulas, sellos y firmas directamente desde las páginas del PDF."
            
        return {
            "success": True,
            "text": full_text,
            "page_count": len(reader.pages),
            "pages": pages_text,
            "is_scanned": is_scanned,
            "format": "pdf"
        }
    except Exception as e:
        return {"success": False, "error": f"Error al procesar PDF: {str(e)}", "text": "", "page_count": 0}


def extract_text_from_docx(file_path: str) -> Dict[str, Any]:
    """Extrae texto de un archivo Word .docx con soporte para párrafos y tablas."""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs_text = []
        
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs_text.append(text)
        
        # También extraer datos de tablas si existen
        tables_data = []
        for table in doc.tables:
            table_rows = []
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                table_rows.append(" | ".join(cells))
            if table_rows:
                tables_data.append("\n".join(table_rows))
        
        full_parts = paragraphs_text
        if tables_data:
            full_parts.append("\n--- TABLAS ANEXAS ---\n" + "\n\n".join(tables_data))
            
        full_text = "\n\n".join(full_parts)
        
        return {
            "success": True,
            "text": full_text,
            "paragraph_count": len(paragraphs_text),
            "table_count": len(doc.tables),
            "format": "docx"
        }
    except Exception as e:
        return {"success": False, "error": f"Error al procesar DOCX: {str(e)}", "text": ""}


def extract_text_from_txt(file_path: str) -> Dict[str, Any]:
    """Extrae texto de archivos .txt o texto plano en utf-8 o latin-1."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            return {
                "success": True,
                "text": content,
                "format": "txt"
            }
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return {"success": False, "error": str(e), "text": ""}
    return {"success": False, "error": "No se pudo decodificar el archivo de texto.", "text": ""}


def parse_contract_file(file_path: str) -> Dict[str, Any]:
    """
    Punto de entrada principal para procesar cualquier contrato soportado.
    Retorna texto limpio, metadatos y desglose preliminar de cláusulas.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        result = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        result = extract_text_from_docx(file_path)
    elif ext in [".txt", ".md"]:
        result = extract_text_from_txt(file_path)
    else:
        return {"success": False, "error": f"Formato no soportado: {ext}"}
    
    if not result.get("success"):
        return result
    
    text = result.get("text", "").strip()
    
    if result.get("is_scanned"):
        result.update({
            "word_count": 0,
            "char_count": len(text),
            "paragraph_count": result.get("page_count", 1),
            "estimated_read_time_min": round(result.get("page_count", 1) * 1.5, 1),
            "detected_clause_count": 0,
            "sample_clauses": ["Documento escaneado (análisis visual vía IA activado)"]
        })
        return result

    if not text:
        return {"success": False, "error": "El documento no contiene texto legible."}

    # Metadatos del documento
    words = len(text.split())
    chars = len(text)
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    estimated_read_time_min = round(words / 200, 1)

    # Detección de títulos de cláusulas típicas (ej. PRIMERA, CLÁUSULA 1, OBJETO, etc.)
    clause_pattern = re.compile(
        r'(?:^|\n)\s*(CL[AÁ]USULA\s+[A-Z0-9IVXLCDM\.-]+|[A-Z0-9IVXLCDM]+[\.\-]\s*|\b(?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[EÉ]PTIMA|OCTAVA|NOVENA|D[EÉ]CIMA|UND[EÉ]CIMA|DUOD[EÉ]CIMA|D[EÉ]CIMO\s+[A-Z]+)\b[^\n:]*[:\.-]?)(?=\s|\n)',
        re.IGNORECASE
    )
    detected_clauses = [m.group(0).strip() for m in clause_pattern.finditer(text)]

    result.update({
        "word_count": words,
        "char_count": chars,
        "paragraph_count": len(paragraphs),
        "estimated_read_time_min": estimated_read_time_min,
        "detected_clause_count": len(detected_clauses),
        "sample_clauses": detected_clauses[:15]
    })
    
    return result
