"""Service layer for interacting with local Ollama LLM models.

Provides health checks, auto-start, model listing, and completion
requests with retry logic and exponential backoff.
"""

import os
import subprocess
import time
from typing import Any

import requests

from app.utils.logger import setup_logger

logger = setup_logger("ollama_service")

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1.0
BACKOFF_MULTIPLIER = 2.0


class OllamaService:
    """Manages connection, health checks, and completion requests to local Ollama."""

    def __init__(self, base_url: str = DEFAULT_OLLAMA_URL):
        """Initializes the Ollama service with a base API URL.

        Args:
            base_url: The URL where the Ollama server is hosting its API.
        """
        self.base_url = base_url.rstrip("/")

    def is_healthy(self) -> bool:
        """Pings the Ollama tags endpoint to verify if the server is running.

        Returns:
            True if the server responded with HTTP status 200, False otherwise.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def ensure_ollama_running(self) -> bool:
        """Checks health and attempts to start the Ollama background process if down.

        This handles Windows-specific paths (e.g. User AppData) as well as the
        global command path.

        Returns:
            True if Ollama is running and healthy, False if it failed to start.
        """
        if self.is_healthy():
            logger.info("Ollama service is already running and healthy.")
            return True

        logger.info("Ollama is not running. Attempting to start the service...")

        # Formulate possible command paths
        commands_to_try = []

        if os.name == "nt":  # Windows
            # Standard user-level install path
            appdata = os.environ.get("LOCALAPPDATA", "")
            user_path = os.path.join(appdata, "Programs", "Ollama", "ollama.exe")
            if os.path.exists(user_path):
                commands_to_try.append([user_path, "serve"])

        # Fallback to PATH-based execution
        commands_to_try.append(["ollama", "serve"])

        started = False
        for cmd in commands_to_try:
            try:
                # Start process in background without blocking
                if os.name == "nt":
                    # On Windows, use creation flags to hide the window
                    # and prevent console takeover
                    # CREATE_NO_WINDOW = 0x08000000
                    subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=0x08000000,
                    )
                else:
                    subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                started = True
                cmd_str = " ".join(cmd)
                logger.info(f"Launched Ollama server process: {cmd_str}")
                break
            except (FileNotFoundError, subprocess.SubprocessError) as e:
                cmd_str = " ".join(cmd)
                logger.debug(f"Failed to start Ollama with command {cmd_str}: {e}")
                continue

        if not started:
            logger.error("Could not find or run the Ollama executable on this system.")
            return False

        # Poll health endpoint for up to 15 seconds
        logger.info("Waiting for Ollama server to initialize...")
        for attempt in range(15):
            time.sleep(1)
            if self.is_healthy():
                logger.info("Ollama server started successfully and is responsive.")
                return True
            logger.debug(f"Ping attempt {attempt + 1}/15 failed...")

        logger.error(
            "Ollama server failed to become healthy within the timeout period."
        )
        return False

    def get_available_models(self) -> list[str]:
        """Fetches the names of all models installed in the local Ollama instance.

        Returns:
            A list of model name strings (e.g. ['qwen2.5-coder:7b']).
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return models
            return []
        except requests.RequestException as e:
            logger.error(f"Failed to fetch local Ollama models: {e}")
            return []

    def validate_model(self, model_name: str) -> bool:
        """Checks if a specific model is available in the local Ollama instance.

        Args:
            model_name: Name of the model to validate.

        Returns:
            True if the model exists locally, False otherwise.
        """
        available = self.get_available_models()
        return model_name in available

    def _retry_request(
        self,
        request_fn: Any,
        max_retries: int = MAX_RETRIES,
    ) -> requests.Response:
        """Executes an HTTP request with exponential backoff retry logic.

        Args:
            request_fn: A callable that returns a requests.Response.
            max_retries: Maximum number of retry attempts.

        Returns:
            The successful HTTP response.

        Raises:
            RuntimeError: If all retry attempts fail.
        """
        last_exception: Exception | None = None
        backoff = INITIAL_BACKOFF_SECONDS

        for attempt in range(1, max_retries + 1):
            try:
                response = request_fn()
                if response.status_code == 200:
                    return response
                else:
                    err_msg = (
                        f"Ollama API returned status {response.status_code}: "
                        f"{response.text}"
                    )
                    last_exception = RuntimeError(err_msg)
                    logger.warning(f"Attempt {attempt}/{max_retries} failed: {err_msg}")
            except requests.RequestException as e:
                last_exception = e
                logger.warning(f"Attempt {attempt}/{max_retries} connection error: {e}")

            if attempt < max_retries:
                logger.info(f"Retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= BACKOFF_MULTIPLIER

        err_msg = (
            f"All {max_retries} attempts failed for Ollama request: {last_exception}"
        )
        logger.error(err_msg)
        raise RuntimeError(err_msg) from last_exception

    def generate_completion(
        self,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generates a text completion with retry logic and exponential backoff.

        Args:
            model: The name of the model to use.
            prompt: The input prompt.
            system_prompt: Optional system prompt to instruct the model.
            options: Optional inference options (e.g., temperature, seed).

        Returns:
            The generated response string.

        Raises:
            RuntimeError: If the request to Ollama fails after retries.
        """
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if options:
            payload["options"] = options

        logger.info(f"Sending generation request to model '{model}'")

        def _do_request() -> requests.Response:
            return requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=180
            )

        try:
            response = self._retry_request(_do_request)
            return str(response.json().get("response", ""))
        except RuntimeError:
            raise
        except Exception as e:
            err_msg = f"Failed to connect to Ollama server at {self.base_url}: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e

    def generate_chat_response(
        self,
        model: str,
        messages: list[dict[str, str]],
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generates a chat completion with retry logic and exponential backoff.

        Args:
            model: The name of the model to use.
            messages: A list of dicts with 'role' and 'content' keys.
            options: Optional inference options.

        Returns:
            The content of the assistant's reply.

        Raises:
            RuntimeError: If the request to Ollama fails after retries.
        """
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options

        msg_count = len(messages)
        logger.info(
            f"Sending chat request to model '{model}' with {msg_count} messages"
        )

        def _do_request() -> requests.Response:
            return requests.post(f"{self.base_url}/api/chat", json=payload, timeout=180)

        try:
            response = self._retry_request(_do_request)
            return str(response.json().get("message", {}).get("content", ""))
        except RuntimeError:
            raise
        except Exception as e:
            err_msg = f"Failed to connect to Ollama server at {self.base_url}: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e
