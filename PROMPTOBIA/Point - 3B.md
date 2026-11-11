Act as an autonomous senior full-stack engineer. Build, configure, and launch a complete 2-stage Medical AI Agent web application on a Kubuntu Linux host environment. Execute all steps end-to-end automatically without asking for manual confirmation during plan compilation or execution.

### 1. Workspace & Environment Setup
- Target OS: Linux (Kubuntu).
- Workspace Directory: Create and navigate into `medical_ai_agent`.
- Virtual Environment: Create `python3 -m venv venv`, activate it, and install: `flask`, `google-genai`, `groq`, and `python-dotenv`.
- Dependencies: Export installed packages into `requirements.txt`.
- Configuration Files: 
  - Create `.env` containing:
    ```env
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    GROQ_API_KEY=YOUR_GROQ_API_KEY
    PORT=9995
    HOST=127.0.0.1
    ```
  - Create `.env.example` with placeholder keys.

### 2. Backend Architecture (`app.py`)
Implement a Flask backend server running on `127.0.0.1:9995`:
- Endpoint `/api/analyze` (POST): Receives JSON payload `{"query": "<user_symptoms>"}`.
- Stage 1 (Primary Medical Agent - Google Gemini):
  - SDK/Model: `google-genai` package using model `gemini-2.5-flash`.
  - Role: Analyze patient symptoms, generate differential diagnoses, suggest home care steps, highlight red-flag signs, and recommend questions for a physician.
  - Safety Directive: Include an explicit directive instructing users to call **1122** immediately if emergency red flags appear.
- Stage 2 (Evaluator & Auditor Agent - Groq):
  - SDK/Model: `groq` package using model `llama-3.3-70b-versatile`.
  - Role: Audit Stage 1 output for clinical safety and accuracy. Output Safety Score (1-10), Completeness Score (1-10), detailed critiques, and a refined final medical response that reinforces emergency contact **1122**.
- Response: Return both `stage1_gemini` and `stage2_evaluator` strings in the output JSON.

### 3. Frontend Web Interface (`templates/index.html`)
Build a dark-themed UI (`#0B0F19` background, `#151C2C` cards, `#38BDF8` blue accents):
- Emergency Banner: Display a top red/amber notice: `"🚨 EMERGENCY NOTICE: If you are experiencing severe chest pain, shortness of breath, or trauma, call 1122 immediately."`
- Header: Display project title and active model status details.
- Input Area: Textarea for symptoms, an "Execute Pipeline" button, and a dynamic loading indicator.
- Dual-Column Layout:
  - Left Panel: Stage 1 initial output (Gemini 2.5 Flash).
  - Right Panel: Stage 2 evaluation scores and refined medical response (Groq Llama 3.3 70B).
- Markdown Rendering: Include `marked.js` CDN script to render all output headers, bold text, and bullet lists cleanly.

### 4. Automated Execution
- Create `app.py`, `templates/index.html`, `requirements.txt`, `.env`, and `.env.example`.
- Launch the Flask server in background/non-blocking mode on port `9995`.
- Output a final confirmation message showing `http://localhost:9995`.