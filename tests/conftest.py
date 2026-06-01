"""Pytest-only hooks (not used when you run flow scripts directly with python tests/...)."""

import pytest

from utils.logging_config import setup_logging


@pytest.fixture(scope="session", autouse=True)
def _configure_logging() -> None:
    """Show INFO logs in the terminal during pytest / Allure runs."""
    setup_logging()
