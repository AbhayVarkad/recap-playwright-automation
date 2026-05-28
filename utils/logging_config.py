"""Logging setup for automation scripts."""

import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure readable console logging for test runs."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )
