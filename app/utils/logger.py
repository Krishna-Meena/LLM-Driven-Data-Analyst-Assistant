"""Centralized logging utility for the Local LLM Data Analyst application."""

import logging
from pathlib import Path


def setup_logger(name: str = "data_analyst") -> logging.Logger:
    """Configures and returns a logger with both file and console handlers.

    Args:
        name: Name of the logger. Defaults to 'data_analyst'.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # If the logger already has handlers, don't duplicate them
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    # Define log format
    fmt = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )
    formatter = logging.Formatter(fmt)

    # Console Handler (Stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Prevent propagation to the root logger
    logger.propagate = False

    return logger
