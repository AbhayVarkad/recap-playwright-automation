"""Project browser search verification flow (refactored from test.py)."""

import asyncio
import logging

from playwright.async_api import async_playwright

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


async def process_stack_lifo(page, stack: list[str], label: str) -> None:
    """Pop and log each item from a stack in LIFO order."""
    logger.info("Processing %s stack (LIFO order)", label)
    print(f"--- Processing {label} stack (LIFO order) ---")
    while stack:
        current = stack.pop()
        logger.info("Printing/Processing %s: %s", label.rstrip("s"), current)
        print(f"Printing/Processing {label.rstrip('s')}: {current}")
        await page.wait_for_timeout(STACK_PROCESS_DELAY_MS)


async def run_project_browser_flow() -> tuple[int, int]:
    """Execute the full project browser verification workflow."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await new_viewer_context(browser)
        page = await context.new_page()

        viewer = ViewerPage(page)
        project_browser = ProjectBrowserPage(page)

        await viewer.open_and_refresh_for_project_browser()

        logger.info("Clicking scan group in project browser")
        await project_browser.click_scan_group()

        logger.info("Fetching scans")
        print("--- Fetching scans ---")
        scan_stack: list[str] = []
        scan_names = await project_browser.collect_scan_names()

        if len(scan_names) < 2:
            raise RuntimeError(
                "Expected at least 2 scans after clicking scan group, "
                f"found {len(scan_names)}: {scan_names}"
            )

        for name in scan_names[:2]:
            scan_stack.append(name)
            logger.info("Stored in stack: %s", name)
            print(f"Stored in stack: {name}")

        print(f"\nTotal scans stored in stack: {len(scan_stack)}\n")

        scan_names_for_verify = list(scan_stack)
        await process_stack_lifo(page, scan_stack, "scan")

        scan_passed, scan_total = await project_browser.verify_names_via_search(
            "Scans",
            scan_names_for_verify,
            project_browser.click_scan_group,
            SCANS_TAB_PAGE,
        )

        await project_browser.open_annotations_tab()

        logger.info("Fetching annotations")
        print("--- Fetching annotations ---")
        annotation_stack: list[str] = []
        annotation_names = await project_browser.collect_annotation_names()

        for name in annotation_names:
            annotation_stack.append(name)
            logger.info("Stored annotation in stack: %s", name)
            print(f"Stored annotation in stack: {name}")

        print(f"\nTotal annotations stored in stack: {len(annotation_stack)}\n")

        annotation_names_for_verify = list(annotation_stack)
        await process_stack_lifo(page, annotation_stack, "annotation")

        annotation_passed, annotation_total = await project_browser.verify_names_via_search(
            "Annotations",
            annotation_names_for_verify,
            project_browser.open_annotations_tab,
            ANNOTATIONS_TAB_PAGE,
        )

        await project_browser.open_view_states_tab()
        await project_browser.click_view_states_group()

        logger.info("Fetching view tests")
        print("--- Fetching view tests ---")
        view_test_stack: list[str] = []
        view_test_names = await project_browser.collect_view_state_names()

        for name in view_test_names:
            view_test_stack.append(name)
            logger.info("Stored view test in stack: %s", name)
            print(f"Stored view test in stack: {name}")

        print(f"\nTotal view tests stored in stack: {len(view_test_stack)}\n")

        view_test_names_for_verify = list(view_test_stack)
        await process_stack_lifo(page, view_test_stack, "view test")

        view_test_passed, view_test_total = await project_browser.verify_names_via_search(
            "View States",
            view_test_names_for_verify,
            project_browser.prepare_view_states_tab,
            VIEW_STATES_TAB_PAGE,
        )

        await project_browser.open_extracted_features_tab()
        await project_browser.click_extracted_features_group()

        logger.info("Fetching extracted features")
        print("--- Fetching extracted features ---")
        extracted_features_stack: list[str] = []
        extracted_feature_names = await project_browser.collect_extracted_feature_names()

        for name in extracted_feature_names:
            extracted_features_stack.append(name)
            logger.info("Stored extracted feature in stack: %s", name)
            print(f"Stored extracted feature in stack: {name}")

        print(
            f"\nTotal extracted features stored in stack: {len(extracted_features_stack)}\n"
        )

        extracted_names_for_verify = list(extracted_features_stack)
        await process_stack_lifo(page, extracted_features_stack, "extracted feature")

        extracted_passed, extracted_total = await project_browser.verify_names_via_search(
            "Extracted Features",
            extracted_names_for_verify,
            project_browser.prepare_extracted_features_tab,
            EXTRACTED_FEATURES_TAB_PAGE,
            use_feature_inputs=True,
        )

        total_passed = (
            scan_passed + annotation_passed + view_test_passed + extracted_passed
        )
        total_checked = scan_total + annotation_total + view_test_total + extracted_total

        logger.info("Search verification summary: %d/%d overall", total_passed, total_checked)
        print("\n=== Search verification summary ===")
        print(f"Scans:              {scan_passed}/{scan_total}")
        print(f"Annotations:        {annotation_passed}/{annotation_total}")
        print(f"View States:        {view_test_passed}/{view_test_total}")
        print(f"Extracted Features: {extracted_passed}/{extracted_total}")
        print(f"Overall:            {total_passed}/{total_checked}")

        logger.info("Refreshing page after all tasks completed")
        print("--- Refreshing page after all tasks completed ---")
        await viewer.reload()
        await viewer.wait_for_project_browser_ready()

        await browser.close()
        return total_passed, total_checked


async def main() -> None:
    setup_logging()
    total_passed, total_checked = await run_project_browser_flow()
    if total_passed != total_checked:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
