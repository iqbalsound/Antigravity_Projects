#!/usr/bin/env python3
"""
Medical Q&A Chatbot CLI
A standalone, interactive medical information assistant powered by the official google-genai SDK.
"""

import os
import sys
from pathlib import Path

# Automatically switch to local .venv if not already active
_venv_python = Path(__file__).resolve().parent / ".venv" / "bin" / "python3"
if _venv_python.exists() and sys.executable != str(_venv_python):
    os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
import typer

# Initialize environment variables
load_dotenv()

app = typer.Typer(
    help="🩺 MedBot: An interactive medical information assistant using Google Gemini.",
    add_completion=False,
)
console = Console()

# Mandatory medical disclaimer
MANDATORY_DISCLAIMER = (
    "This application provides educational info only and does not replace "
    "professional medical diagnosis or treatment."
)

# System persona instruction for the Gemini model
SYSTEM_INSTRUCTION = (
    "You are an empathetic, knowledgeable, and responsible medical information assistant. "
    "Your mission is to provide accurate, evidence-based educational explanations "
    "about health topics, symptoms, conditions, and wellness.\n\n"
    "Crucial Guidelines & Safety Rules:\n"
    "1. Never provide a binding medical diagnosis or prescribe medication dosages.\n"
    "2. Always emphasize that this information is educational and recommend consulting a licensed healthcare professional.\n"
    "3. EMERGENCY TRIAGE: If symptoms suggest a medical emergency (e.g., severe chest pain, "
    "difficulty breathing, signs of stroke, severe bleeding, or thoughts of self-harm), "
    "immediately and explicitly advise the user to contact local emergency services (such as 911) or proceed to the nearest emergency facility.\n"
    "4. Structure answers clearly with structured headings, bullet points, potential causes, general self-care advice, and warning signs."
)


def get_api_key(cli_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Gemini API key from CLI argument or environment variables."""
    return cli_key or os.getenv("GEMINI_API_KEY")


def display_startup_banner() -> None:
    """Display the title banner and mandatory medical disclaimer."""
    title_text = (
        "[bold cyan]🩺 MedBot — Medical Information Assistant[/bold cyan]\n"
        "[dim]Powered by Google Gemini & the official google-genai SDK[/dim]\n\n"
        f"[bold yellow]⚠️ Mandatory Medical Disclaimer:[/bold yellow]\n"
        f"[italic]{MANDATORY_DISCLAIMER}[/italic]"
    )
    console.print(
        Panel(
            title_text,
            title="[bold green]Welcome[/bold green]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def format_response(response_text: str) -> str:
    """Format the model response, appending the mandatory medical disclaimer."""
    clean_text = response_text.strip()
    disclaimer_block = f"\n\n---\n**Disclaimer:** *{MANDATORY_DISCLAIMER}*"
    return f"{clean_text}{disclaimer_block}"


def display_response(formatted_text: str) -> None:
    """Render markdown response inside a styled Rich panel."""
    md = Markdown(formatted_text)
    console.print(
        Panel(
            md,
            title="[bold green]MedBot Response[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )


def create_genai_client(api_key: str) -> genai.Client:
    """Instantiate and return the official google-genai Client."""
    return genai.Client(api_key=api_key)


def query_assistant(
    client: genai.Client,
    model: str,
    prompt: str,
    chat_session: Optional[object] = None,
) -> str:
    """
    Send prompt to Gemini model and return formatted response text.
    Supports either multi-turn chat_session or single generation.
    """
    if chat_session is not None:
        response = chat_session.send_message(prompt)
    else:
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
        )
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

    raw_text = response.text or "No response received from the medical assistant."
    return format_response(raw_text)


@app.command()
def main(
    query: Optional[str] = typer.Option(
        None,
        "--query",
        "-q",
        help="Single medical query to ask in non-interactive mode.",
    ),
    model: str = typer.Option(
        "gemini-3.8-flash",
        "--model",
        "-m",
        help="Gemini model name to use.",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Gemini API Key (defaults to GEMINI_API_KEY environment variable).",
    ),
) -> None:
    """
    Launch MedBot interactive chat or execute a single medical Q&A query.
    """
    display_startup_banner()

    resolved_api_key = get_api_key(api_key)
    if not resolved_api_key:
        console.print(
            Panel(
                "[bold red]Error: GEMINI_API_KEY not found![/bold red]\n\n"
                "Please configure your API key by:\n"
                "  1. Creating a [cyan].env[/cyan] file based on [cyan].env.example[/cyan]\n"
                "  2. Exporting [cyan]GEMINI_API_KEY[/cyan] in your environment\n"
                "  3. Passing [cyan]--api-key <YOUR_KEY>[/cyan] on the command line\n\n"
                "Get an API key from Google AI Studio: [link=https://aistudio.google.com/]https://aistudio.google.com/[/link]",
                title="[bold red]Missing API Key[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)

    try:
        client = create_genai_client(resolved_api_key)
    except Exception as exc:
        console.print(f"[bold red]Failed to initialize Gemini client:[/bold red] {exc}")
        raise typer.Exit(code=1)

    # Single-query mode
    if query:
        console.print(f"[bold cyan]User Query:[/bold cyan] {query}\n")
        try:
            with console.status("[bold green]Analyzing medical query...[/bold green]", spinner="dots"):
                answer = query_assistant(client, model, query)
            display_response(answer)
        except errors.APIError as api_err:
            console.print(
                Panel(
                    f"[bold red]Gemini API Error:[/bold red] {api_err.message if hasattr(api_err, 'message') else api_err}",
                    title="[bold red]API Connection Error[/bold red]",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)
        except Exception as exc:
            console.print(
                Panel(
                    f"[bold red]Unexpected Error:[/bold red] {exc}",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)
        return

    # Interactive multi-turn chat mode
    try:
        chat_config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
        )
        chat = client.chats.create(model=model, config=chat_config)
    except Exception as exc:
        console.print(f"[bold red]Failed to initiate chat session:[/bold red] {exc}")
        raise typer.Exit(code=1)

    console.print(
        "[bold cyan]Interactive mode active.[/bold cyan] Type your health questions below. "
        "Type [bold yellow]'exit'[/bold yellow], [bold yellow]'quit'[/bold yellow], or [bold yellow]'q'[/bold yellow] to exit.\n"
    )

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Session ended. Stay safe and healthy![/bold yellow]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            console.print("[bold yellow]Session ended. Stay safe and healthy![/bold yellow]")
            break

        try:
            with console.status("[bold green]Consulting medical assistant...[/bold green]", spinner="dots"):
                answer = query_assistant(client, model, user_input, chat_session=chat)
            display_response(answer)
            console.print()  # Add spacing
        except errors.APIError as api_err:
            err_msg = getattr(api_err, "message", str(api_err))
            console.print(
                Panel(
                    f"[bold red]Gemini API Error:[/bold red] {err_msg}\nPlease try again or verify your connection.",
                    title="[bold red]API Error[/bold red]",
                    border_style="red",
                )
            )
        except Exception as exc:
            console.print(
                Panel(
                    f"[bold red]Unexpected Error:[/bold red] {exc}\nPlease try again.",
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                )
            )


if __name__ == "__main__":
    app()
