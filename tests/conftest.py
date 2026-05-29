"""Pytest hooks for Recap Allure tests."""

import pytest

from utils.logging_config import setup_logging


@pytest.fixture(scope="session", autouse=True)
def _configure_logging() -> None:
    setup_logging()
