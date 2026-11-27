"""
Servidor Web Flask del Agente LegalTech CLM.
Gestión del ciclo de vida contractual, resúmenes inteligentes,
matriz de riesgos y chat interactivo con el contrato.
"""

import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar variables de entorno desde .env explícito
load_dotenv(os.path.join(BASE_DIR, ".env"))

from contract_parser import parse_contract_file
from clm_agent import CLMAgent
from contract_exporter import generate_contract_report_docx

app = Flask(__name__)
app.config["SECRET_KEY"] = "clm-legaltech-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
SAMPLES_FOLDER = os.path.join(BASE_DIR, "ejemplos_contratos")

for folder in [UPLOAD_FOLDER, REPORTS_FOLDER, SAMPLES_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Memoria de sesiones activas (análisis recientes)
ACTIVE_ANALYSES = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config", methods=["GET", "POST"])
def manage_config():
    """Consulta o actualiza la configuración de la clave de IA en el servidor."""
    env_path = os.path.join(BASE_DIR, ".env")
    
    if request.method == "POST":
        data = request.get_json() or {}
        api_key = data.get("api_key", "").strip()
        provider = data.get("provider", "gemini").strip().lower()
        
        # Guardar en .env
        env_content = f"GEMINI_API_KEY={api_key if provider == 'gemini' else ''}\n"
        env_content += f"OPENAI_API_KEY={api_key if provider == 'openai' else ''}\n"
        env_content += f"AI_PROVIDER={provider}\n"
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
            
        os.environ["GEMINI_API_KEY"] = api_key if provider == "gemini" else ""
        os.environ["OPENAI_API_KEY"] = api_key if provider == "openai" else ""
        os.environ["AI_PROVIDER"] = provider
        
        return jsonify({"success": True, "message": "Clave API guardada exitosamente en el servidor (.env)"})

    # GET
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    provider = os.getenv("AI_PROVIDER", "gemini")
    
    active_key = gemini_key if provider == "gemini" else openai_key
    has_key = bool(active_key and len(active_key.strip()) > 8)
    masked_key = (active_key[:6] + "..." + active_key[-4:]) if has_key else ""
    
    return jsonify({
        "success": True,
        "has_server_key": has_key,
        "provider": provider,
        "masked_key": masked_key
    })


@app.route("/api/samples", methods=["GET"])
def get_samples():
    """Lista los contratos de ejemplo predefinidos."""
    samples = []
    if os.path.exists(SAMPLES_FOLDER):
        for f in sorted(os.listdir(SAMPLES_FOLDER)):
            if f.endswith((".docx", ".txt", ".pdf")):
                samples.append({
                    "filename": f,
                    "title": f.replace("_", " ").replace(".docx", "").replace(".txt", "").replace(".pdf", ""),
                    "format": f.split(".")[-1].upper()
                })
    return jsonify({"success": True, "samples": samples})


@app.route("/api/load-sample", methods=["POST"])
def load_sample():
    """Carga un contrato de ejemplo para análisis instantáneo."""
    data = request.get_json() or {}
    filename = data.get("filename")
    if not filename:
        return jsonify({"success": False, "error": "Nombre de archivo no especificado"}), 400
        
    path = os.path.join(SAMPLES_FOLDER, secure_filename(filename))
    if not os.path.exists(path):
        return jsonify({"success": False, "error": "Archivo no encontrado"}), 404
        
    parsed = parse_contract_file(path)
    if not parsed.get("success"):
        return jsonify(parsed), 400
        
    return jsonify({
        "success": True,
        "filename": filename,
        "text": parsed.get("text", ""),
        "metadata": {
            "format": parsed.get("format"),
            "word_count": parsed.get("word_count"),
            "char_count": parsed.get("char_count"),
            "paragraph_count": parsed.get("paragraph_count"),
            "estimated_read_time_min": parsed.get("estimated_read_time_min"),
            "detected_clause_count": parsed.get("detected_clause_count")
        }
    })


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Recibe un archivo contractual (.docx, .pdf, .txt) y extrae su contenido."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No se subió ningún archivo"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Nombre de archivo vacío"}), 400
        
    orig_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex[:8]}_{orig_name}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)
    
    parsed = parse_contract_file(save_path)
    if not parsed.get("success"):
        return jsonify(parsed), 400
        
    return jsonify({
        "success": True,
        "filename": orig_name,
        "saved_path": save_path,
        "text": parsed.get("text", ""),
        "metadata": {
            "format": parsed.get("format"),
            "word_count": parsed.get("word_count"),
            "char_count": parsed.get("char_count"),
            "paragraph_count": parsed.get("paragraph_count"),
            "estimated_read_time_min": parsed.get("estimated_read_time_min"),
            "detected_clause_count": parsed.get("detected_clause_count")
        }
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Ejecuta el análisis inteligente CLM del contrato."""
    data = request.get_json() or {}
    text = data.get("text", "")
    filename = data.get("filename", "Contrato")
    saved_path = data.get("saved_path")
    api_key = data.get("api_key", "").strip()
    provider = data.get("provider", "gemini")
    
    if not text.strip():
        return jsonify({"success": False, "error": "El texto del contrato está vacío"}), 400
        
    agent = CLMAgent(api_key=api_key, provider=provider)
    analysis = agent.analyze_contract(contract_text=text, file_name=filename, pdf_path=saved_path)
    
    # Generar ID de sesión para Q&A y exportación
    session_id = uuid.uuid4().hex
    ACTIVE_ANALYSES[session_id] = {
        "filename": filename,
        "text": text,
        "saved_path": saved_path,
        "analysis": analysis,
        "api_key": api_key,
        "provider": provider
    }
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "analysis": analysis
    })


@app.route("/api/ask", methods=["POST"])
def ask():
    """Responde consultas interactivas sobre el contrato (Chat con el Contrato)."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    question = data.get("question", "").strip()
    api_key = data.get("api_key", "").strip()
    
    if not question:
        return jsonify({"success": False, "error": "Pregunta vacía"}), 400
        
    cached = ACTIVE_ANALYSES.get(session_id)
    if not cached:
        text = data.get("text", "")
        analysis = data.get("analysis", {})
        saved_path = data.get("saved_path")
        provider = data.get("provider", "gemini")
    else:
        text = cached["text"]
        analysis = cached["analysis"]
        saved_path = cached.get("saved_path")
        api_key = api_key or cached.get("api_key")
        provider = cached.get("provider", "gemini")
        
    agent = CLMAgent(api_key=api_key, provider=provider)
    answer = agent.answer_question(question=question, contract_text=text, analysis_data=analysis, pdf_path=saved_path)
    
    return jsonify({
        "success": True,
        "answer": answer
    })
    
    return jsonify({
        "success": True,
        "answer": answer
    })


@app.route("/api/export-docx", methods=["POST"])
def export_docx():
    """Genera y descarga el informe legal en Word (.docx)."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    
    if session_id and session_id in ACTIVE_ANALYSES:
        analysis = ACTIVE_ANALYSES[session_id]["analysis"]
        filename = ACTIVE_ANALYSES[session_id]["filename"]
    else:
        analysis = data.get("analysis")
        filename = data.get("filename", "Contrato")
        
    if not analysis:
        return jsonify({"success": False, "error": "No hay datos de análisis para exportar"}), 400
        
    report_filename = f"Informe_CLM_{secure_filename(filename).replace('.', '_')}.docx"
    output_path = os.path.join(REPORTS_FOLDER, report_filename)
    
    generate_contract_report_docx(analysis_data=analysis, output_path=output_path, contract_name=filename)
    
    return send_file(output_path, as_attachment=True, download_name=report_filename)


@app.route("/api/export-json", methods=["POST"])
def export_json():
    """Exporta los datos estructurados en formato JSON para integraciones."""
    data = request.get_json() or {}
    analysis = data.get("analysis")
    filename = data.get("filename", "contrato")
    
    if not analysis:
        return jsonify({"success": False, "error": "Sin datos"}), 400
        
    json_path = os.path.join(REPORTS_FOLDER, f"analisis_{secure_filename(filename)}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
        
    return send_file(json_path, as_attachment=True, download_name=f"analisis_{secure_filename(filename)}.json")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("⚖️  AGENTE LEGALTECH - CONTRACT LIFECYCLE MANAGEMENT (CLM)")
    print("🚀  Servidor web iniciado exitosamente en: http://localhost:5005")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5005, debug=True)
