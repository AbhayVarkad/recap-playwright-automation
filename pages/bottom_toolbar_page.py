"""Bottom toolbar page object for scan group workflow."""

from config.selectors import (
    BOTTOM_SCAN_GROUP,
    BOTTOM_SCAN_GROUP_DONE,
    SCAN_GROUP_TUTORIAL_NEXT,
    SCAN_GROUP_TUTORIAL_OK,
)
from config.settings import DEFAULT_TIMEOUT_MS
from pages.base_page import BasePage


class BottomToolbarPage(BasePage):
    """Actions for the bottom toolbar scan group controls."""

    async def click_scan_group(self) -> None:
        """Click the Scan Group control in the bottom toolbar."""
        self.logger.info("Clicking bottom scan group (%s)", BOTTOM_SCAN_GROUP)
        scan_group = self.page.locator(BOTTOM_SCAN_GROUP)
        await scan_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await scan_group.click()

    async def dismiss_scan_group_tutorial(self) -> None:
        """Close the first-run Scan Groups modal so Done is reachable."""
        self.logger.info("Dismissing Scan Groups tutorial modal (Next, OK)")
        next_button = self.page.locator(SCAN_GROUP_TUTORIAL_NEXT)
        if await next_button.count() == 0:
            return
        if not await next_button.is_visible():
            return
        await next_button.click()

        ok_button = self.page.locator(SCAN_GROUP_TUTORIAL_OK)
        await ok_button.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await ok_button.click()

    async def click_scan_group_done(self) -> None:
        """Click Done after the bottom toolbar control appears."""
        self.logger.info("Clicking Done (%s)", BOTTOM_SCAN_GROUP_DONE)
        await self.page.wait_for_selector(
            BOTTOM_SCAN_GROUP_DONE,
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )
        done_button = self.page.locator(BOTTOM_SCAN_GROUP_DONE)
        await done_button.click()

    async def complete_scan_group_workflow(self) -> None:
        """Run the full bottom toolbar scan group flow."""
        await self.click_scan_group()
        await self.dismiss_scan_group_tutorial()
        await self.click_scan_group_done()
        self.logger.info("Scan group workflow completed")
