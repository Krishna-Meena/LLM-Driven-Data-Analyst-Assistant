"""Unit tests for OllamaService."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.services.ollama_service import OllamaService


@pytest.fixture
def service() -> OllamaService:
    """Fixture to instantiate the OllamaService."""
    return OllamaService(base_url="http://127.0.0.1:11434")


def test_is_healthy_success(service: OllamaService) -> None:
    """Test that is_healthy returns True when server responds 200."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert service.is_healthy() is True
        mock_get.assert_called_once_with("http://127.0.0.1:11434/api/tags", timeout=3)


def test_is_healthy_failure(service: OllamaService) -> None:
    """Test that is_healthy returns False when server connection fails."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Connection refused")
        assert service.is_healthy() is False


def test_get_available_models(service: OllamaService) -> None:
    """Test get_available_models returns correct list of model names."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "qwen2.5-coder:7b", "size": 4683087561},
                {"name": "llama3.3", "size": 8000000000},
            ]
        }
        mock_get.return_value = mock_response

        models = service.get_available_models()
        assert models == ["qwen2.5-coder:7b", "llama3.3"]


def test_generate_completion_success(service: OllamaService) -> None:
    """Test generate_completion returns the correct response text."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "The answer is 42"}
        mock_post.return_value = mock_response

        result = service.generate_completion(
            model="qwen2.5-coder:7b", prompt="What is the meaning of life?"
        )
        assert result == "The answer is 42"
        mock_post.assert_called_once()


def test_generate_completion_failure(service: OllamaService) -> None:
    """Test generate_completion raises RuntimeError when status is not 200."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Ollama API returned status 500"):
            service.generate_completion(model="llama3.3", prompt="Test prompt")
