# Antigravity Projects

A collection of small Python projects and event documents built with Google Antigravity. Each project is
self-contained: it has its own folder, its own dependencies and its own tests. This README explains how to
run and build every project from the repository root.

> **Medical disclaimer:** `medical-ai-agent` and `med-chatbot` are educational demonstrations. They do not
> diagnose, prescribe or replace a clinician. In an emergency, call your local emergency number.

## Contents

| Folder | What it is | Type | Needs an API key | Build output |
| --- | --- | --- | --- | --- |
| [`medical-ai-agent/`](#1-medical-ai-agent) | Two-tier medical agent web app (Gemini drafts, Groq audits) on port 9995 | Flask web app | Gemini and Groq | None (optional gunicorn deployment) |
| [`med-chatbot/`](#2-med-chatbot) | MedBot, a medical Q&A chatbot for the terminal | CLI (Typer, Rich) | Gemini | Optional single-file binary (PyInstaller) |
| [`Task-3A/`](#3-task-3a-md2html-branded) | `md2html` Markdown to HTML converter with PROMTOBIA branding | CLI | No | None |
| [`demo/`](#4-demo-md2html-installable-package) | `md2html` 0.1.0, installable Markdown to HTML package | CLI and library | No | Wheel and source archive |
| [`PROMPTOBIA/`](#5-promptobia-event-materials) | Event decks, guides, prompts and the MetaOrigin installer | Documents and a shell installer | No | `.deb` and APT repository (via installer) |
| `Task-3A1/` | Empty placeholder folder | None | No | None |

## Repository layout

```
Antigravity_Projects/
├── README.md                  <- this file
├── .gitignore                 <- add the one from "Before you upload to Git"
├── medical-ai-agent/          Flask app: app.py, medical_agent/, templates/, static/, tests/
├── med-chatbot/               CLI: med_bot.py, test_med_bot.py, requirements.txt
├── Task-3A/                   md2html (branded): md2html/, examples/, tests/, requirements.txt
├── demo/                      md2html package: md2html/, pyproject.toml, tests/, examples/
├── PROMPTOBIA/                PDFs, prompts, runbook, BACKUP_install_metaorigin.sh, MetaOrigin/
└── Task-3A1/                  empty
```

## Prerequisites

| Requirement | Why | Check |
| --- | --- | --- |
| Python 3.10 or newer | All projects (`demo` supports 3.9 or newer) | `python3 --version` |
| `python3-venv` and `pip` | One virtual environment per project | `python3 -m venv --help` |
| Git | Upload the repository | `git --version` |
| Internet for the first `pip install` | Download dependencies | |
| Gemini API key (Google AI Studio) | `medical-ai-agent`, `med-chatbot` | https://aistudio.google.com/ |
| Groq API key | `medical-ai-agent` (second tier) | https://console.groq.com/ |

On Ubuntu, Kubuntu or Debian:

```bash
sudo apt install python3 python3-venv python3-pip git
```

**Use one virtual environment per project.** `Task-3A` and `demo` both contain a Python package named
`md2html`, so installing both into one environment makes them overwrite each other.

On Windows PowerShell, replace `source .venv/bin/activate` with `.venv\Scripts\Activate.ps1`.

---

## 1. medical-ai-agent

A single-page web app. Tier 1 (Gemini 2.5 Flash through `google-genai`) drafts a non-diagnostic answer.
Tier 2 (Groq, Llama 3.3 70B) audits it, scores safety and accuracy from 0 to 100, and refines the text.
The page shows the refined answer, the raw draft and the audit concerns.

### Run

```bash
cd medical-ai-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then edit .env and add your keys
python app.py
```

Open http://127.0.0.1:9995 in a browser.

### Configuration (`.env` or exported variables)

| Variable | Required | Meaning |
| --- | --- | --- |
| `GEMINI_API_KEY` or `GOOGLE_API_KEY` | Yes | Gemini key (either name works) |
| `GROQ_API_KEY` | Yes | Groq key for the audit tier |
| `GEMINI_MODEL` | No | Override the primary model (default `gemini-2.5-flash`) |
| `GROQ_MODEL` | No | Override the review model (default `llama-3.3-70b-versatile`) |
| `PORT` | No | Web port (default `9995`) |

Without keys the page still opens, and the API answers with a clear "Set GOOGLE_API_KEY or GEMINI_API_KEY"
message. The keys can also be entered per request (see the API table).

### API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | The web page |
| GET | `/api/health` | `{"status": "ok"}` |
| GET | `/api/status` | Models, whether each key is configured, port |
| GET | `/api/presets` | Sample clinical scenarios |
| POST | `/api/respond` | Body `{"symptoms": "...", "gemini_api_key": optional, "groq_api_key": optional}` |

```bash
curl -s http://127.0.0.1:9995/api/status
curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"symptoms":"Sore throat for two days, mild fever"}' http://127.0.0.1:9995/api/respond
```

### Test

```bash
python -m unittest discover -s tests -v      # 9 tests; the AI calls are mocked, no keys needed
```

### Build and deploy

There is no compile step. For a production-style server instead of the Flask development server:

```bash
pip install gunicorn
gunicorn -b 127.0.0.1:9995 -w 2 app:app
```

> `python app.py` binds to `0.0.0.0`, which exposes the app to your whole network. Use `gunicorn -b
> 127.0.0.1:...` on shared networks, and put a reverse proxy with HTTPS in front before any public use.

---

## 2. med-chatbot

MedBot is a terminal chatbot (Typer and Rich) that talks to Gemini with a medical persona, emergency-triage
alerts and a mandatory disclaimer on every answer.

### Run

```bash
cd med-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then edit .env and set GEMINI_API_KEY
python3 med_bot.py                                   # interactive chat
python3 med_bot.py -q "What causes tension headaches?"   # single question
python3 med_bot.py --help
```

| Option | Meaning |
| --- | --- |
| `-q`, `--query` | Ask one question and exit |
| `-m`, `--model` | Gemini model name (default `gemini-3.8-flash`) |
| `-k`, `--api-key` | Key on the command line (default: `GEMINI_API_KEY`) |

- `med_bot.py` re-launches itself with `./.venv/bin/python3` when that file exists, so keep the virtual
  environment named `.venv` and inside this folder.
- Check that the default model ID is available to your account. If not, pass another with `--model`.

### Test

```bash
pytest -q                 # or: python3 -m pytest -q      (11 tests; the Gemini client is mocked)
```

Run it as `pytest` or `python3 -m pytest`, **not** `python -m pytest`: inside the `.venv`, `python` and `python3`
are different paths, and the auto-switch in `med_bot.py` then restarts the test run silently.

### Build a single-file executable (optional)

```bash
pip install pyinstaller
pyinstaller --onefile --name medbot med_bot.py
GEMINI_API_KEY=your_key ./dist/medbot -q "What is dehydration?"
```

On Linux this produced a working `dist/medbot` of about 25 MB. Build on each operating system you want to
support (PyInstaller does not cross-compile). Give the binary its key through the `GEMINI_API_KEY`
environment variable or `--api-key`.

---

## 3. Task-3A (md2html, branded)

A Markdown to HTML5 converter with syntax highlighting, light, dark and auto themes, and a "Task done for
PROMTOBIA" banner and footer on every page. Uses `markdown` and `Pygments`.

### Run

```bash
cd Task-3A
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m md2html.cli examples/showcase.md                    # writes examples/showcase.html
python -m md2html.cli notes.md -o build/notes.html --open     # open in the browser
python -m md2html.cli docs/ -o build/ --recursive             # convert a folder
python -m md2html.cli page.md --title "My Page" --theme dark
python -m md2html.cli --help
```

| Option | Meaning |
| --- | --- |
| `-o`, `--output` | Output file or folder (default: next to the input, `.html`) |
| `-t`, `--title` | Document title (default: first `#` heading) |
| `--theme {light,dark,auto}` | Color theme (default `auto`) |
| `-r`, `--recursive` | Include subfolders when the input is a folder |
| `-b`, `--open` | Open the result in the default browser |
| `--version` | Print the version (`1.0.0`) |

### Test

```bash
python -m pytest -q
```

Known issue: `tests/test_cli.py` contains the absolute path `/home/iqbal/Antigravity_Projects/Task-3A`, so on any
other machine 8 tests fail with `FileNotFoundError`. In `tests/test_cli.py`, change

```python
cwd=cwd or "/home/iqbal/Antigravity_Projects/Task-3A",
```

to

```python
cwd=cwd or str(Path(__file__).resolve().parent.parent),
```

(`Path` is already imported). With that change all 68 tests pass.

### Build

This project has no packaging file, so there is nothing to compile: run it from the source folder. To get an
installable package, use the `pyproject.toml` approach shown in [`demo/`](#4-demo-md2html-installable-package).

---

## 4. demo (md2html, installable package)

`md2html` 0.1.0: a separate, installable converter with a command (`md2html`), a Python API and pipe
support. Python 3.9 or newer.

### Run

```bash
cd demo
python3 -m venv .venv
source .venv/bin/activate
pip install -e .              # editable install; creates the `md2html` command
pip install pytest            # only needed for the tests

md2html input.md -o output.html
python3 -m md2html input.md -o output.html          # same thing without the command
cat input.md | md2html > output.html                # stdin to stdout
md2html input.md -f -o fragment.html                # HTML fragment only
md2html input.md -t "My Custom Title" -o output.html
md2html input.md --css custom.css -o output.html    # custom stylesheet
md2html input.md --no-css -o output.html            # no embedded CSS
md2html --help
```

Use it from Python:

```python
from md2html import convert_file, convert_markdown
html = convert_markdown("# Hello\n\nSome **bold** text.")
```

### Test

```bash
python -m pytest -q          # 30 tests
```

### Build a distributable package

```bash
pip install build
python -m build
```

This creates `dist/md2html-0.1.0-py3-none-any.whl` and `dist/md2html-0.1.0.tar.gz`. Install the wheel anywhere with:

```bash
pip install dist/md2html-0.1.0-py3-none-any.whl
```

> `demo/.env` is not used by this project. Delete it (see the security section).

---

## 5. PROMPTOBIA (event materials)

Documents and prompts for the PROMPTOBIA event (Tuesday, 10 November 2026). Mostly PDFs, so there is nothing to
install. The code-related items are:

| Item | Purpose |
| --- | --- |
| `PROMPTOBIA Event Deck V3.pdf`, `PROMPTOBIA Step by Step Guide V3.pdf` | Final deck and guide (V2 guide kept for reference) |
| `PROMPTOBIA_Event_Agenda_Final.pdf` | Official agenda |
| `AI Cyber Attacks Myths and Realities*.pdf` | Deep-dive report and presentation |
| `Prompt Framing Experiment.pdf` | Prompt-framing experiment guide |
| `Point - 3A.md` | Cheat sheet of Antigravity slash commands |
| `Point - 3B.md` | The prompt that builds the `medical-ai-agent` project |
| `NCCI Overview.jpeg` | Infographic titled "NCCIA Katalyst: Overview & Key Pillars" (see the warning below) |
| `PROMPT_A_Antigravity.txt`, `PROMPT_B_Claude.txt` | Prompts that build the MetaOrigin app |
| `LIVE_RUNBOOK.txt` | Live demo checklist and troubleshooting |
| `BACKUP_install_metaorigin.sh` | Offline installer that creates the MetaOrigin project |
| `MetaOrigin/` | Copies of the prompts, runbook and demo guide |

> **Check the infographic before using it.** `NCCI Overview.jpeg` describes a generic enterprise AI platform
> (manufacturing, finance and retail use cases, and success figures such as +25% and +30%). That does not match
> public reporting on NCCIA's Katalyst, which is an investigative tool for online child sexual exploitation cases,
> and the figures have no source. Do not present it as fact without verifying it against NCCIA material.

### Build MetaOrigin (a small Linux app with a `.deb` and an APT repository)

Needs `python3`, `dpkg-deb`, `gpg`, `git` and `apt-get` (all standard on Ubuntu and Kubuntu). No internet is needed.

```bash
mkdir -p ~/metaorigin-build && cd ~/metaorigin-build
bash /path/to/PROMPTOBIA/BACKUP_install_metaorigin.sh
```

The script asks six questions (creator name, email, designation, company, GitHub username, repository name),
creates a `metaorigin/` project, runs its self-tests, builds `dist/metaorigin_1.0_all.deb`, builds a signed
APT repository in `docs/apt`, verifies that repository with real `apt`, and runs a demo. Use
`--no-run` to create the files only. Afterwards:

```bash
cd metaorigin
bash scripts/git_init.sh https://github.com/USER/REPO.git
bash scripts/release_v1.sh
git push -u origin main --tags
```

Then publish the release in the browser and enable GitHub Pages (Settings, Pages, branch `main`, folder `/docs`). The
full steps are in `LIVE_RUNBOOK.txt`.

---

## Run all tests at once

From the repository root, after creating each virtual environment as shown above:

```bash
(cd medical-ai-agent && .venv/bin/python -m unittest discover -s tests)
(cd med-chatbot      && .venv/bin/pytest -q)
(cd Task-3A          && .venv/bin/python -m pytest -q)
(cd demo             && .venv/bin/python -m pytest -q)
```

Expected: 9, 11, 68 (after the fix above) and 30 tests pass.

---

## Before you upload to Git

**1. Remove secrets.** `medical-ai-agent/.env`, `med-chatbot/.env` and `demo/.env` contain what look like real API
keys. They are ignored by the project-level `.gitignore` files in `medical-ai-agent` and `med-chatbot`, but `demo`
has no `.gitignore` and its `.env` is not used by anything. If any key was ever uploaded or shared (for example in
a ZIP), treat it as exposed: revoke it in Google AI Studio or the Groq console and create a new one.

```bash
rm demo/.env
```

**2. Remove build clutter.** The folders contain virtual environments (about 700 MB: `med-chatbot/.venv`,
`medical-ai-agent/venv`), `__pycache__`, `.pytest_cache` and LibreOffice lock files (`.~lock.*#`). None of
these belong in Git.

**3. Create a `.gitignore` in the repository root:**

```gitignore
# Secrets
.env
.env.*
!.env.example

# Python
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/

# Build output
build/
dist/
*.spec

# Editor and office leftovers
.~lock.*#
.DS_Store
```

**4. Add an empty folder placeholder** if you want to keep `Task-3A1/`: Git does not track empty folders, so
add a file such as `Task-3A1/.gitkeep`, or delete the folder.

**5. Initialize and push** (no GitHub CLI needed; create a blank repository on GitHub first):

```bash
cd Antigravity_Projects
git init -b main
git add -A
git status                      # review: no .env, no venv, no __pycache__
git commit -m "Add Antigravity projects"
git remote add origin https://github.com/USER/REPO.git
git push -u origin main
```

If a key was committed by mistake, revoke it first, then remove it from Git with `git rm --cached path/to/.env`
and commit. Removing it from old history needs a history rewrite, so revoking the key is the real fix.

## Known issues and recommendations

1. **Task-3A tests use an absolute path** (`/home/iqbal/...`). Fix shown in section 3.
2. **`python -m pytest` in `med-chatbot`** restarts silently because of the `.venv` auto-switch. Use `pytest` or
   `python3 -m pytest`.
3. **Default model `gemini-3.8-flash`** in `med-chatbot`: confirm it exists for your account, or pass `--model`.
4. **Brand spelling:** `Task-3A` prints and embeds "PROMTOBIA" (43 places) while the event is spelled PROMPTOBIA.
   Decide which is intended and replace consistently.
5. **License:** `Task-3A/README.md` shows an MIT badge that links to a `LICENSE` file that does not exist. Add a
   `LICENSE` file or remove the badge. Add a root license before making the repository public.
6. **Duplicate package name:** `Task-3A` and `demo` both provide `md2html`. Keep them in separate environments.
7. **`medical-ai-agent` network exposure:** it listens on `0.0.0.0` and accepts API keys in the request body,
   which it stores in the process environment. Keep it on `127.0.0.1` or behind authentication.
8. **Medical content:** these tools are educational and are not validated for clinical use.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `No module named venv` | `sudo apt install python3-venv` |
| `pip install` fails or is very slow | Check the internet connection; run it again |
| `Set GOOGLE_API_KEY or GEMINI_API_KEY` | Create `.env` from `.env.example` and add the key, or export it in the shell |
| Port 9995 already in use | `PORT=9996 python app.py` |
| `GEMINI_API_KEY not found` in MedBot | Add it to `.env`, export it, or pass `--api-key` |
| `ModuleNotFoundError: markdown` | Activate that project's `.venv` and run `pip install -r requirements.txt` |
| `md2html` runs the wrong version | You installed both md2html projects into one environment; use separate ones |
| Tests pass locally but fail elsewhere | Check for hard-coded paths (see Task-3A) |

## Verification

The commands in this README were run in a clean Ubuntu 24.04 environment with Python 3.12 (the original virtual
environments used Python 3.14): `medical-ai-agent` 9 tests passed and its endpoints and `gunicorn` run worked;
`med-chatbot` 11 tests passed and its PyInstaller binary ran; `Task-3A` 60 of 68 tests passed as shipped and
all 68 after the path fix; `demo` 30 tests passed and its wheel and source archive built. The live Gemini and Groq calls were not run, because they need
your keys. The MetaOrigin installer was run end to end in an earlier session.
