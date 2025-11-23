from playwright.async_api import async_playwright
from utils.user_agent import get_random_ua


class PlaywrightManager:
    """
    Manages Playwright browser instances.
    """

    def __init__(self):
        self._playwright = None
        self._browser = None

    async def start(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)

    async def new_context_page(self):
        print("[DEBUG] PlaywrightManager: Creating new browser context...")
        context = await self._browser.new_context(user_agent=get_random_ua())
        print("[DEBUG] PlaywrightManager: Creating new page...")
        page = await context.new_page()
        print("[DEBUG] PlaywrightManager: Page created successfully")
        return page

    async def close_page(self, page):
        print("[DEBUG] PlaywrightManager: Closing page...")
        await page.close()
        print("[DEBUG] PlaywrightManager: Page closed")

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
