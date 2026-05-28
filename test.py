import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from playwright.async_api import async_playwright

from utils.browser import new_viewer_context

VIEWER_URL = (
    "https://cdn.recap-staging.autodesk.com/viewer/current/index.html?"
    "file=https://rs-asrd-nas.ads.autodesk.com/datasets/rctp_v1.0/"
    "AutodeskReCapSampleProject_realview/AutodeskReCapSampleProject.rcp"
    "&env=local&src=local"
)
DEFAULT_TIMEOUT_MS = 120_000
PROJECT_BROWSER_SEARCH = "#search-input"
SEARCH_FILTER_DELAY_MS = 800


def normalize_tree_label(text: str) -> str:
    """Normalize tree labels that may span multiple lines."""
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def search_query_for_name(name: str) -> str:
    """Build a single-line search query (search box does not accept newlines well)."""
    lines = [line.strip() for line in name.splitlines() if line.strip()]
    return lines[0] if lines else name.strip()


async def wait_for_viewer_ready(page) -> None:
    """Wait until the viewer page and project browser scan tree are ready."""
    await page.wait_for_load_state("load", timeout=DEFAULT_TIMEOUT_MS)
    await page.wait_for_load_state("networkidle", timeout=DEFAULT_TIMEOUT_MS)
    await page.wait_for_selector("#Root", state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await page.wait_for_selector(
        '#tab-page-scan > .tree-node span.line-item-text',
        state="visible",
        timeout=DEFAULT_TIMEOUT_MS,
    )


async def ensure_project_browser_open(page) -> None:
    panel_title = page.locator('.docking-panel-title:has-text("Project Browser")')
    if await panel_title.is_visible():
        return
    toggle = page.locator("#recap-pcv-project-panel, #recap-rv-project-panel").first
    await toggle.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await toggle.click()


async def click_scan_group(page) -> None:
    """Click the 'All Scans' scan group in the project browser."""
    await ensure_project_browser_open(page)
    scan_group = page.locator("#Root span.line-item-text")
    await scan_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await scan_group.click()


async def collect_scan_names(page) -> list[str]:
    """Return the two scan names listed under the scan group (excludes 'All Scans')."""
    scan_items = page.locator(
        "#tab-page-scan > .tree-node:not(#Root) span.line-item-text"
    )
    await scan_items.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    names: list[str] = []
    for i in range(await scan_items.count()):
        text = (await scan_items.nth(i).text_content() or "").strip()
        if text:
            names.append(text)
    return names


async def click_annotations_tab(page) -> None:
    """Open the Annotations tab in the project browser."""
    await ensure_project_browser_open(page)
    annotations_tab = page.locator("#tab-header-annotation")
    await annotations_tab.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await annotations_tab.click()
    annotation_page = page.locator("#tab-page-annotation")
    await annotation_page.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)


async def collect_annotation_names(page) -> list[str]:
    """Return annotation names listed under the Annotations tab."""
    annotation_items = page.locator(
        "#tab-page-annotation .line-item .line-item-text"
    )
    await annotation_items.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    names: list[str] = []
    for i in range(await annotation_items.count()):
        text = (await annotation_items.nth(i).text_content() or "").strip()
        if text:
            names.append(text)
    return names


async def click_view_tests_tab(page) -> None:
    """Open the View States tab in the project browser."""
    await ensure_project_browser_open(page)
    view_tests_tab = page.locator("#tab-header-view-state")
    await view_tests_tab.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await view_tests_tab.click()
    view_test_page = page.locator("#tab-page-view-state")
    await view_test_page.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)


async def click_view_test_group(page) -> None:
    """Click the 'View States' group in the project browser."""
    await ensure_project_browser_open(page)
    view_test_group = page.locator("#Root-ViewState span.line-item-text")
    await view_test_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await view_test_group.click()


async def prepare_view_states_tab(page) -> None:
    """Open View States tab and expand the group for search verification."""
    await click_view_tests_tab(page)
    await click_view_test_group(page)


async def prepare_extracted_features_tab(page) -> None:
    """Open Extracted Features tab and expand the group for search verification."""
    await click_extracted_features_tab(page)
    await click_extracted_features_group(page)


async def collect_view_test_names(page) -> list[str]:
    """Return view state names listed under the View States group."""
    view_test_items = page.locator(
        "#tab-page-view-state > .tree-node:not(#Root-ViewState) span.line-item-text"
    )
    await view_test_items.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    names: list[str] = []
    for i in range(await view_test_items.count()):
        text = (await view_test_items.nth(i).text_content() or "").strip()
        if text:
            names.append(text)
    return names


