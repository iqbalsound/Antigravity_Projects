"use strict";

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const form = document.querySelector("#symptom-form");
  const symptomsInput = document.querySelector("#symptoms");
  const charCount = document.querySelector("#char-count");
  const clearButton = document.querySelector("#clear-button");
  const submitButton = document.querySelector("#submit-button");
  const errorMessage = document.querySelector("#error-message");
  const errorText = document.querySelector("#error-text");
  const progressPanel = document.querySelector("#pipeline-progress");
  const stepTier1 = document.querySelector("#step-tier1");
  const stepTier2 = document.querySelector("#step-tier2");
  const resultPanel = document.querySelector("#result-panel");
  const emergencyAlert = document.querySelector("#emergency-alert");
  const triagePill = document.querySelector("#triage-pill");
  const responseContent = document.querySelector("#response");
  const draftContent = document.querySelector("#draft-response");
  const safetyScoreVal = document.querySelector("#safety-score-val");
  const accuracyScoreVal = document.querySelector("#accuracy-score-val");
  const safetyCircle = document.querySelector(".safety-circle");
  const accuracyCircle = document.querySelector(".accuracy-circle");
  const copyGuidanceBtn = document.querySelector("#copy-guidance-btn");
  const printGuidanceBtn = document.querySelector("#print-guidance-btn");
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");
  const concernsListContainer = document.querySelector("#concerns-list-container");
  const concernsCountBadge = document.querySelector("#concerns-count-badge");
  const refinedModelTag = document.querySelector("#refined-model-tag");
  const draftModelTag = document.querySelector("#draft-model-tag");
  const auditModelPill = document.querySelector("#audit-model-pill");

  // Modal elements
  const settingsToggle = document.querySelector("#settings-toggle");
  const settingsModal = document.querySelector("#settings-modal");
  const modalCloseBtn = document.querySelector("#modal-close-btn");
  const geminiStatusBadge = document.querySelector("#gemini-status-badge");
  const groqStatusBadge = document.querySelector("#groq-status-badge");
  const saveKeysBtn = document.querySelector("#save-keys-btn");
  const geminiKeyInput = document.querySelector("#gemini-key-input");
  const groqKeyInput = document.querySelector("#groq-key-input");

  let currentGuidanceMarkdown = "";

  // Presets Database
  const presetData = {
    tension_headache: "I have had a dull, aching band of tightness around my forehead and back of my head for the past 2 days after working long hours on a laptop. No fever, no nausea, and no vision changes.",
    chest_pain: "Sudden crushing, heavy pressure in the center of my chest radiating down my left arm and jaw, accompanied by shortness of breath, dizziness, and cold sweats for 20 minutes.",
    persistent_cough: "Deep, productive cough with greenish phlegm for 7 days, accompanied by a fever of 101.5°F, mild shortness of breath when climbing stairs, and fatigue.",
    diabetic_foot: "I have type 2 diabetes and noticed a small painless blister on the ball of my right foot 3 days ago. The skin around it is now swollen, noticeably warm, and slightly red.",
    pediatric_fever: "My 3-year-old child had a high fever (102.5°F) for 3 days that broke this morning. Now a rosy, pink rash has appeared across their chest and back. They are drinking fluids but fussy."
  };

  // Character Count Listener
  function updateCharCount() {
    const len = symptomsInput.value.length;
    charCount.textContent = len.toLocaleString();
  }
  symptomsInput.addEventListener("input", updateCharCount);

  // Clear button
  clearButton.addEventListener("click", () => {
    symptomsInput.value = "";
    updateCharCount();
    symptomsInput.focus();
  });

  // Preset chips click
  document.querySelectorAll(".preset-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const presetKey = chip.getAttribute("data-preset");
      if (presetData[presetKey]) {
        symptomsInput.value = presetData[presetKey];
        updateCharCount();
        symptomsInput.scrollIntoView({ behavior: "smooth", block: "center" });
        symptomsInput.focus();
      }
    });
  });

  // Markdown rendering helper
  function renderMarkdownSafe(markdownText) {
    if (!window.marked || !window.DOMPurify) {
      return markdownText;
    }
    const rawHtml = window.marked.parse(markdownText, {
      gfm: true,
      breaks: true,
    });
    return window.DOMPurify.sanitize(rawHtml);
  }

  // Update Score SVG gauges
  function setScoreGauge(circleElement, score) {
    const clamped = Math.max(0, Math.min(100, score));
    circleElement.setAttribute("stroke-dasharray", `${clamped}, 100`);
    if (clamped < 70) {
      circleElement.style.stroke = "var(--crimson)";
    } else if (clamped < 85) {
      circleElement.style.stroke = "var(--amber)";
    } else {
      circleElement.style.stroke = "var(--mint)";
    }
  }

  // Populate Result UI
  function displayResults(data) {
    currentGuidanceMarkdown = data.response;

    // Render Markdown for both Refined and Draft
    responseContent.innerHTML = renderMarkdownSafe(data.response);
    if (data.draft) {
      draftContent.innerHTML = renderMarkdownSafe(data.draft);
    } else {
      draftContent.innerHTML = "<p>Primary draft unavailable.</p>";
    }

    // Model tags
    if (data.primary_model) {
      draftModelTag.textContent = data.primary_model;
    }
    if (data.review_model) {
      refinedModelTag.textContent = data.review_model;
      auditModelPill.textContent = `Audited by ${data.review_model}`;
    }

    // Scores
    safetyScoreVal.textContent = data.safety_score;
    accuracyScoreVal.textContent = data.accuracy_score;
    setScoreGauge(safetyCircle, data.safety_score);
    setScoreGauge(accuracyCircle, data.accuracy_score);

    // Triage Level & Emergency
    const triage = data.triage_category || "Routine / Self-Care";
    triagePill.textContent = triage;
    triagePill.className = "triage-pill";

    if (data.emergency_detected || triage.toLowerCase().includes("emergency")) {
      triagePill.classList.add("emergency");
      emergencyAlert.hidden = false;
    } else if (triage.toLowerCase().includes("urgent")) {
      triagePill.classList.add("urgent");
      emergencyAlert.hidden = true;
    } else {
      triagePill.classList.add("routine");
      emergencyAlert.hidden = true;
    }

    // Concerns list
    concernsListContainer.replaceChildren();
    const concerns = Array.isArray(data.concerns) ? data.concerns : [];
    concernsCountBadge.textContent = concerns.length;

    if (concerns.length > 0) {
      const ul = document.createElement("ul");
      ul.className = "concerns-list";
      concerns.forEach((concern) => {
        const li = document.createElement("li");
        li.className = "concern-item";
        li.innerHTML = `
          <span class="concern-icon">⚠️</span>
          <span>${concern}</span>
        `;
        ul.appendChild(li);
      });
      concernsListContainer.appendChild(ul);
    } else {
      const div = document.createElement("div");
      div.className = "no-concerns";
      div.innerHTML = "✓ <strong>Full Protocol Approval:</strong> The Tier 2 clinical safety auditor identified no factual hallucinations, inappropriate prescriptions, or boundary violations.";
      concernsListContainer.appendChild(div);
    }

    // Switch to first tab
    activateTab("tab-refined");

    // Reveal result panel
    resultPanel.hidden = false;
    resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Tab Switching
  function activateTab(tabId) {
    tabBtns.forEach((btn) => {
      const targetId = btn.getAttribute("aria-controls");
      const isSelected = targetId === tabId;
      btn.setAttribute("aria-selected", isSelected);
      btn.classList.toggle("active", isSelected);
    });

    tabPanels.forEach((panel) => {
      const isMatch = panel.id === tabId;
      panel.hidden = !isMatch;
      panel.classList.toggle("active", isMatch);
    });
  }

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("aria-controls");
      activateTab(tabId);
    });
  });

  // Copy Action
  copyGuidanceBtn.addEventListener("click", async () => {
    if (!currentGuidanceMarkdown) return;
    try {
      await navigator.clipboard.writeText(currentGuidanceMarkdown);
      const span = copyGuidanceBtn.querySelector("span");
      const originalText = span.textContent;
      span.textContent = "Copied!";
      setTimeout(() => {
        span.textContent = originalText;
      }, 2000);
    } catch {
      alert("Failed to copy guidance to clipboard.");
    }
  });

  // Print Action
  printGuidanceBtn.addEventListener("click", () => {
    window.print();
  });

  // Form Submit Handler
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const symptomsText = symptomsInput.value.trim();
    if (!symptomsText) return;

    errorMessage.hidden = true;
    resultPanel.hidden = true;
    submitButton.disabled = true;
    submitButton.querySelector(".btn-label").textContent = "Evaluating Pipeline...";

    // Show animated pipeline progress
    progressPanel.hidden = false;
    stepTier1.classList.add("active");
    stepTier2.classList.remove("active");

    const timer = setTimeout(() => {
      stepTier2.classList.add("active");
    }, 1800);

    // Retrieve session overrides if saved
    const geminiKey = sessionStorage.getItem("gemini_api_key") || undefined;
    const groqKey = sessionStorage.getItem("groq_api_key") || undefined;

    try {
      const response = await fetch("/api/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptoms: symptomsText,
          gemini_api_key: geminiKey,
          groq_api_key: groqKey,
        }),
      });

      clearTimeout(timer);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "The two-tier pipeline could not complete evaluation.");
      }

      displayResults(data);
    } catch (err) {
      clearTimeout(timer);
      errorText.textContent = err instanceof Error
        ? err.message
        : "An unexpected error occurred while communicating with the medical agent pipeline.";
      errorMessage.hidden = false;
      errorMessage.scrollIntoView({ behavior: "smooth", block: "center" });
    } finally {
      progressPanel.hidden = true;
      submitButton.disabled = false;
      submitButton.querySelector(".btn-label").textContent = "Run Two-Tier Evaluation";
    }
  });

  // Settings & Status Modal
  async function checkHealthStatus() {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const info = await res.json();
        geminiStatusBadge.textContent = info.gemini_configured ? "Connected" : "Missing Key";
        geminiStatusBadge.className = `badge-status ${info.gemini_configured ? "ok" : "missing"}`;

        groqStatusBadge.textContent = info.groq_configured ? "Connected" : "Missing Key";
        groqStatusBadge.className = `badge-status ${info.groq_configured ? "ok" : "missing"}`;
      }
    } catch {
      geminiStatusBadge.textContent = "Offline";
      groqStatusBadge.textContent = "Offline";
    }
  }

  settingsToggle.addEventListener("click", () => {
    settingsModal.hidden = false;
    checkHealthStatus();
  });

  modalCloseBtn.addEventListener("click", () => {
    settingsModal.hidden = true;
  });

  settingsModal.addEventListener("click", (e) => {
    if (e.target === settingsModal) {
      settingsModal.hidden = true;
    }
  });

  saveKeysBtn.addEventListener("click", () => {
    const gemVal = geminiKeyInput.value.trim();
    const groqVal = groqKeyInput.value.trim();

    if (gemVal) sessionStorage.setItem("gemini_api_key", gemVal);
    if (groqVal) sessionStorage.setItem("groq_api_key", groqVal);

    alert("Session keys saved. Next evaluations will use your provided keys.");
    settingsModal.hidden = true;
  });

  // Initial check
  checkHealthStatus();
});
