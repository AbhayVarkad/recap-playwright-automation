"""Base page object with shared Playwright helpers."""

import logging
from typing import TYPE_CHECKING

from config.settings import DEFAULT_TIMEOUT_MS

if TYPE_CHECKING:
    from playwright.async_api import Page

logger = logging.getLogger(__name__)


class BasePage:
    """Common page wrapper used by all Recap viewer page objects."""

    def __init__(self, page: "Page") -> None:
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT_MS)
        self.logger = logging.getLogger(self.__class__.__name__)
