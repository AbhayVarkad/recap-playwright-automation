"""Viewer page object for launching and waiting on the Recap viewer."""

from config.selectors import BOTTOM_SCAN_GROUP, SCANS_ROOT, SCANS_TREE_ITEM
from config.settings import DEFAULT_TIMEOUT_MS, VIEWER_URL
from pages.base_page import BasePage


class ViewerPage(BasePage):
    """Actions for loading, refreshing, and waiting on the Recap viewer."""

    async def open(self, url: str = VIEWER_URL) -> None:
        """Navigate to the Recap viewer URL."""
        self.logger.info("Launching Recap viewer")
        await self.page.goto(url, wait_until="domcontentloaded")

    async def reload(self) -> None:
        """Reload the viewer page."""
        self.logger.info("Refreshing viewer")
        await self.page.reload(wait_until="domcontentloaded")

    async def wait_for_common_load(self) -> None:
        """Wait for the document load event.

        networkidle is intentionally omitted: the Recap viewer keeps long-lived
        connections open and may never reach idle, which leads to long hangs or
        flaky "page closed" errors during wait_for_load_state.
        """
        await self.page.wait_for_load_state("load", timeout=DEFAULT_TIMEOUT_MS)

    async def wait_for_project_browser_ready(self) -> None:
        """Wait until the project browser scan tree is visible."""
        self.logger.info("Waiting for project browser to be ready")
        await self.wait_for_common_load()
        await self.page.wait_for_selector(SCANS_ROOT, state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await self.page.wait_for_selector(
            SCANS_TREE_ITEM,
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )

    async def wait_for_bottom_toolbar_ready(self) -> None:
        """Wait until the bottom toolbar scan group control is visible."""
        self.logger.info("Waiting for bottom toolbar to be ready")
        await self.wait_for_common_load()
        await self.page.wait_for_selector(
            BOTTOM_SCAN_GROUP,
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )

    async def open_and_refresh_for_project_browser(self, url: str = VIEWER_URL) -> None:
        """Open viewer, wait, refresh, and wait again (project browser flow)."""
        await self.open(url)
        self.logger.info("Waiting for initial viewer to be fully loaded")
        await self.wait_for_project_browser_ready()
        await self.reload()
        self.logger.info("Waiting for viewer after refresh")
        await self.wait_for_project_browser_ready()

    async def open_and_refresh_for_bottom_toolbar(self, url: str = VIEWER_URL) -> None:
        """Open viewer, wait, refresh, and wait again (bottom toolbar flow)."""
        await self.open(url)
        self.logger.info("Waiting for initial viewer to be fully loaded")
        await self.wait_for_bottom_toolbar_ready()
        await self.reload()
        self.logger.info("Waiting for viewer after refresh")
        await self.wait_for_bottom_toolbar_ready()
