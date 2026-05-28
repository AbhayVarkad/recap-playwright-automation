"""Project browser page object for tree navigation and search verification."""

from collections.abc import Awaitable, Callable

from config.selectors import (
    ANNOTATIONS_TAB_HEADER,
    ANNOTATIONS_TAB_PAGE,
    ANNOTATION_ITEMS,
    EXTRACTED_FEATURES_CHILDREN,
    EXTRACTED_FEATURES_GROUP,
    EXTRACTED_FEATURES_TAB_HEADER,
    EXTRACTED_FEATURES_TAB_PAGE,
    EXTRACTED_FEATURE_INPUTS,
    EXTRACTED_FEATURE_INPUTS_TEMPLATE,
    PROJECT_BROWSER_NO_RESULTS,
    PROJECT_BROWSER_SEARCH,
    PROJECT_BROWSER_TITLE,
    PROJECT_BROWSER_TOGGLE,
    SCAN_GROUP_LABEL,
    SCANS_CHILD_ITEMS,
    SCANS_TAB_PAGE,
    TREE_TEXT_ITEMS,
    VIEW_STATES_GROUP,
    VIEW_STATES_TAB_HEADER,
    VIEW_STATES_TAB_PAGE,
    VIEW_STATE_ITEMS,
)
from config.settings import DEFAULT_TIMEOUT_MS, SEARCH_FILTER_DELAY_MS
from pages.base_page import BasePage
from utils.text_helpers import normalize_tree_label, search_query_for_name


