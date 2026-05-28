"""Browser context helpers for Recap viewer automation."""

from playwright.async_api import Browser, BrowserContext

from config.settings import LOCAL_NETWORK_ACCESS_PERMISSION, VIEWER_ORIGIN


async def new_viewer_context(browser: Browser) -> BrowserContext:
    """Create a context with local-network-access granted for the viewer origin."""
    context = await browser.new_context(
        permissions=[LOCAL_NETWORK_ACCESS_PERMISSION],
    )
    await context.grant_permissions(
        [LOCAL_NETWORK_ACCESS_PERMISSION],
        origin=VIEWER_ORIGIN,
    )
    return context
