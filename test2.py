import asyncio
import re

from playwright.async_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from utils.browser import new_viewer_context

VIEWER_URL = (
    "https://cdn.recap-staging.autodesk.com/viewer/current/index.html?"
    "file=https://rs-asrd-nas.ads.autodesk.com/datasets/rctp_v1.0/"
    "AutodeskReCapSampleProject_realview/AutodeskReCapSampleProject.rcp"
    "&env=local&src=local"
)
DEFAULT_TIMEOUT_MS = 120_000
TUTORIAL_APPEAR_TIMEOUT_MS = 15_000
TUTORIAL_STEP_TIMEOUT_MS = 10_000
TUTORIAL_CANDIDATE_TIMEOUT_MS = 1_500
TUTORIAL_CLICK_RETRIES = 3
TUTORIAL_RETRY_DELAY_MS = 400
TUTORIAL_STEP_TRANSITION_MS = 500

SCAN_GROUP_SELECTOR = "#recap-pcv-scan-group"
SCAN_GROUP_DONE_SELECTOR = "#recap-pcv-scan-group-done"
SCAN_GROUP_MODAL_OVERLAY = '[data-testid="modal-overlay"]'
SCAN_GROUP_NEXT_CLASS_SELECTOR = "button.recap-scan-group-step1"
SCAN_GROUP_OK_CLASS_SELECTOR = "button.recap-scan-group-step2"
NEXT_BUTTON_TEXT = re.compile(r"^\s*Next\s*$", re.I)
OK_BUTTON_TEXT = re.compile(r"^\s*OK\s*$", re.I)


async def wait_for_viewer_ready(page) -> None:
    """Wait until the viewer toolbar is ready."""
    await page.wait_for_load_state("load", timeout=DEFAULT_TIMEOUT_MS)
    await page.wait_for_load_state("networkidle", timeout=DEFAULT_TIMEOUT_MS)
    await page.wait_for_selector(SCAN_GROUP_SELECTOR, state="visible", timeout=DEFAULT_TIMEOUT_MS)


async def click_bottom_scan_group(page) -> None:
    """Click the Scan Group control in the bottom toolbar."""
    scan_group = page.locator(SCAN_GROUP_SELECTOR)
    await scan_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await scan_group.click()


def _tutorial_next_locators(page):
    """Return ordered Next-button locators (modal-scoped first)."""
    modal = page.locator(SCAN_GROUP_MODAL_OVERLAY)
    return [
        ("modal-overlay Next", modal.locator("button", has_text=NEXT_BUTTON_TEXT)),
        (
            "class step1 + Next text",
            page.locator(SCAN_GROUP_NEXT_CLASS_SELECTOR, has_text=NEXT_BUTTON_TEXT),
        ),
        ("class step1", page.locator(SCAN_GROUP_NEXT_CLASS_SELECTOR)),
    ]


def _tutorial_ok_locators(page):
    """Return ordered OK-button locators (modal-scoped first)."""
    modal = page.locator(SCAN_GROUP_MODAL_OVERLAY)
    return [
        ("modal-overlay OK", modal.locator("button", has_text=OK_BUTTON_TEXT)),
        (
            "class step2 + OK text",
            page.locator(SCAN_GROUP_OK_CLASS_SELECTOR, has_text=OK_BUTTON_TEXT),
        ),
        ("class step2", page.locator(SCAN_GROUP_OK_CLASS_SELECTOR)),
    ]


async def _find_visible_tutorial_button(
    candidates, label: str, timeout_ms: int = TUTORIAL_CANDIDATE_TIMEOUT_MS
):
    """Pick the first visible, enabled candidate locator."""
    for name, locator in candidates:
        try:
            await locator.first.wait_for(state="visible", timeout=timeout_ms)
        except PlaywrightTimeoutError:
            continue
        button = locator.first
        if not await button.is_enabled():
            print(f"--- Tutorial: {label} candidate '{name}' visible but disabled ---")
            continue
        print(f"--- Tutorial: using {label} locator '{name}' ---")
        return button
    return None


async def _wait_for_tutorial_modal(page) -> bool:
    """Wait for modal overlay or a Next button; return False if neither appears."""
    modal = page.locator(SCAN_GROUP_MODAL_OVERLAY)
    deadline = TUTORIAL_APPEAR_TIMEOUT_MS
    try:
        await modal.first.wait_for(state="visible", timeout=deadline)
        print("--- Tutorial: modal overlay visible ---")
        return True
    except PlaywrightTimeoutError:
        pass

    for name, locator in _tutorial_next_locators(page):
        try:
            await locator.first.wait_for(
                state="visible", timeout=TUTORIAL_CANDIDATE_TIMEOUT_MS
            )
            print(f"--- Tutorial: modal detected via '{name}' ---")
            return True
        except PlaywrightTimeoutError:
            continue

    print("--- Tutorial: no modal detected; skipping dismissal ---")
    return False


