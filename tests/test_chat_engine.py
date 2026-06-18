"""Unit tests for the ChatEngine."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from app.analytics.profiler import ColumnProfile, DataProfile
from app.llm.chat_engine import ChatEngine
from app.services.ollama_service import OllamaService


@pytest.fixture
def mock_ollama() -> OllamaService:
    """Fixture to mock OllamaService."""
    return MagicMock(spec=OllamaService)


@pytest.fixture
def chat_engine(mock_ollama: OllamaService) -> ChatEngine:
    """Fixture to instantiate ChatEngine with mock Ollama."""
    return ChatEngine(
        ollama_service=mock_ollama,
        model_name="qwen2.5-coder:7b",
        max_history_turns=2,  # Set low to easily test sliding window
    )


def test_add_message_sliding_window(chat_engine: ChatEngine) -> None:
    """Test message history size limits and sliding window behavior."""
    # 2 turns = max 4 messages (user + assistant)
    chat_engine.add_message("user", "msg1")
    chat_engine.add_message("assistant", "reply1")
    chat_engine.add_message("user", "msg2")
    chat_engine.add_message("assistant", "reply2")

    assert len(chat_engine.history) == 4
    assert chat_engine.history[0]["content"] == "msg1"

    # Add a 5th message (3rd turn starts, should drop the first turn of 2 messages)
    chat_engine.add_message("user", "msg3")

    assert len(chat_engine.history) == 3
    # The first turn (msg1, reply1) should be dropped
    assert chat_engine.history[0]["content"] == "msg2"
    assert chat_engine.history[-1]["content"] == "msg3"


def test_clear_history(chat_engine: ChatEngine) -> None:
    """Test clearing chat history and execution logs."""
    chat_engine.add_message("user", "hello")
    chat_engine.log_execution("Step run")

    assert len(chat_engine.history) == 1
    assert len(chat_engine.execution_logs) == 1

    chat_engine.clear_history()

    assert len(chat_engine.history) == 0
    assert len(chat_engine.execution_logs) == 0


def test_generate_response_without_context(
    chat_engine: ChatEngine, mock_ollama: MagicMock
) -> None:
    """Test response generation without any dataset uploaded."""
    mock_ollama.generate_chat_response.return_value = "Hello user!"

    reply = chat_engine.generate_response("Hi")

    assert reply == "Hello user!"
    assert len(chat_engine.history) == 2  # user msg + assistant reply
    assert chat_engine.history[0]["content"] == "Hi"
    assert chat_engine.history[1]["content"] == "Hello user!"


def test_generate_response_with_context(
    chat_engine: ChatEngine, mock_ollama: MagicMock
) -> None:
    """Test response generation with DataFrame context injected."""
    mock_ollama.generate_chat_response.return_value = "Analysis reply"
    df = pd.DataFrame({"sales": [100, 200]})
    profile = DataProfile(
        shape=(2, 1),
        num_rows=2,
        num_cols=1,
        columns=["sales"],
        duplicate_rows=0,
        duplicate_pct=0.0,
        memory_usage_bytes=100,
        memory_usage_str="100 B",
        column_profiles={
            "sales": ColumnProfile(
                name="sales",
                dtype="int64",
                missing_count=0,
                missing_pct=0.0,
                num_unique=2,
            )
        },
    )

    reply = chat_engine.generate_response("Analyze sales", df, profile)

    assert reply == "Analysis reply"
    # Verify that the mocked call passed system prompt containing 'sales' column
    mock_ollama.generate_chat_response.assert_called_once()
    args, kwargs = mock_ollama.generate_chat_response.call_args
    passed_messages = kwargs.get("messages", args[1] if len(args) > 1 else [])

    system_message = passed_messages[0]
    assert system_message["role"] == "system"
    assert "sales (Type: int64" in system_message["content"]
