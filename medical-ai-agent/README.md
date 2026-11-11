# MediAgent · Two-Tier Medical Agent Pipeline

A high-contrast single-page clinical intelligence web application built with **Flask running on port 9995**. It implements a two-tiered medical agent pipeline combining **Google GenAI (Gemini 2.5 Flash)** for primary symptom synthesis and **Groq (Llama 3.3 70B)** for safety auditing, accuracy scoring, and clinical refinement.

> **Disclaimer:** MediAgent is an educational and triage demonstration tool. It does not provide medical diagnoses, prescribe medications, or replace professional clinical judgment. In an emergency, always call 1122 (or local emergency dispatch) immediately.

---

## Architecture

```
[ Patient Symptoms ]
         │
         ▼
[ Tier 1: Primary Symptom Synthesis ]
  • Model: Google GenAI (Gemini 2.5 Flash)
  • Role: Symptom parsing, non-diagnostic differentials, supportive care, red flags
         │
         ▼ (Primary Draft)
[ Tier 2: Adversarial Safety & Accuracy Audit ]
  • Model: Groq (Llama 3.3 70B)
  • Role: Clinical hallucination check, pharmacological safety, emergency escalation,
          Safety Scoring (0-100), Accuracy Scoring (0-100), and Text Refinement
         │
         ▼
[ High-Contrast Dark Theme Markdown UI ]
  • Score Gauges: Real-time Safety & Accuracy metrics
  • Multi-Tab Views: Refined Response vs. Raw Gemini Draft vs. Audit Concerns
  • Markdown Rendering: Modern GitHub-flavored markdown via marked.js + DOMPurify
```

---

## Features

- **Port 9995**: Pre-configured and running by default.
- **Two-Tier Pipeline**:
  - **Tier 1 (Gemini 2.5 Flash)**: Primary response generation via `google-genai`.
  - **Tier 2 (Groq Llama 3.3 70B)**: Clinical evaluation, safety/accuracy grading (0–100), red flag detection, and refinement via `groq`.
- **High-Contrast Dark Theme Single-Page UI**:
  - Accessible, WCAG-compliant high-contrast dark theme (`#06090e` base, electric mint `#00f0aa`, cyan `#38bdf8`, and crimson alerts).
  - Modern GitHub-flavored Markdown rendering (`marked.js` + `DOMPurify` sanitization).
  - Quick-select Clinical Presets (Tension Headache, Acute Chest Pain, Persistent Cough, Diabetic Foot Ulcer, Pediatric Fever).
  - Multi-tab inspection: **Refined Guidance (Final)**, **Tier 1 Gemini Draft**, and **Safety Audit & Checklist**.
  - Animated circular SVG score gauges for Safety & Accuracy.
  - Emergency callout banner with 1122 rescue guidance upon detection of high-risk symptoms.
  - Copy to clipboard & Print/PDF export buttons.
  - In-app API diagnostics and session key configuration modal.

---

## Setup & Running

### 1. Requirements

- Python 3.10+
- Google Gemini API Key (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)
- Groq API Key (`GROQ_API_KEY`)

### 2. Environment Setup

```bash
# Activate existing virtual environment
source venv/bin/activate

# Or create a new one
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Keys

In `.env`:
```env
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
PORT=9995
```

### 4. Run the Application

```bash
python app.py
```

Open **[http://localhost:9995](http://localhost:9995)** in your browser.

---

## REST Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the single-page web UI |
| `GET` | `/api/health` | Service health status check (`{"status": "ok"}`) |
| `GET` | `/api/status` | Extended diagnostics: model targets, API key status, active port |
| `GET` | `/api/presets` | Clinical sample scenarios for 1-click testing |
| `POST` | `/api/respond` | Evaluates symptoms through the two-tier pipeline. Accepts `{"symptoms": "...", "gemini_api_key": optional, "groq_api_key": optional}` |

### Sample Response (`POST /api/respond`)

```json
{
  "response": "### Clinical Summary\n...",
  "draft": "### Symptom Overview & Potential Factors\n...",
  "safety_score": 96,
  "accuracy_score": 98,
  "concerns": [
    "Identified minor over-the-counter analgesic ambiguity and clarified maximum dosage duration."
  ],
  "primary_model": "gemini-2.5-flash",
  "review_model": "llama-3.3-70b-versatile",
  "emergency_detected": false,
  "triage_category": "Routine / Self-Care"
}
```

---

## Running Automated Tests

Run the test suite:

```bash
python -m unittest discover tests -v
```

All 9 unit tests cover endpoint validation, payload limits, two-tiered execution, score constraints, and error handling.
