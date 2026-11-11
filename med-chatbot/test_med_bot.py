"""
Unit tests for MedBot Medical Q&A Chatbot.
Tests CLI parameters, user interaction, medical safety rules, disclaimers,
and mocks Gemini API calls using pytest.
"""

from unittest.mock import MagicMock, patch
import pytest
from typer.testing import CliRunner

from med_bot import (
    MANDATORY_DISCLAIMER,
    SYSTEM_INSTRUCTION,
    app,
    format_response,
    get_api_key,
    query_assistant,
)

runner = CliRunner()


def normalize_output(text: str) -> str:
    """Normalize rich terminal box formatting and line wraps into single-space delimited text."""
    return " ".join(text.replace("│", " ").replace("─", " ").split())


def test_cli_help():
    """Verify that --help exits cleanly with code 0 and displays CLI options."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--query" in result.stdout
    assert "--model" in result.stdout
    assert "--api-key" in result.stdout
    assert "Usage:" in result.stdout
    assert "gemini-3.8-flash" in result.stdout


def test_mandatory_disclaimer_constant():
    """Verify that the mandatory medical disclaimer text meets exact safety specifications."""
    expected_text = (
        "This application provides educational info only and does not replace "
        "professional medical diagnosis or treatment."
    )
    assert MANDATORY_DISCLAIMER == expected_text


def test_system_instruction_safety_rules():
    """Verify system instructions contain critical medical safety and emergency triage rules."""
    assert "empathetic" in SYSTEM_INSTRUCTION.lower()
    assert "educational" in SYSTEM_INSTRUCTION.lower()
    assert "emergency" in SYSTEM_INSTRUCTION.lower()
    assert "diagnosis" in SYSTEM_INSTRUCTION.lower()


def test_format_response_appends_disclaimer():
    """Verify that format_response always appends the mandatory disclaimer to responses."""
    raw_answer = "Tension headaches are commonly caused by stress, lack of sleep, or dehydration."
    formatted = format_response(raw_answer)

    assert raw_answer in formatted
    assert MANDATORY_DISCLAIMER in formatted
    assert "Disclaimer" in formatted


def test_get_api_key(monkeypatch):
    """Test API key resolution hierarchy (CLI argument > environment variable)."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert get_api_key(None) is None

    monkeypatch.setenv("GEMINI_API_KEY", "env_secret_key")
    assert get_api_key(None) == "env_secret_key"
    assert get_api_key("cli_override_key") == "cli_override_key"


def test_missing_api_key_exits_with_error(monkeypatch):
    """Verify missing API key produces friendly error banner and exits with code 1."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = runner.invoke(app, [])

    assert result.exit_code == 1
    assert "GEMINI_API_KEY not found" in result.stdout
    assert MANDATORY_DISCLAIMER in normalize_output(result.stdout)


@patch("med_bot.create_genai_client")
def test_single_query_success_mocked(mock_create_client):
    """Test non-interactive single-query mode with mocked Gemini API."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Resting in a quiet, dark room and staying hydrated may help."
    mock_client.models.generate_content.return_value = mock_response
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        app,
        ["--api-key", "test_key", "--query", "How do I manage a mild headache?"],
    )

    assert result.exit_code == 0
    assert "How do I manage a mild headache?" in result.stdout
    assert "Resting in a quiet, dark room" in result.stdout
    assert MANDATORY_DISCLAIMER in normalize_output(result.stdout)
    mock_client.models.generate_content.assert_called_once()


@patch("med_bot.create_genai_client")
def test_single_query_api_error_mocked(mock_create_client):
    """Test single-query error handling when Gemini API raises an exception."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("Connection timeout to Gemini API")
    mock_create_client.return_value = mock_client

    result = runner.invoke(
        app,
        ["--api-key", "test_key", "--query", "What is hypertension?"],
    )

    assert result.exit_code == 1
    assert "Unexpected Error" in result.stdout
    assert "Connection timeout" in result.stdout


@patch("med_bot.Prompt.ask")
@patch("med_bot.create_genai_client")
def test_interactive_session_quit(mock_create_client, mock_prompt_ask):
    """Test interactive chat session exit command ('quit')."""
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_prompt_ask.return_value = "quit"

    result = runner.invoke(app, ["--api-key", "test_key"])

    assert result.exit_code == 0
    assert "Interactive mode active" in result.stdout
    assert "Session ended. Stay safe and healthy!" in result.stdout
    assert MANDATORY_DISCLAIMER in normalize_output(result.stdout)


@patch("med_bot.Prompt.ask")
@patch("med_bot.create_genai_client")
def test_interactive_session_multi_turn_mocked(mock_create_client, mock_prompt_ask):
    """Test interactive chat session sending message and receiving response before exiting."""
    mock_client = MagicMock()
    mock_chat = MagicMock()
    mock_reply = MagicMock()
    mock_reply.text = "Fever is often a natural immune response to infection."
    mock_chat.send_message.return_value = mock_reply
    mock_client.chats.create.return_value = mock_chat
    mock_create_client.return_value = mock_client

    # Simulate user asking a question, then quitting
    mock_prompt_ask.side_effect = ["What causes a fever?", "exit"]

    result = runner.invoke(app, ["--api-key", "test_key"])

    assert result.exit_code == 0
    assert "Fever is often a natural immune response" in result.stdout
    assert MANDATORY_DISCLAIMER in normalize_output(result.stdout)
    assert "Session ended" in result.stdout
    mock_chat.send_message.assert_called_once_with("What causes a fever?")


def test_query_assistant_direct_mock():
    """Direct unit test of query_assistant function."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Caffeine withdrawal may trigger headaches."
    mock_client.models.generate_content.return_value = mock_response

    output = query_assistant(mock_client, "gemini-3.8-flash", "Caffeine headache")
    assert "Caffeine withdrawal may trigger headaches." in output
    assert MANDATORY_DISCLAIMER in output