async def click_extracted_features_tab(page) -> None:
    """Open the Extracted Features tab in the project browser."""
    await ensure_project_browser_open(page)
    extracted_features_tab = page.locator("#tab-header-linear-feature")
    await extracted_features_tab.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await extracted_features_tab.click()
    extracted_features_page = page.locator("#tab-page-linear-feature")
    await extracted_features_page.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)


async def click_extracted_features_group(page) -> None:
    """Expand the top-level Extracted Features group if it is collapsed."""
    await ensure_project_browser_open(page)
    extracted_features_group = page.locator("#point-first-level > .lf-tree-item-container")
    await extracted_features_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    group_class = await extracted_features_group.get_attribute("class") or ""
    if "expanded" not in group_class:
        await extracted_features_group.click()
        await extracted_features_group.wait_for(
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )


async def clear_project_browser_search(page) -> None:
    """Clear the project browser search box so tabs and trees are unobstructed."""
    await ensure_project_browser_open(page)
    search = page.locator(PROJECT_BROWSER_SEARCH)
    await search.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await search.click()
    await search.fill("")
    await page.wait_for_timeout(SEARCH_FILTER_DELAY_MS)


async def search_project_browser(page, query: str) -> None:
    """Type a query into the project browser search box and wait for filtering."""
    await ensure_project_browser_open(page)
    search = page.locator(PROJECT_BROWSER_SEARCH)
    await search.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    await search.click()
    await search.fill(query)
    await page.wait_for_timeout(SEARCH_FILTER_DELAY_MS)


async def is_search_no_results(page) -> bool:
    """Return True when the search UI shows a no-results state."""
    no_result = page.locator("#project-panel-search-container .no-result-item")
    if await no_result.count() == 0:
        return False
    return await no_result.is_visible()


async def tab_contains_name(
    page,
    tab_page: str,
    name: str,
    *,
    use_feature_inputs: bool = False,
) -> bool:
    """Return True when an item with the exact name exists in the active tab tree."""
    if use_feature_inputs:
        items = page.locator(
            f"{tab_page} #point-first-level > .lf-tree-node-children-container "
            "> .lf-tree-node-container input.lf-curb-name-container[id$='-lf-title']"
        )
        for i in range(await items.count()):
            value = (await items.nth(i).input_value() or "").strip()
            if value == name:
                return True
        return False

    target = normalize_tree_label(name)
    items = page.locator(f"{tab_page} span.line-item-text, {tab_page} .line-item-text")
    for i in range(await items.count()):
        text = normalize_tree_label(await items.nth(i).text_content() or "")
        if text == target:
            return True
    return False


async def verify_names_in_project_browser(
    page,
    category: str,
    names: list[str],
    prepare_tab: Callable[[Any], Awaitable[None]],
    tab_page: str,
    *,
    use_feature_inputs: bool = False,
) -> tuple[int, int]:
    """Search each name in the project browser (LIFO) and report FOUND / NOT FOUND."""
    passed = 0
    print(
        f"\n--- Verifying {category} via project browser search "
        "(LIFO order: last stored verified first) ---"
    )
    await prepare_tab(page)
    for name in reversed(names):
        await clear_project_browser_search(page)
        await search_project_browser(page, search_query_for_name(name))
        found = (not await is_search_no_results(page)) and await tab_contains_name(
            page,
            tab_page,
            name,
            use_feature_inputs=use_feature_inputs,
        )
        status = "FOUND" if found else "NOT FOUND"
        print(f"Verified: {name} - {status}")
        if found:
            passed += 1
        await clear_project_browser_search(page)
    print(f"{category} verification: {passed}/{len(names)} passed")
    return passed, len(names)


