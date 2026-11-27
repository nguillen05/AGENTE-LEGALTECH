/**
 * AGENTE LEGALTECH - CLIENT JAVASCRIPT
 * Gestión de interfaz CLM, carga de documentos, renderizado de resúmenes y chat.
 */

let currentFileName = "Contrato";
let currentContractText = "";
let currentSavedPath = null;
let currentSessionId = null;
let currentAnalysis = null;

// Elementos DOM principales
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const btnBrowse = document.getElementById("btnBrowse");
const contractText = document.getElementById("contractText");
const btnClearText = document.getElementById("btnClearText");
const btnAnalyze = document.getElementById("btnAnalyze");
const btnExportDocx = document.getElementById("btnExportDocx");
const docNameDisplay = document.getElementById("docNameDisplay");
const docMetaBadge = document.getElementById("docMetaBadge");

const emptyState = document.getElementById("emptyState");
const loadingState = document.getElementById("loadingState");
const resultsDashboard = document.getElementById("resultsDashboard");

// Chat DOM
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const btnClearChat = document.getElementById("btnClearChat");

// Configuración DOM
const inputApiKey = document.getElementById("inputApiKey");
const selectAiProvider = document.getElementById("selectAiProvider");
const btnSaveSettings = document.getElementById("btnSaveSettings");
const btnToggleApiKey = document.getElementById("btnToggleApiKey");
const apiStatusLabel = document.getElementById("apiStatusLabel");

// ==========================================
// INICIALIZACIÓN
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  loadSavedSettings();
  setupEventListeners();
  loadSampleButtons();
});

function loadSavedSettings() {
  const savedKey = localStorage.getItem("clm_api_key") || "";
  const savedProvider = localStorage.getItem("clm_provider") || "gemini";
  
  if (inputApiKey) inputApiKey.value = savedKey;
  if (selectAiProvider) selectAiProvider.value = savedProvider;
  
  // Consultar también si el servidor ya tiene una clave en .env
  fetch("/api/config")
    .then(r => r.json())
    .then(data => {
      if (data.has_server_key) {
        if (!savedKey) {
          updateApiStatusBadge(data.masked_key, data.provider);
          if (selectAiProvider) selectAiProvider.value = data.provider;
          if (inputApiKey) inputApiKey.placeholder = `Configurada en servidor (${data.masked_key})`;
        } else {
          updateApiStatusBadge(savedKey, savedProvider);
        }
      } else {
        updateApiStatusBadge(savedKey, savedProvider);
      }
    })
    .catch(() => {
      updateApiStatusBadge(savedKey, savedProvider);
    });
}

function updateApiStatusBadge(key, provider) {
  if (apiStatusLabel) {
    if (key && key.trim().length > 10) {
      apiStatusLabel.textContent = `IA: ${provider.toUpperCase()}`;
      apiStatusLabel.className = "d-none d-md-inline text-gold fw-medium";
    } else {
      apiStatusLabel.textContent = "Motor: Heurístico Local";
      apiStatusLabel.className = "d-none d-md-inline text-light-50";
    }
  }
}

// ==========================================
// EVENT LISTENERS
// ==========================================
function setupEventListeners() {
  // Drag & drop
  btnBrowse.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("click", () => fileInput.click());
  
  ["dragenter", "dragover"].forEach(event => {
    dropZone.addEventListener(event, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(event => {
    dropZone.addEventListener(event, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("dragover");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFileUpload(files[0]);
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) handleFileUpload(e.target.files[0]);
  });

  // Texto manual
  contractText.addEventListener("input", () => {
    currentContractText = contractText.value;
    updateTextStats(currentContractText);
  });

  btnClearText.addEventListener("click", () => {
    contractText.value = "";
    currentContractText = "";
    currentFileName = "Contrato";
    docNameDisplay.textContent = "Texto del Documento";
    docMetaBadge.textContent = "Sin cargar";
    showEmptyState();
  });

  // Ejecución del análisis
  btnAnalyze.addEventListener("click", executeAnalysis);

  // Exportar Word
  btnExportDocx.addEventListener("click", exportWordReport);

  // Chat
  chatForm.addEventListener("submit", handleChatSubmit);
  btnClearChat.addEventListener("click", resetChat);

  // Settings
  btnSaveSettings.addEventListener("click", () => {
    const key = inputApiKey.value.trim();
    const provider = selectAiProvider.value;
    localStorage.setItem("clm_api_key", key);
    localStorage.setItem("clm_provider", provider);
    updateApiStatusBadge(key, provider);
    
    // Guardar también en el servidor (.env)
    fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: key, provider: provider })
    }).catch(() => {});

    // Cerrar modal
    const modalEl = document.getElementById("settingsModal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
  });

  if (btnToggleApiKey) {
    btnToggleApiKey.addEventListener("click", () => {
      inputApiKey.type = inputApiKey.type === "password" ? "text" : "password";
    });
  }
}

