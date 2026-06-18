"""Chat engine for managing LLM chat conversations and history."""

import pandas as pd

from app.analytics.profiler import DataProfile
from app.services.ollama_service import OllamaService
from app.utils.logger import setup_logger

logger = setup_logger("chat_engine")


class ChatEngine:
    """Manages chat history and generates responses with local LLMs."""

    def __init__(
        self,
        ollama_service: OllamaService,
        model_name: str,
        max_history_turns: int = 10,
    ):
        """Initializes the chat engine.

        Args:
            ollama_service: Configured Ollama service client.
            model_name: The name of the LLM model to use for chat.
            max_history_turns: Max conversation turns (user/assistant pairs)
                               to retain in memory. Defaults to 10.
        """
        self.ollama_service = ollama_service
        self.model_name = model_name
        self.max_history_turns = max_history_turns
        self.history: list[dict[str, str]] = []
        self.execution_logs: list[str] = []

    def add_message(self, role: str, content: str) -> None:
        """Adds a message to history and enforces sliding window size.

        Args:
            role: The role of the sender ('user', 'assistant', or 'system').
            content: The message content.
        """
        self.history.append({"role": role, "content": content})

        # Slide history window in pairs (turns) if it exceeds the limit
        max_messages = self.max_history_turns * 2
        while len(self.history) > max_messages:
            # Check if there is a system message at the beginning
            has_system = len(self.history) > 0 and self.history[0]["role"] == "system"
            if has_system:
                if len(self.history) > 2:
                    # Remove the oldest user-assistant pair (index 1 and 2)
                    self.history.pop(1)
                    self.history.pop(1)
                else:
                    self.history.pop(1)
            else:
                self.history = self.history[2:]

    def clear_history(self) -> None:
        """Clears conversation memory and execution logs."""
        self.history = []
        self.execution_logs = []
        logger.info("Chat history cleared.")

    def log_execution(self, message: str) -> None:
        """Appends a message to the execution log list.

        Args:
            message: Execution step description (e.g. 'Executed SQL: ...').
        """
        self.execution_logs.append(message)
        logger.info(f"Execution Log: {message}")

    def generate_response(
        self,
        user_message: str,
        df: pd.DataFrame | None = None,
        profile: DataProfile | None = None,
    ) -> str:
        """Generates a reply for user message, injecting dataset context.

        Args:
            user_message: Message text from the user.
            df: Optional Pandas DataFrame currently loaded.
            profile: Optional DataProfile of the loaded DataFrame.

        Returns:
            The generated reply from the local LLM.
        """
        self.log_execution("Received user chat query.")

        # Construct system prompt with dataset context if available
        system_prompt = (
            "You are a Senior Data Scientist and AI assistant. Your goal is to help "
            "the user analyze their dataset. Speak clearly, explain your reasoning, "
            "and suggest logical next steps."
        )

        if df is not None and profile is not None:
            # Create schema representation
            schema_lines = []
            for col, col_prof in profile.column_profiles.items():
                schema_lines.append(
                    f"- {col} (Type: {col_prof.dtype}, Unique: {col_prof.num_unique}, "
                    f"Missing: {col_prof.missing_count})"
                )
            schema_desc = "\n".join(schema_lines)

            system_prompt += (
                f"\n\nThe user has uploaded a dataset containing {profile.num_rows} "
                f"rows and {profile.num_cols} columns.\n"
                f"Here is the table schema ('data_table'):\n{schema_desc}\n\n"
                "If the user asks questions about this data, answer them based "
                "on the schema, or suggest SQL queries they can run in the SQL "
                "Studio. Do not hallucinate."
            )
            self.log_execution("Loaded active dataset schema into chat system prompt.")

        # Compile chat messages including system prompt
        messages: list[dict[str, str]] = []
        messages.append({"role": "system", "content": system_prompt})

        # Add history messages
        messages.extend(self.history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        try:
            self.log_execution(f"Calling model '{self.model_name}' API...")
            reply = self.ollama_service.generate_chat_response(
                model=self.model_name, messages=messages
            )

            # Record turn in history
            self.add_message("user", user_message)
            self.add_message("assistant", reply)

            self.log_execution("Response generated and conversation history updated.")
            return reply
        except Exception as e:
            err_msg = f"Failed to generate response: {e}"
            self.log_execution(f"Error during generation: {e}")
            logger.error(err_msg)
            raise RuntimeError(err_msg) from e
