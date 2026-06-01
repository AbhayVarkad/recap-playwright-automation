"""Bottom toolbar scan group workflow (refactored from test2.py)."""

import path_setup  # noqa: F401, E402

import asyncio
import logging

from playwright.async_api import async_playwright

from pages.bottom_toolbar_page import BottomToolbarPage
from pages.viewer_page import ViewerPage
from utils.browser import new_viewer_context
from utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


async def run_scan_group_toolbar_flow() -> None:
    """Execute the bottom toolbar scan group workflow."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await new_viewer_context(browser)
        page = await context.new_page()

        viewer = ViewerPage(page)
        bottom_toolbar = BottomToolbarPage(page)

        await viewer.open_and_refresh_for_bottom_toolbar()
        await bottom_toolbar.complete_scan_group_workflow()

        await browser.close()


async def main() -> None:
    setup_logging()
    await run_scan_group_toolbar_flow()


if __name__ == "__main__":
    asyncio.run(main())
