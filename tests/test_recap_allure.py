"""Pytest + Allure entry points for Recap viewer automation flows."""

import allure
import pytest

from tests.test_project_browser_flow import run_project_browser_flow
from tests.test_scan_group_toolbar_flow import run_scan_group_toolbar_flow


@allure.epic("Recap Viewer")
@allure.feature("Project Browser")
@allure.story("Stack collect, search verify, and refresh")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.project_browser
@pytest.mark.asyncio
async def test_project_browser_flow() -> None:
    """Verify scans, annotations, view states, and extracted features via search."""
    with allure.step("Run project browser verification flow"):
        total_passed, total_checked = await run_project_browser_flow()

    summary = f"{total_passed}/{total_checked} passed"
    allure.attach(summary, name="verification_summary", attachment_type=allure.attachment_type.TEXT)
    allure.dynamic.title(f"Project browser search verification ({summary})")

    assert total_passed == total_checked, (
        f"Search verification failed: {total_passed}/{total_checked} passed"
    )


@allure.epic("Recap Viewer")
@allure.feature("Bottom Toolbar")
@allure.story("Scan group tutorial and Done")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.scan_group
@pytest.mark.asyncio
async def test_scan_group_toolbar_flow() -> None:
    """Open scan group, dismiss tutorial modal, and click Done."""
    with allure.step("Run bottom toolbar scan group workflow"):
        await run_scan_group_toolbar_flow()

    allure.dynamic.title("Scan group toolbar workflow completed")
