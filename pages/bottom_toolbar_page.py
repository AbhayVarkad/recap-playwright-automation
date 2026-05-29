"""Bottom toolbar page object for scan group workflow."""

import re
from typing import TYPE_CHECKING

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from config.selectors import (
    BOTTOM_SCAN_GROUP,
    BOTTOM_SCAN_GROUP_DONE,
    SCAN_GROUP_MODAL_OVERLAY,
    SCAN_GROUP_TUTORIAL_NEXT_CLASS,
    SCAN_GROUP_TUTORIAL_OK_CLASS,
)
from config.settings import (
    DEFAULT_TIMEOUT_MS,
    TUTORIAL_APPEAR_TIMEOUT_MS,
    TUTORIAL_CANDIDATE_TIMEOUT_MS,
    TUTORIAL_CLICK_RETRIES,
    TUTORIAL_RETRY_DELAY_MS,
    TUTORIAL_STEP_TIMEOUT_MS,
    TUTORIAL_STEP_TRANSITION_MS,
)
from pages.base_page import BasePage

if TYPE_CHECKING:
    from playwright.async_api import Locator, Page

_NEXT_BUTTON_TEXT = re.compile(r"^\s*Next\s*$", re.I)
_OK_BUTTON_TEXT = re.compile(r"^\s*OK\s*$", re.I)


class BottomToolbarPage(BasePage):
    """Actions for the bottom toolbar scan group controls."""

    async def click_scan_group(self) -> None:
        """Click the Scan Group control in the bottom toolbar."""
        self.logger.info("Clicking bottom scan group (%s)", BOTTOM_SCAN_GROUP)
        scan_group = self.page.locator(BOTTOM_SCAN_GROUP)
        await scan_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await scan_group.click()

    def _tutorial_next_locators(self) -> list[tuple[str, "Locator"]]:
        """Return ordered Next-button locators (modal-scoped first)."""
        modal = self.page.locator(SCAN_GROUP_MODAL_OVERLAY)
        return [
            ("modal-overlay Next", modal.locator("button", has_text=_NEXT_BUTTON_TEXT)),
            (
                "class step1 + Next text",
                self.page.locator(
                    SCAN_GROUP_TUTORIAL_NEXT_CLASS, has_text=_NEXT_BUTTON_TEXT
                ),
            ),
            ("class step1", self.page.locator(SCAN_GROUP_TUTORIAL_NEXT_CLASS)),
        ]

    def _tutorial_ok_locators(self) -> list[tuple[str, "Locator"]]:
        """Return ordered OK-button locators (modal-scoped first)."""
        modal = self.page.locator(SCAN_GROUP_MODAL_OVERLAY)
        return [
            ("modal-overlay OK", modal.locator("button", has_text=_OK_BUTTON_TEXT)),
            (
                "class step2 + OK text",
                self.page.locator(SCAN_GROUP_TUTORIAL_OK_CLASS, has_text=_OK_BUTTON_TEXT),
            ),
            ("class step2", self.page.locator(SCAN_GROUP_TUTORIAL_OK_CLASS)),
        ]

    async def _find_visible_tutorial_button(
        self, candidates: list[tuple[str, "Locator"]], label: str
    ) -> "Locator | None":
        """Pick the first visible, enabled candidate locator."""
        for name, locator in candidates:
            try:
                await locator.first.wait_for(
                    state="visible", timeout=TUTORIAL_CANDIDATE_TIMEOUT_MS
                )
            except PlaywrightTimeoutError:
                continue
            button = locator.first
            if not await button.is_enabled():
                self.logger.warning(
                    "Tutorial %s candidate '%s' visible but disabled", label, name
                )
                continue
            self.logger.info("Tutorial: using %s locator '%s'", label, name)
            return button
        return None

    async def _wait_for_tutorial_modal(self) -> bool:
        """Wait for modal overlay or a Next button; return False if neither appears."""
        modal = self.page.locator(SCAN_GROUP_MODAL_OVERLAY)
        try:
            await modal.first.wait_for(state="visible", timeout=TUTORIAL_APPEAR_TIMEOUT_MS)
            self.logger.info("Tutorial: modal overlay visible")
            return True
        except PlaywrightTimeoutError:
            pass

        for name, locator in self._tutorial_next_locators():
            try:
                await locator.first.wait_for(
                    state="visible", timeout=TUTORIAL_CANDIDATE_TIMEOUT_MS
                )
                self.logger.info("Tutorial: modal detected via '%s'", name)
                return True
            except PlaywrightTimeoutError:
                continue

        self.logger.info("Tutorial: no modal detected; skipping dismissal")
        return False

    async def _click_tutorial_button(
        self, candidates: list[tuple[str, "Locator"]], label: str
    ) -> bool:
        """Click a tutorial button after it is visible and enabled, with short retries."""
        for attempt in range(1, TUTORIAL_CLICK_RETRIES + 1):
            button = await self._find_visible_tutorial_button(candidates, label)
            if button is None:
                self.logger.warning(
                    "Tutorial: no visible enabled %s button (attempt %d/%d)",
                    label,
                    attempt,
                    TUTORIAL_CLICK_RETRIES,
                )
                if attempt < TUTORIAL_CLICK_RETRIES:
                    await self.page.wait_for_timeout(TUTORIAL_RETRY_DELAY_MS)
                continue

            try:
                await button.scroll_into_view_if_needed(timeout=TUTORIAL_STEP_TIMEOUT_MS)
                await button.wait_for(state="visible", timeout=TUTORIAL_STEP_TIMEOUT_MS)
                if not await button.is_enabled():
                    raise PlaywrightTimeoutError(f"{label} button is not enabled")

                use_force = attempt == TUTORIAL_CLICK_RETRIES
                await button.click(timeout=TUTORIAL_STEP_TIMEOUT_MS, force=use_force)
                self.logger.info(
                    "Tutorial: clicked %s (attempt %d%s)",
                    label,
                    attempt,
                    ", force=True" if use_force else "",
                )
                return True
            except (PlaywrightTimeoutError, PlaywrightError) as exc:
                self.logger.warning(
                    "Tutorial: %s click attempt %d/%d failed: %s",
                    label,
                    attempt,
                    TUTORIAL_CLICK_RETRIES,
                    exc,
                )
                if attempt < TUTORIAL_CLICK_RETRIES:
                    await self.page.wait_for_timeout(TUTORIAL_RETRY_DELAY_MS)

        return False

    async def dismiss_scan_group_tutorial(self) -> None:
        """Close the first-run Scan Groups modal so Done is reachable."""
        self.logger.info("Dismissing Scan Groups tutorial modal (Next, OK)")
        if not await self._wait_for_tutorial_modal():
            return

        if not await self._click_tutorial_button(self._tutorial_next_locators(), "Next"):
            raise RuntimeError("Could not click Next on Scan Groups tutorial modal")

        await self.page.wait_for_timeout(TUTORIAL_STEP_TRANSITION_MS)

        if not await self._click_tutorial_button(self._tutorial_ok_locators(), "OK"):
            raise RuntimeError("Could not click OK on Scan Groups tutorial modal")

        modal_overlay = self.page.locator(SCAN_GROUP_MODAL_OVERLAY)
        try:
            await modal_overlay.wait_for(state="hidden", timeout=TUTORIAL_STEP_TIMEOUT_MS)
            self.logger.info("Tutorial: modal dismissed")
        except PlaywrightTimeoutError:
            self.logger.warning("Tutorial: modal overlay still visible after OK")

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