async def _click_tutorial_button(page, candidates, label: str) -> bool:
    """Click a tutorial button after it is visible and enabled, with short retries."""
    for attempt in range(1, TUTORIAL_CLICK_RETRIES + 1):
        button = await _find_visible_tutorial_button(candidates, label)
        if button is None:
            print(
                f"--- Tutorial: no visible enabled {label} button "
                f"(attempt {attempt}/{TUTORIAL_CLICK_RETRIES}) ---"
            )
            if attempt < TUTORIAL_CLICK_RETRIES:
                await page.wait_for_timeout(TUTORIAL_RETRY_DELAY_MS)
            continue

        try:
            await button.scroll_into_view_if_needed(timeout=TUTORIAL_STEP_TIMEOUT_MS)
            await button.wait_for(state="visible", timeout=TUTORIAL_STEP_TIMEOUT_MS)
            if not await button.is_enabled():
                raise PlaywrightTimeoutError(f"{label} button is not enabled")

            use_force = attempt == TUTORIAL_CLICK_RETRIES
            await button.click(timeout=TUTORIAL_STEP_TIMEOUT_MS, force=use_force)
            print(
                f"--- Tutorial: clicked {label} (attempt {attempt}"
                f"{', force=True' if use_force else ''}) ---"
            )
            return True
        except (PlaywrightTimeoutError, PlaywrightError) as exc:
            print(
                f"--- Tutorial: {label} click attempt {attempt}/"
                f"{TUTORIAL_CLICK_RETRIES} failed: {exc} ---"
            )
            if attempt < TUTORIAL_CLICK_RETRIES:
                await page.wait_for_timeout(TUTORIAL_RETRY_DELAY_MS)

    return False


async def dismiss_scan_group_tutorial(page) -> None:
    """Close the first-run Scan Groups modal so Done is reachable."""
    print("--- Tutorial: waiting for Scan Groups modal ---")
    if not await _wait_for_tutorial_modal(page):
        return

    if not await _click_tutorial_button(page, _tutorial_next_locators(page), "Next"):
        print("--- Tutorial: could not click Next; leaving modal open ---")
        return

    await page.wait_for_timeout(TUTORIAL_STEP_TRANSITION_MS)
    print("--- Tutorial: waiting for OK button ---")
    if not await _click_tutorial_button(page, _tutorial_ok_locators(page), "OK"):
        print("--- Tutorial: could not click OK; leaving modal open ---")
        return

    modal_overlay = page.locator(SCAN_GROUP_MODAL_OVERLAY)
    try:
        await modal_overlay.wait_for(state="hidden", timeout=TUTORIAL_STEP_TIMEOUT_MS)
        print("--- Tutorial: modal dismissed ---")
    except PlaywrightTimeoutError:
        print("--- Tutorial: modal overlay still visible after OK ---")


async def click_scan_group_done(page) -> None:
    """Click Done after the bottom toolbar control appears."""
    await page.wait_for_selector(
        SCAN_GROUP_DONE_SELECTOR,
        state="visible",
        timeout=DEFAULT_TIMEOUT_MS,
    )
    done_button = page.locator(SCAN_GROUP_DONE_SELECTOR)
    await done_button.click()


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await new_viewer_context(browser)
        page = await context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MS)

        print("--- Local network access pre-granted (no Allow prompt) ---")
        print("--- Launching Recap viewer ---")
        await page.goto(VIEWER_URL, wait_until="domcontentloaded")

        print("--- Waiting for initial viewer to be fully loaded ---")
        await wait_for_viewer_ready(page)

        print("--- Refreshing viewer ---")
        await page.reload(wait_until="domcontentloaded")

        print("--- Waiting for viewer after refresh ---")
        await wait_for_viewer_ready(page)

        print(f"--- Clicking bottom scan group ({SCAN_GROUP_SELECTOR}) ---")
        await click_bottom_scan_group(page)

        print("--- Dismissing Scan Groups tutorial modal (Next, OK) ---")
        await dismiss_scan_group_tutorial(page)

        print(f"--- Clicking Done ({SCAN_GROUP_DONE_SELECTOR}) ---")
        await click_scan_group_done(page)

        print("--- Scan group workflow completed ---")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
