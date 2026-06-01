"""
End-to-end check of the Project Browser search box.

For each tab (Scans, Annotations, View States, Extracted Features) we:
  1. Read item names from the tree
  2. Walk them in reverse order (LIFO) — same order the original script used
  3. Search for each name and confirm it appears in the tree
"""

import path_setup  # noqa: F401, E402

import asyncio
import logging
from collections.abc import Awaitable, Callable

from playwright.async_api import Page, async_playwright

from config.selectors import (
    ANNOTATIONS_TAB_PAGE,
    EXTRACTED_FEATURES_TAB_PAGE,
    SCANS_TAB_PAGE,
    VIEW_STATES_TAB_PAGE,
)
from config.settings import STACK_PROCESS_DELAY_MS
from pages.project_browser_page import ProjectBrowserPage
from pages.viewer_page import ViewerPage
from utils.browser import new_viewer_context
from utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

MIN_SCAN_COUNT = 2
SCAN_SAMPLE_SIZE = 2


def _section(title: str) -> None:
    """Print a visible section header in the console."""
    print(f"\n--- {title} ---")


async def _pause_between_stack_items(page: Page) -> None:
    await page.wait_for_timeout(STACK_PROCESS_DELAY_MS)


async def _walk_names_lifo(page: Page, names: list[str], what: str) -> None:
    """Process names last-to-first, with a short pause between each (mirrors manual QA steps)."""
    _section(f"Processing {what} (LIFO — last name first)")
    for name in reversed(names):
        logger.info("Processing %s: %s", what.rstrip("s"), name)
        print(f"  → {name}")
        await _pause_between_stack_items(page)


async def _collect_and_report(kind: str, names: list[str]) -> None:
    """Log every name we picked up from the tree."""
    _section(f"Fetching {kind}")
    for name in names:
        logger.info("Stored %s: %s", kind.rstrip("s"), name)
        print(f"  stored: {name}")
    print(f"  ({len(names)} total)\n")


async def _verify_search_hits(
    browser: ProjectBrowserPage,
    page: Page,
    *,
    tab_label: str,
    names: list[str],
    stack_label: str,
    open_tab: Callable[[], Awaitable[None]],
    tab_page_selector: str,
    use_feature_inputs: bool = False,
) -> tuple[int, int]:
    """Run the LIFO walk, then search for each name in the Project Browser."""
    await _collect_and_report(stack_label, names)
    await _walk_names_lifo(page, names, stack_label)
    return await browser.verify_names_via_search(
        tab_label,
        names,
        open_tab,
        tab_page_selector,
        use_feature_inputs=use_feature_inputs,
    )


def _print_summary(
    scan: tuple[int, int],
    annotations: tuple[int, int],
    view_states: tuple[int, int],
    features: tuple[int, int],
) -> tuple[int, int]:
    scan_ok, scan_n = scan
    ann_ok, ann_n = annotations
    vs_ok, vs_n = view_states
    feat_ok, feat_n = features

    passed = scan_ok + ann_ok + vs_ok + feat_ok
    total = scan_n + ann_n + vs_n + feat_n

    _section("Search verification summary")
    print(f"  Scans:              {scan_ok}/{scan_n}")
    print(f"  Annotations:        {ann_ok}/{ann_n}")
    print(f"  View States:        {vs_ok}/{vs_n}")
    print(f"  Extracted Features: {feat_ok}/{feat_n}")
    print(f"  Overall:            {passed}/{total}")

    logger.info("Overall search verification: %d/%d passed", passed, total)
    return passed, total


async def run_project_browser_flow() -> tuple[int, int]:
    """Open the viewer, exercise each Project Browser tab, return (passed, total)."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await new_viewer_context(browser)
        page = await context.new_page()

        viewer = ViewerPage(page)
        project_browser = ProjectBrowserPage(page)

        # Load the viewer twice so panels settle after refresh (existing behaviour).
        await viewer.open_and_refresh_for_project_browser()

        # --- Scans (we only check the first two names) ---
        await project_browser.click_scan_group()
        all_scans = await project_browser.collect_scan_names()

        if len(all_scans) < MIN_SCAN_COUNT:
            raise RuntimeError(
                f"Need at least {MIN_SCAN_COUNT} scans under the scan group; "
                f"got {len(all_scans)}: {all_scans}"
            )

        scans_to_check = all_scans[:SCAN_SAMPLE_SIZE]
        scan_results = await _verify_search_hits(
            project_browser,
            page,
            tab_label="Scans",
            names=scans_to_check,
            stack_label="scans",
            open_tab=project_browser.click_scan_group,
            tab_page_selector=SCANS_TAB_PAGE,
        )

        # --- Annotations ---
        await project_browser.open_annotations_tab()
        annotation_names = await project_browser.collect_annotation_names()
        annotation_results = await _verify_search_hits(
            project_browser,
            page,
            tab_label="Annotations",
            names=annotation_names,
            stack_label="annotations",
            open_tab=project_browser.open_annotations_tab,
            tab_page_selector=ANNOTATIONS_TAB_PAGE,
        )

        # --- View States ---
        await project_browser.open_view_states_tab()
        await project_browser.click_view_states_group()
        view_state_names = await project_browser.collect_view_state_names()
        view_state_results = await _verify_search_hits(
            project_browser,
            page,
            tab_label="View States",
            names=view_state_names,
            stack_label="view states",
            open_tab=project_browser.prepare_view_states_tab,
            tab_page_selector=VIEW_STATES_TAB_PAGE,
        )

        # --- Extracted Features ---
        await project_browser.open_extracted_features_tab()
        await project_browser.click_extracted_features_group()
        feature_names = await project_browser.collect_extracted_feature_names()
        feature_results = await _verify_search_hits(
            project_browser,
            page,
            tab_label="Extracted Features",
            names=feature_names,
            stack_label="extracted features",
            open_tab=project_browser.prepare_extracted_features_tab,
            tab_page_selector=EXTRACTED_FEATURES_TAB_PAGE,
            use_feature_inputs=True,
        )

        passed, total = _print_summary(
            scan_results, annotation_results, view_state_results, feature_results
        )

        _section("Refreshing page after all checks")
        await viewer.reload()
        await viewer.wait_for_project_browser_ready()

        await browser.close()
        return passed, total


async def main() -> None:
    setup_logging()
    passed, total = await run_project_browser_flow()
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