async def collect_extracted_feature_names(page) -> list[str]:
    """Return extracted feature names listed under the Extracted Features group."""
    children_container = page.locator(
        "#tab-page-linear-feature #point-first-level > .lf-tree-node-children-container"
    )
    await children_container.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    feature_items = page.locator(
        "#tab-page-linear-feature #point-first-level > .lf-tree-node-children-container "
        "> .lf-tree-node-container input.lf-curb-name-container[id$='-lf-title']"
    )
    await feature_items.first.wait_for(state="attached", timeout=DEFAULT_TIMEOUT_MS)
    names: list[str] = []
    for i in range(await feature_items.count()):
        text = (await feature_items.nth(i).input_value() or "").strip()
        if text:
            names.append(text)
    return names


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await new_viewer_context(browser)
        page = await context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT_MS)

        print("--- Launching Recap viewer ---")
        await page.goto(VIEWER_URL, wait_until="domcontentloaded")

        print("--- Waiting for initial viewer to be fully loaded ---")
        await wait_for_viewer_ready(page)

        print("--- Refreshing viewer ---")
        await page.reload(wait_until="domcontentloaded")

        print("--- Waiting for viewer after refresh ---")
        await wait_for_viewer_ready(page)

        print("--- Clicking scan group in project browser ---")
        await click_scan_group(page)

        print("--- Fetching scans ---")
        scan_stack: list[str] = []
        scan_names = await collect_scan_names(page)

        if len(scan_names) < 2:
            raise RuntimeError(
                f"Expected at least 2 scans after clicking scan group, found {len(scan_names)}: {scan_names}"
            )

        for name in scan_names[:2]:
            scan_stack.append(name)
            print(f"Stored in stack: {name}")

        print(f"\nTotal scans stored in stack: {len(scan_stack)}\n")

        scan_names_for_verify = list(scan_stack)
        print("--- Processing scan stack (LIFO order) ---")
        while scan_stack:
            current_scan = scan_stack.pop()
            print(f"Printing/Processing scan: {current_scan}")
            await page.wait_for_timeout(500)

        scan_passed, scan_total = await verify_names_in_project_browser(
            page,
            "Scans",
            scan_names_for_verify,
            click_scan_group,
            "#tab-page-scan",
        )

        print("\n--- Opening Annotations tab in project browser ---")
        await click_annotations_tab(page)

        print("--- Fetching annotations ---")
        annotation_stack: list[str] = []
        annotation_names = await collect_annotation_names(page)

        for name in annotation_names:
            annotation_stack.append(name)
            print(f"Stored annotation in stack: {name}")

        print(f"\nTotal annotations stored in stack: {len(annotation_stack)}\n")

        annotation_names_for_verify = list(annotation_stack)
        print("--- Processing annotation stack (LIFO order) ---")
        while annotation_stack:
            current_annotation = annotation_stack.pop()
            print(f"Printing/Processing annotation: {current_annotation}")
            await page.wait_for_timeout(500)

        annotation_passed, annotation_total = await verify_names_in_project_browser(
            page,
            "Annotations",
            annotation_names_for_verify,
            click_annotations_tab,
            "#tab-page-annotation",
        )

        print("\n--- Opening View States tab in project browser ---")
        await click_view_tests_tab(page)

        print("--- Clicking View States group in project browser ---")
        await click_view_test_group(page)

        print("--- Fetching view tests ---")
        view_test_stack: list[str] = []
        view_test_names = await collect_view_test_names(page)

        for name in view_test_names:
            view_test_stack.append(name)
            print(f"Stored view test in stack: {name}")

        print(f"\nTotal view tests stored in stack: {len(view_test_stack)}\n")

        view_test_names_for_verify = list(view_test_stack)
        print("--- Processing view test stack (LIFO order) ---")
        while view_test_stack:
            current_view_test = view_test_stack.pop()
            print(f"Printing/Processing view test: {current_view_test}")
            await page.wait_for_timeout(500)

        view_test_passed, view_test_total = await verify_names_in_project_browser(
            page,
            "View States",
            view_test_names_for_verify,
            prepare_view_states_tab,
            "#tab-page-view-state",
        )

        print("\n--- Opening Extracted Features tab in project browser ---")
        await click_extracted_features_tab(page)

        print("--- Clicking Extracted Features group in project browser ---")
        await click_extracted_features_group(page)

        print("--- Fetching extracted features ---")
        extracted_features_stack: list[str] = []
        extracted_feature_names = await collect_extracted_feature_names(page)

        for name in extracted_feature_names:
            extracted_features_stack.append(name)
            print(f"Stored extracted feature in stack: {name}")

        print(
            f"\nTotal extracted features stored in stack: {len(extracted_features_stack)}\n"
        )

        extracted_names_for_verify = list(extracted_features_stack)
        print("--- Processing extracted features stack (LIFO order) ---")
        while extracted_features_stack:
            current_feature = extracted_features_stack.pop()
            print(f"Printing/Processing extracted feature: {current_feature}")
            await page.wait_for_timeout(500)

        extracted_passed, extracted_total = await verify_names_in_project_browser(
            page,
            "Extracted Features",
            extracted_names_for_verify,
            prepare_extracted_features_tab,
            "#tab-page-linear-feature",
            use_feature_inputs=True,
        )

        total_passed = (
            scan_passed
            + annotation_passed
            + view_test_passed
            + extracted_passed
        )
        total_checked = (
            scan_total + annotation_total + view_test_total + extracted_total
        )
        print("\n=== Search verification summary ===")
        print(f"Scans:              {scan_passed}/{scan_total}")
        print(f"Annotations:        {annotation_passed}/{annotation_total}")
        print(f"View States:        {view_test_passed}/{view_test_total}")
        print(f"Extracted Features: {extracted_passed}/{extracted_total}")
        print(f"Overall:            {total_passed}/{total_checked}")

        print("--- Refreshing page after all tasks completed ---")
        await page.reload(wait_until="domcontentloaded")
        await wait_for_viewer_ready(page)

        await browser.close()

        if total_passed != total_checked:
            raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
