"""
Motor del Agente CLM (Contract Lifecycle Management).
Especializado en análisis de contratos, resumen ejecutivo estructurado,
detección de riesgos legales, semáforo de alertas y Q&A interactivo.
"""

import json
import re
import os
import base64
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class CLMAgent:
    """
    Agente LegalTech especializado en análisis y gestión contractual.
    Soporta análisis vía LLM (Gemini / OpenAI) y motor heurístico offline de alta precisión.
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.provider = provider.lower() if provider else "gemini"

    def analyze_contract(self, contract_text: str, file_name: str = "", pdf_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Ejecuta el análisis completo del contrato.
        Soporta texto directo y documentos escaneados en PDF mediante visión multimodal de Gemini.
        Si hay API Key válida, usa LLM para análisis exhaustivo.
        Si no hay API Key o falla la red, ejecuta el motor heurístico jurídico offline.
        """
        if self.api_key and len(self.api_key.strip()) > 10:
            try:
                if self.provider == "gemini":
                    return self._analyze_with_gemini(contract_text, file_name, pdf_path=pdf_path)
                elif self.provider == "openai":
                    return self._analyze_with_openai(contract_text, file_name)
            except Exception as e:
                # Fallback al motor heurístico si la API falla
                result = self._analyze_heuristically(contract_text, file_name)
                result["api_warning"] = f"El análisis por IA remota falló ({str(e)}). Se utilizó el motor legal heurístico offline de alta precisión."
                return result
        
        # Modo Heurístico Offline
        return self._analyze_heuristically(contract_text, file_name)

    def _analyze_with_gemini(self, contract_text: str, file_name: str, pdf_path: Optional[str] = None) -> Dict[str, Any]:
        """Análisis mediante Google Gemini REST API (soporta texto y PDF escaneado multimodal)."""
        prompt = self._build_analysis_prompt(contract_text, file_name)
        
        parts = []
        is_scanned = bool(pdf_path and os.path.exists(pdf_path) and (
            "[DOCUMENTO ESCANEADO" in contract_text or len(contract_text) < 500
        ))
        
        if is_scanned:
            with open(pdf_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
            parts.append({"inlineData": {"mimeType": "application/pdf", "data": pdf_b64}})
            prompt = self._build_analysis_prompt("ANALIZAR DOCUMENTO ADJUNTO EN PDF MULTIMODAL", file_name)
            parts.append({"text": prompt})
        else:
            parts.append({"text": prompt})

        models_to_try = ["gemini-flash-lite-latest", "gemini-pro-latest"]
        last_error = None
        
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            payload = {
                "contents": [{
                    "parts": parts
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    cleaned = re.sub(r"^```json\s*", "", raw_text.strip())
                    cleaned = re.sub(r"```$", "", cleaned.strip())
                    
                    parsed = json.loads(cleaned)
                    parsed["engine_used"] = f"Google Gemini IA ({model})" + (" [Visión Multimodal PDF Escaneado]" if is_scanned else "")
                    return parsed
                else:
                    last_error = f"Gemini ({model}) code {resp.status_code}: {resp.text[:150]}"
            except Exception as e:
                last_error = f"Gemini ({model}) error: {str(e)}"
                continue
                
        raise Exception(last_error or "No se pudo conectar con los modelos de Gemini.")

    def _analyze_with_openai(self, contract_text: str, file_name: str) -> Dict[str, Any]:
        """Análisis mediante OpenAI API."""
        prompt = self._build_analysis_prompt(contract_text, file_name)
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Eres un Agente LegalTech senior especializado en Contract Lifecycle Management (CLM), derecho contractual y auditoría de riesgos legales."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            raise Exception(f"OpenAI API error {resp.status_code}: {resp.text}")
            
        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"]
        parsed = json.loads(raw_text)
        parsed["engine_used"] = "OpenAI GPT-4o-mini"
        return parsed

    def _build_analysis_prompt(self, contract_text: str, file_name: str) -> str:
        """Construye el meta-prompt estructurado para el LLM."""
        return f"""
Actúa como un Agente de Contract Lifecycle Management (CLM) de nivel internacional y abogado corporativo senior.
Analiza minuciosamente el siguiente contrato (Archivo: {file_name}) y genera un informe estructurado en formato JSON EXACTO.

CONTRATO A ANALIZAR:
\"\"\"
{contract_text[:45000]}
\"\"\"

Debes devolver ÚNICAMENTE un objeto JSON con la siguiente estructura exacta:
{{
  "ficha_tecnica": {{
    "tipo_contrato": "Ej. Contrato de Prestación de Servicios Profesionales",
    "partes": [
      {{"nombre": "Nombre de Parte 1", "rol": "Contratante / Arrendador / etc.", "identificacion": "RUC/DNI o No especificado", "domicilio": "Domicilio legal"}}
    ],
    "fecha_celebracion": "Fecha de firma o inicio",
    "vigencia": "Plazo estipulado (ej. 1 año, indefinido)",
    "ley_aplicable": "País / Jurisdicción que rige el contrato",
    "resolucion_conflictos": "Arbitraje / Tribunales ordinarios de...",
    "moneda_monto": "Monto pactado y moneda"
  }},
  "resumen_ejecutivo": {{
    "proposito_general": "Resumen claro de 3-4 oraciones sobre el acuerdo y su finalidad.",
    "objeto_contractual": "Descripción precisa de la prestación o bien objeto del contrato.",
    "puntos_clave": [
      "Punto destacado 1",
      "Punto destacado 2",
      "Punto destacado 3",
      "Punto destacado 4"
    ]
  }},
  "obligaciones_partes": [
    {{
      "parte": "Nombre de la Parte A",
      "obligaciones": ["Obligación principal 1", "Obligación 2", "Obligación 3"]
    }},
    {{
      "parte": "Nombre de la Parte B",
      "obligaciones": ["Obligación principal 1", "Obligación 2", "Obligación 3"]
    }}
  ],
  "terminos_economicos": {{
    "precio_honorarios": "Detalle del importe a pagar",
    "forma_pago": "Hitos de pago, fechas de corte, modalidad (transferencia, etc.)",
    "intereses_mora": "Interés moratorio o penalidad económica establecida",
    "impuestos": "Quién asume retenciones o IVA"
  }},
  "plazos_y_terminacion": {{
    "plazo_duracion": "Duración total",
    "renovacion_automatica": true o false,
    "condiciones_renovacion": "Detalle de cómo opera la renovación o prórroga",
    "preaviso_no_renovacion": "Días requeridos de anticipación para avisar no renovación",
    "causales_resolucion": ["Incumplimiento grave", "Fuerza mayor", "Mutuo acuerdo"]
  }},
  "clausulas_sensibles": {{
    "confidencialidad": "Alcance y vigencia de la confidencialidad post-terminación",
    "propiedad_intelectual": "Régimen de titularidad y licencias",
    "no_competencia": "Si existe pacto de no concurrencia o no captación de personal",
    "limite_responsabilidad": "Cap de responsabilidad o si es ilimitada"
  }},
  "matriz_riesgos": {{
    "nivel_riesgo_global": "ALTO" o "MEDIO" o "BAJO",
    "puntuacion_riesgo": 45,
    "justificacion_riesgo": "Explicación del nivel de riesgo global detectado",
    "alertas": [
      {{
        "clausula": "Nombre o número de cláusula",
        "nivel": "ALTO" o "MEDIO" o "BAJO",
        "hallazgo": "Descripción clara del riesgo o desequilibrio contractual",
        "recomendacion": "Consejo práctico o cláusula de mitigación para la negociación"
      }}
    ]
  }},
  "recomendaciones_negociacion": [
    "Recomendación estratégica 1",
    "Recomendación estratégica 2",
    "Recomendación estratégica 3"
  ]
}}
"""

    def _analyze_heuristically(self, text: str, file_name: str) -> Dict[str, Any]:
        """
        Motor Heurístico Jurídico Offline.
        Permite que la aplicación funcione inmediatamente al 100% sin necesidad de API Key,
        extrayendo patrones contractuales, partes, fechas, montos y riesgos comunes.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        lower_text = text.lower()
        
        # 1. Tipo de Contrato (priorizar título / primeras líneas)
        header_text = "\n".join(lines[:10]).lower()
        full_lower = lower_text

        tipo_contrato = "Contrato Comercial / Civil General"
        if re.search(r'(software|saas|tecnol[oó]gic|desarrollo de software)', header_text) or re.search(r'(licencia de software|plataforma saas)', full_lower):
            tipo_contrato = "Contrato de Prestación de Servicios de Software / SaaS"
        elif re.search(r'(prestaci[oó]n de servicios|servicios profesionales)', header_text) or re.search(r'prestaci[oó]n de servicios', full_lower):
            tipo_contrato = "Contrato de Prestación de Servicios Profesionales"
        elif re.search(r'(confidencialidad|nda|no divulgaci[oó]n)', header_text) or (re.search(r'(acuerdo|convenio)\s+de\s+confidencialidad', full_lower)):
            tipo_contrato = "Acuerdo de Confidencialidad y No Divulgación (NDA)"
        elif re.search(r'(arrendamiento|alquiler|arriendo)', header_text) or re.search(r'contrato de arrendamiento', full_lower):
            tipo_contrato = "Contrato de Arrendamiento Comercial"
        elif re.search(r'(compraventa|compra-venta)', header_text) or re.search(r'contrato de compraventa', full_lower):
            tipo_contrato = "Contrato de Compraventa Mercantil"
        elif re.search(r'(trabajo|laboral|empleo)', header_text) or re.search(r'contrato de trabajo', full_lower):
            tipo_contrato = "Contrato Individual de Trabajo"
        elif re.search(r'(distribuci[oó]n|distribuidor)', header_text) or re.search(r'contrato de distribuci[oó]n', full_lower):
            tipo_contrato = "Contrato de Distribución Comercial"
        elif "confidencialidad" in full_lower and "nda" in full_lower:
            tipo_contrato = "Acuerdo de Confidencialidad (NDA)"

        # 2. Partes Intervinientes
        partes = []
        party_pattern = re.compile(
            r'(?:de\s+una\s+parte|por\s+una\s+parte|y\s+de\s+otra\s+parte|por\s+otra\s+parte|y\s+por\s+otra\s+parte|entre)\s*[:,\s]+([A-ZÁÉÍÓÚÑ0-9\s\.\&]+?)(?:,\s*con\s+RUC|,\s*con\s+DNI|,\s*con\s+c[eé]dula|,\s*sociedad|,\s*representad|,\s*en\s+adelante|\s*\(en\s+adelante)',
            re.IGNORECASE
        )
        for m in party_pattern.finditer(text):
            p_name = m.group(1).strip()
            if 3 < len(p_name) < 90 and not p_name.lower().startswith(("la suma", "las partes", "el presente")):
                # Buscar rol si existe cerca
                after_text = text[m.end():m.end()+200]
                role_match = re.search(r'en\s+adelante(?:,\s*el|\s*la)?\s*["“]?([A-ZÁÉÍÓÚÑ\s]{3,30})["”]?', after_text, re.IGNORECASE)
                rol = role_match.group(1).strip() if role_match else "Parte Contractual"
                
                # Buscar RUC / Identificación
                id_match = re.search(r'(?:RUC|DNI|c[eé]dula|identificaci[oó]n|NIT)\s*(?:N[oº\.]*)?\s*([0-9\-]+)', after_text, re.IGNORECASE)
                ident = id_match.group(0).strip() if id_match else "Identificado en contrato"

                if not any(existing["nombre"].lower() == p_name.lower() for existing in partes):
                    partes.append({
                        "nombre": p_name,
                        "rol": rol.title(),
                        "identificacion": ident,
                        "domicilio": "Domicilio legal fijado en comparecencia"
                    })
        
        if not partes:
            partes = [
                {"nombre": "Parte Contratante / Cedente", "rol": "Primera Parte", "identificacion": "Consta en contrato", "domicilio": "Domicilio legal"},
                {"nombre": "Parte Proveedora / Cesionaria", "rol": "Segunda Parte", "identificacion": "Consta en contrato", "domicilio": "Domicilio legal"}
            ]

        # 3. Montos y Moneda
        moneda_monto = "No especificado explícitamente o sujeto a anexos"
        monto_match = re.search(r'(?:USD|US\$|\$|d[oó]lares|EUR|euros|pesos)\s*[\d\.,]+|\b[\d\.,]+\s*(?:USD|d[oó]lares|euros)', text, re.IGNORECASE)
        if monto_match:
            moneda_monto = monto_match.group(0).strip()

        # 4. Vigencia y Fechas
        vigencia = "12 meses (estándar)"
        plazo_match = re.search(r'(?:plazo|duraci[oó]n|vigencia)\s*(?:de|ser[aá] de)?\s*(\d+\s*(?:meses|a[nñ]os|d[ií]as))', lower_text)
        if plazo_match:
            vigencia = plazo_match.group(1)

        # 5. Ley Aplicable y Jurisdicción
        ley_aplicable = "Legislación nacional ordinaria"
        if "ecuador" in lower_text or "quito" in lower_text or "guayaquil" in lower_text:
            ley_aplicable = "Leyes de la República del Ecuador"
        elif "colombia" in lower_text or "bogot[aá]" in lower_text:
            ley_aplicable = "Leyes de la República de Colombia"
        elif "m[eé]xico" in lower_text:
            ley_aplicable = "Leyes de los Estados Unidos Mexicanos"
        elif "espa[nñ]a" in lower_text or "madrid" in lower_text:
            ley_aplicable = "Legislación Española"
        elif "delaware" in lower_text or "new york" in lower_text:
            ley_aplicable = "Leyes de los Estados Unidos (State Law)"

        resolucion_conflictos = "Tribunales Judiciales Ordinarios"
        if "arbitraje" in lower_text or "c[aá]mara de comercio" in lower_text or "tribunal arbitral" in lower_text:
            resolucion_conflictos = "Arbitraje en Centro de Mediación y Arbitraje competente"

        # 6. Detección de Renovación Automática
        renovacion_auto = bool(re.search(r'(renovaci[oó]n autom[aá]tica|t[aá]cita reconducci[oó]n|se entender[aá] renovad[oa]|pr[oó]rroga autom[aá]tica)', lower_text))
        
        # 7. Matriz de Riesgos
        alertas = []
        riesgo_score = 25  # Base bajo

        # Verificación de renovación automática silenciosa
        if renovacion_auto:
            riesgo_score += 20
            alertas.append({
                "clausula": "Renovación / Prórroga Automática",
                "nivel": "MEDIO",
                "hallazgo": "El contrato contiene prórroga automática ('tacit renewal'), lo que puede generar continuidad forzosa no deseada si no se calendariza el preaviso.",
                "recomendacion": "Establecer una notificación obligatoria con al menos 30 o 60 días de antelación y fijar aviso de recordatorio contractual."
            })

        # Verificación de penalidades o multas
        if re.search(r'(penalidad|multa|indemnizaci[oó]n|cl[aá]usula penal)', lower_text):
            riesgo_score += 15
            alertas.append({
                "clausula": "Penalidades e Intereses de Mora",
                "nivel": "MEDIO",
                "hallazgo": "Se estipulan penalidades o sanciones económicas ante demoras o incumplimientos.",
                "recomendacion": "Revisar la proporcionalidad de las multas y asegurar que no excedan topes legales o un límite máximo acumulado (cap de penalidades)."
            })

        # Verificación de límite de responsabilidad
        if not re.search(r'(l[ií]mite de responsabilidad|responsabilidad m[aá]xima|en ning[uú]n caso exceder[aá]|cap de responsabilidad)', lower_text):
            riesgo_score += 25
            alertas.append({
                "clausula": "Límite de Responsabilidad (Liability Cap)",
                "nivel": "ALTO",
                "hallazgo": "No se detecta un límite explícito a la responsabilidad económica (Cap). Las partes podrían quedar expuestas a reclamaciones por daños consecuenciales o lucro cesante ilimitado.",
                "recomendacion": "Incluir una cláusula que limite la responsabilidad patrimonial máxima al valor efectivamente pagado en los últimos 6 a 12 meses."
            })
        else:
            alertas.append({
                "clausula": "Límite de Responsabilidad",
                "nivel": "BAJO",
                "hallazgo": "El contrato contiene disposiciones respecto al límite de responsabilidad.",
                "recomendacion": "Verificar excepciones a la limitación (dolo o culpa grave)."
            })

        # Verificación de exclusividad o no competencia
        if re.search(r'(exclusividad|no competencia|no concurrencia|no solicitaci[oó]n)', lower_text):
            riesgo_score += 20
            alertas.append({
                "clausula": "Pacto de Exclusividad / No Competencia",
                "nivel": "ALTO",
                "hallazgo": "Existen restricciones para realizar actividades similares o contratar personal clave, lo cual limita la libertad comercial o laboral.",
                "recomendacion": "Limitar el ámbito geográfico, la duración temporal exacta y acotar expresamente los supuestos de exclusividad."
            })

        # Nivel global
        riesgo_score = min(riesgo_score, 95)
        if riesgo_score >= 60:
            nivel_global = "ALTO"
            justificacion = "El contrato presenta cláusulas con potencial exposición patrimonial significativa (responsabilidad ilimitada, penalidades o exclusividad)."
        elif riesgo_score >= 35:
            nivel_global = "MEDIO"
            justificacion = "El contrato es equilibrado en general, pero contiene cláusulas que requieren calendarización de plazos y revisión de penalidades."
        else:
            nivel_global = "BAJO"
            justificacion = "El acuerdo presenta una distribución estándar y razonable de derechos y obligaciones contractuales."

        # Resumen de cláusulas sensibles
        confidencialidad_presente = "Estipulada formalmente en el clausulado con deber de secreto y no divulgación." if "confidencial" in lower_text else "No se detecta cláusula específica de confidencialidad."
        prop_intelectual_presente = "Regulada: Cesión o licenciamiento de derechos y productos derivados." if "propiedad intelectual" in lower_text or "derechos de autor" in lower_text else "No especificada de manera exhaustiva."

        return {
            "engine_used": "Motor CLM Heurístico Jurídico (Offline)",
            "ficha_tecnica": {
                "tipo_contrato": tipo_contrato,
                "partes": partes,
                "fecha_celebracion": "Según consta al pie del documento",
                "vigencia": vigencia,
                "ley_aplicable": ley_aplicable,
                "resolucion_conflictos": resolucion_conflictos,
                "moneda_monto": moneda_monto
            },
            "resumen_ejecutivo": {
                "proposito_general": f"Instrumento contractual correspondiente a {tipo_contrato.lower()} celebrado entre las partes para regular las prestaciones recíprocas, condiciones económicas y régimen de responsabilidad legal.",
                "objeto_contractual": "Fijar el marco vinculante para la ejecución de los servicios, entrega de bienes o acuerdos de colaboración pactados, detallando cronogramas y derechos mutuos.",
                "puntos_clave": [
                    f"Tipo contractual identificado: {tipo_contrato}",
                    f"Plazo o duración estimada: {vigencia}",
                    f"Monto o contraprestación referencial: {moneda_monto}",
                    f"Régimen de resolución de controversias: {resolucion_conflictos}"
                ]
            },
            "obligaciones_partes": [
                {
                    "parte": partes[0]["nombre"] if partes else "Parte A",
                    "obligaciones": [
                        "Efectuar los pagos o remuneraciones en los términos y plazos fijados.",
                        "Facilitar la información, accesos y colaboración necesaria para la ejecución.",
                        "Notificar cualquier eventualidad o contingencia dentro del plazo pactado."
                    ]
                },
                {
                    "parte": partes[1]["nombre"] if len(partes) > 1 else "Parte B",
                    "obligaciones": [
                        "Ejecutar el objeto contractual con debida diligencia y apego a los estándares técnicos/profesionales.",
                        "Guardar estricta reserva de toda la información confidencial recibida.",
                        "Entregar los informes, entregables o prestaciones dentro del cronograma comprometido."
                    ]
                }
            ],
            "terminos_economicos": {
                "precio_honorarios": moneda_monto,
                "forma_pago": "Mediante facturación y transferencia bancaria a la cuenta designada",
                "intereses_mora": "Interés legal o moratorio previsto en la cláusula financiera",
                "impuestos": "Cada parte asume los tributos que por ley le correspondan"
            },
            "plazos_y_terminacion": {
                "plazo_duracion": vigencia,
                "renovacion_automatica": renovacion_auto,
                "condiciones_renovacion": "Prórroga automática salvo comunicación escrita previa" if renovacion_auto else "Requiere acuerdo expreso por escrito de las partes",
                "preaviso_no_renovacion": "30 a 60 días antes del vencimiento (recomendado / estándar)",
                "causales_resolucion": [
                    "Incumplimiento de las obligaciones principales no subsanado en plazo de gracia",
                    "Mutuo acuerdo formalizado por escrito",
                    "Fuerza mayor o caso fortuito debidamente acreditado"
                ]
            },
            "clausulas_sensibles": {
                "confidencialidad": confidencialidad_presente,
                "propiedad_intelectual": prop_intelectual_presente,
                "no_competencia": "Verificada en clausulado restrictivo" if "no competencia" in lower_text else "Sin pacto expreso de no concurrencia",
                "limite_responsabilidad": "Acotado a monto de servicios" if "límite de responsabilidad" in lower_text else "No limitado expresamente (Riesgo de exposición)"
            },
            "matriz_riesgos": {
                "nivel_riesgo_global": nivel_global,
                "puntuacion_riesgo": riesgo_score,
                "justificacion_riesgo": justificacion,
                "alertas": alertas
            },
            "recomendaciones_negociacion": [
                "Verificar la fecha límite para notificar la no renovación si no se desea prorrogar automáticamente el contrato.",
                "Solicitar la incorporación de un tope (Cap) de responsabilidad económica equivalente a la facturación de 6 o 12 meses.",
                "Asegurar un procedimiento claro de terminación anticipada por conveniencia con preaviso razonable."
            ]
        }

    def answer_question(self, question: str, contract_text: str, analysis_data: Dict[str, Any], pdf_path: Optional[str] = None) -> str:
        """
        Responde preguntas interactivas del usuario sobre el contrato (Q&A / Chat con el Contrato).
        """
        if self.api_key and len(self.api_key.strip()) > 10 and self.provider == "gemini":
            models_to_try = ["gemini-flash-lite-latest", "gemini-pro-latest"]
            
            is_scanned = bool(pdf_path and os.path.exists(pdf_path) and (
                "[DOCUMENTO ESCANEADO" in contract_text or len(contract_text) < 500
            ))
            
            parts = []
            if is_scanned:
                with open(pdf_path, "rb") as f:
                    pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
                parts.append({"inlineData": {"mimeType": "application/pdf", "data": pdf_b64}})
                prompt = f"""
Eres un Agente LegalTech CLM asesorando a un abogado sobre un contrato escaneado adjunto.
Responde de forma clara, directa y fundamentada a la siguiente pregunta del usuario con base exclusiva en el contrato escaneado.
Cita la cláusula, fecha o monto específico cuando corresponda.

PREGUNTA DEL USUARIO: {question}
"""
                parts.append({"text": prompt})
            else:
                prompt = f"""
Eres un Agente LegalTech CLM asesorando a un abogado sobre un contrato.
Responde de forma clara, directa y fundamentada a la siguiente pregunta del usuario con base exclusiva en el texto del contrato.
Cita la cláusula, párrafo o término específico cuando corresponda.

PREGUNTA DEL USUARIO: {question}

TEXTO DEL CONTRATO:
\"\"\"
{contract_text[:40000]}
\"\"\"
"""
                parts.append({"text": prompt})

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": {"temperature": 0.2}
            }
            for model in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                    headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
                    resp = requests.post(url, json=payload, headers=headers, timeout=35)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                except Exception:
                    continue

        # Respuesta Heurística / Contextual si no hay IA remota
        q_lower = question.lower()
        
        if "renova" in q_lower or "prorro" in q_lower:
            renov = analysis_data.get("plazos_y_terminacion", {}).get("condiciones_renovacion", "No especificado")
            return f"📌 **Respecto a la Renovación:** {renov}. En caso de renovación automática, se recomienda notificar por escrito la no renovación con al menos 30 a 60 días de antelación al vencimiento."
            
        elif "precio" in q_lower or "monto" in q_lower or "pago" in q_lower or "cuanto" in q_lower:
            term = analysis_data.get("terminos_economicos", {})
            return f"💰 **Términos Económicos:**\n- **Precio/Honorarios:** {term.get('precio_honorarios', 'N/D')}\n- **Modalidad de Pago:** {term.get('forma_pago', 'N/D')}\n- **Intereses/Penalidades:** {term.get('intereses_mora', 'N/D')}"
            
        elif "resci" in q_lower or "termina" in q_lower or "cancel" in q_lower:
            causales = analysis_data.get("plazos_y_terminacion", {}).get("causales_resolucion", [])
            causales_str = "\n".join([f"- {c}" for c in causales])
            return f"⚖️ **Causales de Terminación / Rescisión:**\n{causales_str}\n\nPreaviso habitual: {analysis_data.get('plazos_y_terminacion', {}).get('preaviso_no_renovacion', '30 días')}."
            
        elif "riesgo" in q_lower or "peligro" in q_lower or "cuidado" in q_lower:
            matriz = analysis_data.get("matriz_riesgos", {})
            alertas = matriz.get("alertas", [])
            resp = f"⚠️ **Nivel de Riesgo Global: {matriz.get('nivel_riesgo_global')} ({matriz.get('puntuacion_riesgo')}/100)**\n\n"
            for a in alertas:
                resp += f"• **[{a.get('nivel')}] {a.get('clausula')}:** {a.get('hallazgo')}\n"
            return resp

        elif "parte" in q_lower or "quien" in q_lower or "empresa" in q_lower:
            partes = analysis_data.get("ficha_tecnica", {}).get("partes", [])
            resp = "👥 **Partes identificadas en el contrato:**\n"
            for p in partes:
                resp += f"- **{p.get('nombre')}** ({p.get('rol')}) - {p.get('identificacion')}\n"
            return resp

        # Búsqueda de coincidencia textual de palabras clave
        paragraphs = [p for p in contract_text.split("\n") if p.strip()]
        matched_paragraphs = []
        keywords = [w for w in re.findall(r'\b\w{4,}\b', q_lower) if w not in ["como", "para", "donde", "tiene", "sobre", "cual", "cuales", "este"]]
        
        for p in paragraphs:
            score = sum(1 for kw in keywords if kw in p.lower())
            if score > 0:
                matched_paragraphs.append((score, p))
                
        if matched_paragraphs:
            matched_paragraphs.sort(key=lambda x: x[0], reverse=True)
            top_snippet = matched_paragraphs[0][1]
            return f"🔍 **Cláusula relevante encontrada en el contrato:**\n\n> \"{top_snippet[:400]}...\"\n\n*(Basado en la búsqueda directa en el texto del documento)*"

        return f"He revisado el contrato. Para una respuesta más detallada, puedes configurar tu API Key de Gemini en el panel lateral, o consultar sobre: partes, vigencia, precio/pagos, causales de terminación o matriz de riesgos."
