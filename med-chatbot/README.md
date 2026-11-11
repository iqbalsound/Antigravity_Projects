# 🩺 MedBot - Standalone Medical Q&A Chatbot

An executable, standalone medical Q&A assistant built with Python, Typer, Rich, and the official Google GenAI SDK (`google-genai`).

---

## 🌟 Features

- **Empathetic Medical Persona**: Configured with strict system instructions providing evidence-based educational explanations, symptom overviews, and self-care boundaries.
- **Critical Safety Protocols**: Built-in emergency triage alerts directing users with emergency symptoms (e.g. chest pain, stroke symptoms, severe breathing difficulties) immediately to local emergency care.
- **Mandatory Medical Disclaimer**: Prominently displayed on application startup and permanently attached to every response:
  > *"This application provides educational info only and does not replace professional medical diagnosis or treatment."*
- **Rich Terminal UI**: Beautiful CLI panels, markdown rendering, spinners, and clean error messages.
- **Flexible Modes**:
  - **Interactive Chat**: Multi-turn conversation session (`./med_bot.py`).
  - **Single Query Mode**: Direct one-shot inquiry (`./med_bot.py --query "What causes tension headaches?"`).
- **Comprehensive Unit Testing**: Complete test coverage via `pytest` with mocked Gemini API client and CLI interactions.

---

## 📁 Project Structure

```
med-chatbot/
├── .env.example        # Environment variable template for GEMINI_API_KEY
├── med_bot.py          # Executable entrypoint (Typer + Rich CLI)
├── requirements.txt    # Project dependencies
├── test_med_bot.py     # Pytest unit test suite
└── README.md           # Documentation
```

---

## 🚀 Quickstart

### 1. Set Up Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Your API Key

Obtain an API key from [Google AI Studio](https://aistudio.google.com/):

```bash
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY
```

Alternatively, export it directly:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or pass it as a CLI parameter (`--api-key`).

### 3. Run the Assistant

**Executable CLI (Default model: `gemini-3.8-flash`):**
```bash
chmod +x med_bot.py
./med_bot.py
```

**Single-Query Non-Interactive Mode:**
```bash
./med_bot.py --query "What are the common causes of migraine?"
```

**View CLI Options:**
```bash
./med_bot.py --help
```

---

## 🧪 Running Unit Tests

Run the test suite using `pytest`:

```bash
pytest -v
```

---

## ⚖️ Medical Disclaimer

*This application provides educational info only and does not replace professional medical diagnosis or treatment.*