// ==========================================
// CARGA Y PARSEO DE ARCHIVOS
// ==========================================
function handleFileUpload(file) {
  const formData = new FormData();
  formData.append("file", file);

  showLoading("Cargando y extrayendo documento...", "Procesando estructura, párrafos y tablas");

  fetch("/api/upload", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    hideLoading();
    if (data.success) {
      currentFileName = data.filename;
      currentContractText = data.text;
      currentSavedPath = data.saved_path || null;
      contractText.value = data.text;
      
      docNameDisplay.textContent = currentFileName;
      const m = data.metadata;
      docMetaBadge.textContent = `${m.format.toUpperCase()} | ${m.word_count} palabras | ~${m.estimated_read_time_min} min`;
      
      // Ejecutar análisis automáticamente tras carga
      executeAnalysis();
    } else {
      alert("Error al cargar archivo: " + (data.error || "Formato desconocido"));
    }
  })
  .catch(err => {
    hideLoading();
    alert("Error de red al procesar el archivo: " + err.message);
  });
}

function loadSampleByName(filename) {
  showLoading("Cargando contrato de ejemplo...", filename);
  
  fetch("/api/load-sample", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename })
  })
  .then(res => res.json())
  .then(data => {
    hideLoading();
    if (data.success) {
      currentFileName = data.filename;
      currentContractText = data.text;
      currentSavedPath = data.saved_path || null;
      contractText.value = data.text;
      
      docNameDisplay.textContent = currentFileName;
      const m = data.metadata;
      docMetaBadge.textContent = `${m.format.toUpperCase()} | ${m.word_count} palabras | ~${m.estimated_read_time_min} min`;
      
      executeAnalysis();
    } else {
      alert("Error al cargar ejemplo: " + data.error);
    }
  })
  .catch(err => {
    hideLoading();
    alert("Error al cargar ejemplo: " + err.message);
  });
}

function loadSampleButtons() {
  document.querySelectorAll(".sample-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const sample = btn.getAttribute("data-sample");
      if (sample) loadSampleByName(sample);
    });
  });
}

function updateTextStats(text) {
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  if (words > 0) {
    docMetaBadge.textContent = `${words} palabras | ~${(words / 200).toFixed(1)} min`;
  } else {
    docMetaBadge.textContent = "Sin contenido";
  }
}

// ==========================================
// EJECUCIÓN DEL ANÁLISIS CLM
// ==========================================
function executeAnalysis() {
  const text = contractText.value.trim();
  if (!text) {
    alert("Por favor carga un archivo de contrato o escribe su contenido primero.");
    return;
  }

  const apiKey = localStorage.getItem("clm_api_key") || "";
  const provider = localStorage.getItem("clm_provider") || "gemini";

  showLoading("Auditoría CLM en Curso...", "Generando resumen ejecutivo, extrayendo obligaciones y evaluando matriz de riesgos");

  fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: text,
      filename: currentFileName,
      saved_path: currentSavedPath,
      api_key: apiKey,
      provider: provider
    })
  })
  .then(res => res.json())
  .then(data => {
    hideLoading();
    if (data.success) {
      currentSessionId = data.session_id;
      currentAnalysis = data.analysis;
      renderAnalysisResults(data.analysis);
      btnExportDocx.disabled = false;
    } else {
      alert("Error durante el análisis: " + (data.error || "Error desconocido"));
    }
  })
  .catch(err => {
    hideLoading();
    alert("Error de conexión al analizar: " + err.message);
  });
}