class ProjectBrowserPage(BasePage):
    """Actions for the Project Browser panel tabs, trees, and search."""

    async def ensure_open(self) -> None:
        """Open the Project Browser panel if it is collapsed."""
        panel_title = self.page.locator(PROJECT_BROWSER_TITLE)
        if await panel_title.is_visible():
            return
        toggle = self.page.locator(PROJECT_BROWSER_TOGGLE).first
        await toggle.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await toggle.click()

    async def click_scan_group(self) -> None:
        """Click the 'All Scans' scan group in the project browser."""
        await self.ensure_open()
        self.logger.info("Clicking scan group in project browser")
        scan_group = self.page.locator(SCAN_GROUP_LABEL)
        await scan_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await scan_group.click()

    async def collect_scan_names(self) -> list[str]:
        """Return scan names listed under the scan group (excludes 'All Scans')."""
        scan_items = self.page.locator(SCANS_CHILD_ITEMS)
        await scan_items.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        return await self._collect_text_items(scan_items)

    async def open_annotations_tab(self) -> None:
        """Open the Annotations tab in the project browser."""
        await self.ensure_open()
        self.logger.info("Opening Annotations tab in project browser")
        annotations_tab = self.page.locator(ANNOTATIONS_TAB_HEADER)
        await annotations_tab.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await annotations_tab.click()
        annotation_page = self.page.locator(ANNOTATIONS_TAB_PAGE)
        await annotation_page.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)

    async def collect_annotation_names(self) -> list[str]:
        """Return annotation names listed under the Annotations tab."""
        annotation_items = self.page.locator(ANNOTATION_ITEMS)
        await annotation_items.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        return await self._collect_text_items(annotation_items)

    async def open_view_states_tab(self) -> None:
        """Open the View States tab in the project browser."""
        await self.ensure_open()
        self.logger.info("Opening View States tab in project browser")
        view_tests_tab = self.page.locator(VIEW_STATES_TAB_HEADER)
        await view_tests_tab.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await view_tests_tab.click()
        view_test_page = self.page.locator(VIEW_STATES_TAB_PAGE)
        await view_test_page.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)

    async def click_view_states_group(self) -> None:
        """Click the 'View States' group in the project browser."""
        await self.ensure_open()
        self.logger.info("Clicking View States group in project browser")
        view_test_group = self.page.locator(VIEW_STATES_GROUP)
        await view_test_group.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await view_test_group.click()

    async def prepare_view_states_tab(self) -> None:
        """Open View States tab and expand the group for search verification."""
        await self.open_view_states_tab()
        await self.click_view_states_group()

    async def collect_view_state_names(self) -> list[str]:
        """Return view state names listed under the View States group."""
        view_test_items = self.page.locator(VIEW_STATE_ITEMS)
        await view_test_items.first.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        return await self._collect_text_items(view_test_items)

    async def open_extracted_features_tab(self) -> None:
        """Open the Extracted Features tab in the project browser."""
        await self.ensure_open()
        self.logger.info("Opening Extracted Features tab in project browser")
        extracted_features_tab = self.page.locator(EXTRACTED_FEATURES_TAB_HEADER)
        await extracted_features_tab.wait_for(
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )
        await extracted_features_tab.click()
        extracted_features_page = self.page.locator(EXTRACTED_FEATURES_TAB_PAGE)
        await extracted_features_page.wait_for(
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )

    async def click_extracted_features_group(self) -> None:
        """Expand the top-level Extracted Features group if it is collapsed."""
        await self.ensure_open()
        self.logger.info("Clicking Extracted Features group in project browser")
        extracted_features_group = self.page.locator(EXTRACTED_FEATURES_GROUP)
        await extracted_features_group.wait_for(
            state="visible",
            timeout=DEFAULT_TIMEOUT_MS,
        )
        group_class = await extracted_features_group.get_attribute("class") or ""
        if "expanded" not in group_class:
            await extracted_features_group.click()
            await extracted_features_group.wait_for(
                state="visible",
                timeout=DEFAULT_TIMEOUT_MS,
            )

    async def prepare_extracted_features_tab(self) -> None:
        """Open Extracted Features tab and expand the group for search verification."""
        await self.open_extracted_features_tab()
        await self.click_extracted_features_group()

    async def collect_extracted_feature_names(self) -> list[str]:
        """Return extracted feature names listed under the Extracted Features group."""
        children_container = self.page.locator(EXTRACTED_FEATURES_CHILDREN)
        await children_container.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        feature_items = self.page.locator(EXTRACTED_FEATURE_INPUTS)
        await feature_items.first.wait_for(state="attached", timeout=DEFAULT_TIMEOUT_MS)
        names: list[str] = []
        for i in range(await feature_items.count()):
            text = (await feature_items.nth(i).input_value() or "").strip()
            if text:
                names.append(text)
        return names

    async def clear_search(self) -> None:
        """Clear the project browser search box."""
        await self.ensure_open()
        search = self.page.locator(PROJECT_BROWSER_SEARCH)
        await search.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await search.click()
        await search.fill("")
        await self.page.wait_for_timeout(SEARCH_FILTER_DELAY_MS)

    async def search(self, query: str) -> None:
        """Type a query into the project browser search box and wait for filtering."""
        await self.ensure_open()
        search = self.page.locator(PROJECT_BROWSER_SEARCH)
        await search.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        await search.click()
        await search.fill(query)
        await self.page.wait_for_timeout(SEARCH_FILTER_DELAY_MS)

    async def is_search_no_results(self) -> bool:
        """Return True when the search UI shows a no-results state."""
        no_result = self.page.locator(PROJECT_BROWSER_NO_RESULTS)
        if await no_result.count() == 0:
            return False
        return await no_result.is_visible()

    async def tab_contains_name(
        self,
        tab_page: str,
        name: str,
        *,
        use_feature_inputs: bool = False,
    ) -> bool:
        """Return True when an item with the exact name exists in the active tab tree."""
        if use_feature_inputs:
            items = self.page.locator(
                EXTRACTED_FEATURE_INPUTS_TEMPLATE.format(tab_page=tab_page)
            )
            for i in range(await items.count()):
                value = (await items.nth(i).input_value() or "").strip()
                if value == name:
                    return True
            return False

        target = normalize_tree_label(name)
        items = self.page.locator(TREE_TEXT_ITEMS.format(tab_page=tab_page))
        for i in range(await items.count()):
            text = normalize_tree_label(await items.nth(i).text_content() or "")
            if text == target:
                return True
        return False

    async def verify_names_via_search(
        self,
        category: str,
        names: list[str],
        prepare_tab: Callable[[], Awaitable[None]],
        tab_page: str,
        *,
        use_feature_inputs: bool = False,
    ) -> tuple[int, int]:
        """Search each name in the project browser (LIFO) and report FOUND / NOT FOUND."""
        passed = 0
        self.logger.info(
            "Verifying %s via project browser search (LIFO order: last stored verified first)",
            category,
        )
        print(
            f"\n--- Verifying {category} via project browser search "
            "(LIFO order: last stored verified first) ---"
        )
        await prepare_tab()
        for name in reversed(names):
            await self.clear_search()
            await self.search(search_query_for_name(name))
            found = (not await self.is_search_no_results()) and await self.tab_contains_name(
                tab_page,
                name,
                use_feature_inputs=use_feature_inputs,
            )
            status = "FOUND" if found else "NOT FOUND"
            self.logger.info("Verified: %s - %s", name, status)
            print(f"Verified: {name} - {status}")
            if found:
                passed += 1
            await self.clear_search()
        self.logger.info("%s verification: %d/%d passed", category, passed, len(names))
        print(f"{category} verification: {passed}/{len(names)} passed")
        return passed, len(names)

    async def _collect_text_items(self, locator) -> list[str]:
        """Collect non-empty text content from a locator's elements."""
        names: list[str] = []
        for i in range(await locator.count()):
            text = (await locator.nth(i).text_content() or "").strip()
            if text:
                names.append(text)
        return names
