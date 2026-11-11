## Essential slash commands and shortcut keys for Google Antigravity include:

### Core Slash Commands

- `/clear` (Alias: /new): Clears the terminal output and resets your active conversation context.
- `/plan [task]`: Explores the codebase, clarifies requirements, and drafts a reviewable implementation plan.
- `/goal <task>`: Puts the agent into an autonomous loop (research, plan, execute, verify, fix) until the goal is finished.
- `/grillme`: Prompts the agent to ask clarifying questions before writing code for open-ended or complex tasks.
- `/resume (Alias: /switch)`: Opens the conversation picker overlay to load previous threads.
- `/model <model>`: Switches your active reasoning model.
- `/exit (Alias: /quit)`: Closes the TUI session and returns to your host shell.

### Essential Keybindings & Shortcuts

- `Enter`: Submits your prompt or active menu selection.
- `Shift + Tab`: Cycles through execution modes (default, accept-edits, auto, plan).
- `Ctrl + L`: Clears the terminal screen.
- `Ctrl + C`: Stops an active stream, closes menus, or cancels the current prompt.
- `Ctrl + G`: Opens your default external shell editor ($EDITOR) to compose your prompt.
- `Ctrl + _ or Ctrl + Shift + -`: Undoes the last edit.

### Sample Prompt
    `/plan Create a Python app that converts Markdown files to clean HTML. Include unit tests using pytest and run the tests in the terminal`.

## Review the Agent's Plan:
    The agent will output a step-by-step action plan (e.g., set up virtual environment, install dependencies, create converter.py, write test_converter.py, execute tests).
    Click Approve & Execute.
    **Observe Agent Execution Functions:** 
    File System Operations: Watch the agent generate files inside `~/projects/antigravity-demo`. 

### Terminal Execution: 
    Watch the command output panel as the agent creates a venv, installs requirements, and runs pytest in the background.

## Self-Correction Loop:
    If a test fails, the agent will analyze the terminal output trace, edit converter.py, and automatically re-run pytest until all tests pass.
## Test Browser
    ActuationAntigravity can launch local Browser sessions to visually test web apps. 
    Enter the following slash command in the chat window:
    `/browser Serve the generated HTML output using a simple Python HTTP server on port 8000 and verify it loads` correctly.
    Grant permission when the prompt requests access to launch a local browser window.
    The agent will start `python -m http.server 8000`, open Browser, inspect the page, and report back.
