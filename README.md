# Agente LegalTech CLM 📄⚖️

**Contract Lifecycle Management & Contract Intelligence System**

Aplicación especializada para la **revisión, extracción, resumen inteligente y auditoría de riesgos de contratos legales** (SaaS, Acuerdos de Confidencialidad NDA, Arrendamientos, Prestación de Servicios, Contratos Laborales, etc.).

---

## 🚀 Inicio Rápido (En 1 Clic)

Simplemente haz doble clic en el archivo lanzador:
```
iniciar_agente.bat
```
El navegador se abrirá automáticamente en: **`http://localhost:5005`**

O desde PowerShell / Terminal:
```powershell
cd "C:\Users\josen\Downloads\AGENTE LEGALTECH"
& "C:\Users\josen\AppData\Local\Python\pythoncore-3.14-64\python.exe" app.py
```

---

## 🌟 Capacidades del Agente CLM

### 1. Ingesta Multiformato
* **Soporte completo:** Carga contratos en formatos `.docx`, `.pdf`, `.txt` y `.md` con drag & drop.
* **Extracción estructurada:** Lectura de cláusulas, párrafos, tablas anexas y metadatos (conteo de palabras, tiempo estimado de lectura y conteo de cláusulas).

### 2. Resumen Ejecutivo & Ficha Técnica Inteligente
* **Ficha Técnica Automatizada:**
  * Identificación de Partes Comparecientes (roles, personerías, domicilios).
  * Tipo contractual detectado.
  * Vigencia y plazo estipulado.
  * Valor o contraprestación económica.
  * Legislación aplicable y régimen de resolución de controversias (arbitraje o justicia ordinaria).
* **Resumen Ejecutivo:** Propósito general del acuerdo, objeto contractual detallado y viñetas con los 4-6 puntos más relevantes.

### 3. Desglose de Obligaciones por Parte
* Matriz comparativa entre la **Parte A** y la **Parte B**, clasificando de forma independiente qué prestaciones debe cumplir cada contratante.

### 4. Términos Económicos y Plazos de Riesgo
* **Régimen Financiero:** Honorarios/precio, modalidad de pago, penalidades por mora y régimen impositivo.
* **Calendario Crítico:** Detección de renovación automática (*tacit renewal*), plazo obligatorio de preaviso para evitar prórrogas no deseadas y causales de terminación anticipada.

### 5. Matriz de Riesgo y Semáforo Legal (Traffic Light)
* **Score de Riesgo (0 a 100):** Clasificación en nivel **ALTO**, **MEDIO** o **BAJO**.
* **Detección de Cláusulas Sensibles y Abusivas:**
  * Falta de límite de responsabilidad (*Liability Cap* o responsabilidad ilimitada).
  * Renovación tácita sin salvaguardas.
  * Cláusulas penales desproporcionadas.
  * Exclusividad y pactos de no competencia o no captación (*non-solicitation*).
  * Régimen de Confidencialidad y Propiedad Intelectual.
* **Recomendaciones de Negociación (*Redlining*):** Sugerencias prácticas para contraofertas y blindaje jurídico.

### 6. Chat Interactivo con el Contrato (Q&A Jurídico)
* Conversa con el agente para formular preguntas puntuales sobre cualquier artículo o duda:
  * *"¿Cómo opera la rescisión anticipada?"*
  * *"¿Qué penalidad aplica por retraso en los pagos?"*
  * *"¿Quién es el titular de los derechos de autor?"*
* El agente responde con precisión contextual citando la cláusula o párrafo relevante.

### 7. Exportación Profesional a Word (.docx) y JSON
* Con un solo clic en **"Exportar Informe Word"**, genera un documento formateado con encabezados, tablas estilizadas con paleta corporativa y semáforo de riesgos listo para enviar a directores o clientes.

---

## 🧠 Arquitectura de Doble Motor de IA

1. **Motor Heurístico Jurídico Offline (100% Autónomo):**
   * Funciona de inmediato sin necesidad de ninguna conexión ni clave API externa.
   * Utiliza reconocimiento de patrones legales, gramática contractual y análisis estático.
2. **Motor LLM Remoto (Google Gemini / OpenAI):**
   * Configurable desde el botón de tuerca en la barra superior.
   * Compatible con **Gemini 1.5 Flash / Gemini 2.0 Flash** y **GPT-4o-mini** mediante prompts jurídicos de alta precisión.

---

## 📁 Estructura del Proyecto

```
AGENTE LEGALTECH/
├── app.py                      # Servidor Web Flask y API REST
├── contract_parser.py          # Extractor multiformato (PDF, DOCX, TXT)
├── clm_agent.py                # Motor del Agente CLM (IA + Heurístico)
├── contract_exporter.py        # Generador de informes Word (.docx)
├── generate_samples.py         # Creador de contratos de prueba
├── iniciar_agente.bat          # Lanzador directo en Windows
├── templates/
│   └── index.html              # Interfaz web del Agente CLM
├── static/
│   ├── css/style.css           # Estilos corporativos LegalTech
│   └── js/app.js               # Lógica interactiva del cliente
├── ejemplos_contratos/         # Contratos de muestra listos para probar
│   ├── Contrato_SaaS_CloudTech.docx
│   ├── Acuerdo_Confidencialidad_NDA.docx
│   └── ...
├── uploads/                    # Almacenamiento temporal de contratos
└── reports/                    # Informes Word y JSON exportados
```
