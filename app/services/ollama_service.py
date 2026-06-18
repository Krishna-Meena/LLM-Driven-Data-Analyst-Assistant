"""Service layer for interacting with local Ollama LLM models."""

import os
import subprocess
import time
from typing import Any

import requests

from app.utils.logger import setup_logger

logger = setup_logger("ollama_service")

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


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
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
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

        # Poll health endpoint for up to 10 seconds
        logger.info("Waiting for Ollama server to initialize...")
        for attempt in range(10):
            time.sleep(1)
            if self.is_healthy():
                logger.info("Ollama server started successfully and is responsive.")
                return True
            logger.debug(f"Ping attempt {attempt + 1}/10 failed...")

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
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return models
            return []
        except requests.RequestException as e:
            logger.error(f"Failed to fetch local Ollama models: {e}")
            return []

    def generate_completion(
        self,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generates a text completion based on a prompt and optional configuration.

        Args:
            model: The name of the model to use.
            prompt: The input prompt.
            system_prompt: Optional system prompt to instruct the model.
            options: Optional inference options (e.g., temperature, seed).

        Returns:
            The generated response string.

        Raises:
            RuntimeError: If the request to Ollama fails.
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

        try:
            logger.info(f"Sending generation request to model '{model}'")
            response = requests.post(
                f"{self.base_url}/api/generate", json=payload, timeout=120
            )
            if response.status_code == 200:
                return str(response.json().get("response", ""))
            else:
                err_msg = (
                    f"Ollama API returned status {response.status_code}: "
                    f"{response.text}"
                )
                logger.error(err_msg)
                raise RuntimeError(err_msg)
        except requests.RequestException as e:
            err_msg = f"Failed to connect to Ollama server at {self.base_url}: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e

    def generate_chat_response(
        self,
        model: str,
        messages: list[dict[str, str]],
        options: dict[str, Any] | None = None,
    ) -> str:
        """Generates a chat completion given a list of messages.

        Args:
            model: The name of the model to use.
            messages: A list of dicts with 'role' and 'content' keys.
            options: Optional inference options.

        Returns:
            The content of the assistant's reply.

        Raises:
            RuntimeError: If the request to Ollama fails.
        """
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options

        try:
            msg_count = len(messages)
            logger.info(
                f"Sending chat request to model '{model}' with {msg_count} messages"
            )
            response = requests.post(
                f"{self.base_url}/api/chat", json=payload, timeout=120
            )
            if response.status_code == 200:
                return str(response.json().get("message", {}).get("content", ""))
            else:
                err_msg = (
                    f"Ollama API returned status {response.status_code}: "
                    f"{response.text}"
                )
                logger.error(err_msg)
                raise RuntimeError(err_msg)
        except requests.RequestException as e:
            err_msg = f"Failed to connect to Ollama server at {self.base_url}: {e}"
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e
