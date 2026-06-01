"""Simple console logging for tests and scripts."""

import logging

# Example line:  14:30:01 [INFO] ViewerPage: Launching Recap viewer
_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_TIME_FORMAT = "%H:%M:%S"


def setup_logging() -> None:
    """Show INFO-level messages in the terminal. Call once when a run starts."""
    logging.basicConfig(
        level=logging.INFO,
        format=_FORMAT,
        datefmt=_TIME_FORMAT,
        force=True,
    )