// ==========================================
// RENDERIZADO DEL DASHBOARD
// ==========================================
function renderAnalysisResults(analysis) {
  emptyState.classList.add("d-none");
  resultsDashboard.classList.remove("d-none");

  // 1. BANNER SUPERIOR
  const ficha = analysis.ficha_tecnica || {};
  const resumen = analysis.resumen_ejecutivo || {};
  const matriz = analysis.matriz_riesgos || {};

  document.getElementById("resContractTypeBadge").textContent = (ficha.tipo_contrato || "CONTRATO").toUpperCase();
  document.getElementById("resContractTitle").textContent = ficha.tipo_contrato || currentFileName;
  document.getElementById("resSummaryLead").textContent = resumen.proposito_general || "Sin resumen disponible.";
  document.getElementById("resEngineBadge").textContent = `Motor: ${analysis.engine_used || "Agente CLM"}`;

  // Semáforo de Riesgo
  const riskLvl = (matriz.nivel_riesgo_global || "MEDIO").toUpperCase();
  const riskBadge = document.getElementById("resRiskBadge");
  riskBadge.textContent = riskLvl;
  riskBadge.className = `badge fs-6 px-3 py-2 ${riskLvl === 'ALTO' ? 'badge-risk-high' : (riskLvl === 'MEDIO' ? 'badge-risk-medium' : 'badge-risk-low')}`;
  document.getElementById("resRiskScore").textContent = `${matriz.puntuacion_riesgo || 50}/100`;

  // 2. FICHA TÉCNICA
  const fichaGrid = document.getElementById("fichaDetailsGrid");
  const partesStr = (ficha.partes || []).map(p => `<strong>${p.nombre || 'Parte'}</strong> (${p.rol || ''})`).join("<br>") || "No especificado";

  fichaGrid.innerHTML = `
    <div class="col-md-6">
      <div class="ficha-item">
        <div class="ficha-label"><i class="bi bi-people me-1"></i> Partes Comparecientes</div>
        <div class="ficha-val fs-xs">${partesStr}</div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="ficha-item">
        <div class="ficha-label"><i class="bi bi-calendar3 me-1"></i> Vigencia y Duración</div>
        <div class="ficha-val">${ficha.vigencia || 'N/D'}</div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="ficha-item">
        <div class="ficha-label"><i class="bi bi-cash-stack me-1"></i> Valor / Honorarios</div>
        <div class="ficha-val text-success">${ficha.moneda_monto || 'N/D'}</div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="ficha-item">
        <div class="ficha-label"><i class="bi bi-bank me-1"></i> Jurisdicción y Ley</div>
        <div class="ficha-val">${ficha.ley_aplicable || 'N/D'}</div>
      </div>
    </div>
    <div class="col-12">
      <div class="ficha-item">
        <div class="ficha-label"><i class="bi bi-hammer me-1"></i> Resolución de Controversias</div>
        <div class="ficha-val fs-xs">${ficha.resolucion_conflictos || 'Tribunales ordinarios'}</div>
      </div>
    </div>
  `;

  document.getElementById("resObjetoContractual").textContent = resumen.objeto_contractual || "No especificado.";
  
  const puntosContainer = document.getElementById("resPuntosClaveList");
  puntosContainer.innerHTML = (resumen.puntos_clave || []).map(pt => `
    <div class="d-flex align-items-start gap-2 bg-light p-2 rounded border">
      <i class="bi bi-check-circle-fill text-primary-gold mt-1"></i>
      <span class="fs-sm text-navy">${pt}</span>
    </div>
  `).join("");

  // 3. OBLIGACIONES POR PARTE
  const obligacionesRow = document.getElementById("obligacionesRow");
  const grupos = analysis.obligaciones_partes || [];
  if (grupos.length > 0) {
    obligacionesRow.innerHTML = grupos.map((g, idx) => `
      <div class="col-md-${grupos.length > 1 ? '6' : '12'}">
        <div class="card shadow-sm border-0 rounded-3 h-100">
          <div class="card-header bg-navy text-white py-2">
            <span class="badge bg-gold text-dark me-2">Parte ${idx + 1}</span>
            <strong class="fs-sm">${g.parte || 'Parte Contractual'}</strong>
          </div>
          <div class="card-body p-3">
            <ul class="list-unstyled mb-0 d-flex flex-column gap-2">
              ${(g.obligaciones || []).map(o => `
                <li class="d-flex align-items-start gap-2 fs-sm">
                  <i class="bi bi-arrow-right-circle text-primary mt-1"></i>
                  <span>${o}</span>
                </li>
              `).join("")}
            </ul>
          </div>
        </div>
      </div>
    `).join("");
  } else {
    obligacionesRow.innerHTML = `<div class="col-12 text-muted">No se extrajeron obligaciones específicas.</div>`;
  }

  // 4. ECONOMÍA Y PLAZOS
  const eco = analysis.terminos_economicos || {};
  document.getElementById("resEconomiaContent").innerHTML = `
    <div class="mb-3">
      <span class="text-muted fs-xs fw-semibold">PRECIO / CONTRAPRESTACIÓN:</span>
      <h5 class="fw-bold text-success mb-1">${eco.precio_honorarios || 'No especificado'}</h5>
    </div>
    <div class="mb-3">
      <span class="text-muted fs-xs fw-semibold">FORMA Y CONDICIONES DE PAGO:</span>
      <p class="fs-sm mb-1">${eco.forma_pago || 'Según estipulaciones contractuales'}</p>
    </div>
    <div class="mb-3">
      <span class="text-muted fs-xs fw-semibold">PENALIDADES E INTERESES DE MORA:</span>
      <p class="fs-sm mb-1 text-danger">${eco.intereses_mora || 'Sin penalidad moratoria expresa'}</p>
    </div>
    <div>
      <span class="text-muted fs-xs fw-semibold">RÉGIMEN TRIBUTARIO / RETENCIONES:</span>
      <p class="fs-sm mb-0">${eco.impuestos || 'Cada parte asume los impuestos de ley'}</p>
    </div>
  `;

  const plazos = analysis.plazos_y_terminacion || {};
  const causales = (plazos.causales_resolucion || []).map(c => `<li>${c}</li>`).join("");
  document.getElementById("resPlazosContent").innerHTML = `
    <div class="mb-3">
      <span class="text-muted fs-xs fw-semibold">PLAZO DE DURACIÓN:</span>
      <h6 class="fw-bold text-navy mb-1">${plazos.plazo_duracion || '1 año'}</h6>
    </div>
    <div class="mb-3">
      <span class="text-muted fs-xs fw-semibold">PRÓRROGA / RENOVACIÓN AUTOMÁTICA:</span>
      <p class="fs-sm mb-1">
        ${plazos.renovacion_automatica ? '<span class="badge bg-warning text-dark">SÍ - Renovación Automática</span>' : '<span class="badge bg-secondary">NO - Requiere Acuerdo Escrito</span>'}
        <br><small class="text-muted">${plazos.condiciones_renovacion || ''}</small>
      </p>
    </div>
    <div class="mb-3">
      <span class="text-muted fs-xs fw-semibold">PREAVISO PARA NO RENOVAR:</span>
      <p class="fs-sm mb-1 fw-bold text-navy">${plazos.preaviso_no_renovacion || '30 días de anticipación'}</p>
    </div>
    <div>
      <span class="text-muted fs-xs fw-semibold">CAUSALES DE RESOLUCIÓN:</span>
      <ul class="fs-sm ps-3 mb-0">${causales || '<li>Incumplimiento grave</li>'}</ul>
    </div>
  `;

  // 5. MATRIZ DE RIESGO
  const alertasContainer = document.getElementById("resAlertasContainer");
  const alertas = matriz.alertas || [];
  if (alertas.length > 0) {
    alertasContainer.innerHTML = alertas.map(a => {
      const lvl = (a.nivel || "MEDIO").toUpperCase();
      const cardClass = lvl === 'ALTO' ? 'risk-high' : (lvl === 'MEDIO' ? 'risk-medium' : 'risk-low');
      const badgeClass = lvl === 'ALTO' ? 'bg-danger' : (lvl === 'MEDIO' ? 'bg-warning text-dark' : 'bg-success');
      return `
        <div class="risk-card ${cardClass}">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="fw-bold text-navy mb-0">${a.clausula || 'Cláusula Contractual'}</h6>
            <span class="badge ${badgeClass} fs-xxs">NIVEL ${lvl}</span>
          </div>
          <p class="fs-sm text-secondary mb-2">${a.hallazgo || ''}</p>
          <div class="bg-white p-2 rounded border border-light">
            <small class="text-muted fw-semibold"><i class="bi bi-lightbulb-fill text-warning me-1"></i> Recomendación de Mitigación:</small>
            <p class="fs-xs mb-0 text-navy">${a.recomendacion || 'Revisar en negociación'}</p>
          </div>
        </div>
      `;
    }).join("");
  } else {
    alertasContainer.innerHTML = `<div class="text-muted fs-sm">No se detectaron alertas críticas de riesgo.</div>`;
  }

  const recomList = document.getElementById("resRecomendacionesList");
  recomList.innerHTML = (analysis.recomendaciones_negociacion || []).map(r => `
    <li class="list-group-item px-0 py-2 d-flex align-items-start gap-2 fs-sm">
      <i class="bi bi-pencil-square text-primary-gold mt-1"></i>
      <span>${r}</span>
    </li>
  `).join("");
}

// ==========================================
// CHAT CON EL CONTRATO (Q&A)
// ==========================================
function handleChatSubmit(e) {
  e.preventDefault();
  const q = chatInput.value.trim();
  if (!q) return;

  appendUserMessage(q);
  chatInput.value = "";
  
  // Agregar indicador de pensando
  const thinkingId = appendAgentThinking();

  fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: currentSessionId,
      question: q,
      text: currentContractText,
      saved_path: currentSavedPath,
      analysis: currentAnalysis,
      api_key: localStorage.getItem("clm_api_key") || "",
      provider: localStorage.getItem("clm_provider") || "gemini"
    })
  })
  .then(res => res.json())
  .then(data => {
    removeThinking(thinkingId);
    if (data.success) {
      appendAgentMessage(data.answer);
    } else {
      appendAgentMessage("Lo siento, ocurrió un error al responder: " + data.error);
    }
  })
  .catch(err => {
    removeThinking(thinkingId);
    appendAgentMessage("Error de conexión al consultar al agente: " + err.message);
  });
}

function sendQuickQuery(query) {
  // Activar pestaña de chat si no está activa
  const chatTabBtn = document.getElementById("tab-chat-btn");
  if (chatTabBtn) {
    const tab = new bootstrap.Tab(chatTabBtn);
    tab.show();
  }
  chatInput.value = query;
  handleChatSubmit(new Event("submit"));
}

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "chat-bubble user-bubble mb-3";
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendAgentMessage(markdownText) {
  const div = document.createElement("div");
  div.className = "chat-bubble agent-bubble mb-3";
  // Conversión simple de markdown básico (* y #)
  let formatted = markdownText
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
  div.innerHTML = formatted;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendAgentThinking() {
  const id = "thinking-" + Date.now();
  const div = document.createElement("div");
  div.id = id;
  div.className = "chat-bubble agent-bubble mb-3 text-muted";
  div.innerHTML = '<span class="spinner-grow spinner-grow-sm me-1" role="status"></span> Consultando el texto del contrato...';
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function removeThinking(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function resetChat() {
  chatMessages.innerHTML = `
    <div class="chat-bubble agent-bubble mb-3">
      <p class="mb-1">Chat reiniciado. ¿En qué cláusula o aspecto del contrato te puedo orientar?</p>
    </div>
  `;
}

// ==========================================
// EXPORTACIÓN A WORD
// ==========================================
function exportWordReport() {
  if (!currentAnalysis) {
    alert("No hay análisis generado para exportar.");
    return;
  }

  btnExportDocx.disabled = true;
  btnExportDocx.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Generando DOCX...';

  fetch("/api/export-docx", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: currentSessionId,
      filename: currentFileName,
      analysis: currentAnalysis
    })
  })
  .then(resp => {
    if (!resp.ok) throw new Error("Error en la descarga del informe");
    return resp.blob();
  })
  .then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Informe_CLM_${currentFileName.replace(/\.[^/.]+$/, "")}.docx`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    btnExportDocx.disabled = false;
    btnExportDocx.innerHTML = '<i class="bi bi-file-earmark-word me-1"></i> Exportar Informe Word';
  })
  .catch(err => {
    btnExportDocx.disabled = false;
    btnExportDocx.innerHTML = '<i class="bi bi-file-earmark-word me-1"></i> Exportar Informe Word';
    alert("Error al exportar documento: " + err.message);
  });
}

// ==========================================
// UTILIDADES UI
// ==========================================
function showLoading(title, desc) {
  emptyState.classList.add("d-none");
  resultsDashboard.classList.add("d-none");
  loadingState.classList.remove("d-none");
  
  if (title) document.getElementById("loadingTitle").textContent = title;
  if (desc) document.getElementById("loadingDesc").textContent = desc;
}

function hideLoading() {
  loadingState.classList.add("d-none");
}

function showEmptyState() {
  resultsDashboard.classList.add("d-none");
  loadingState.classList.add("d-none");
  emptyState.classList.remove("d-none");
  btnExportDocx.disabled = true;
}
