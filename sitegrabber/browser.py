
from playwright.async_api import async_playwright

class BrowserCtx:
    def __init__(self, user_agent: str, headless: bool):
        self.user_agent = user_agent
        self.headless = headless
        self.pw = None
        self.browser = None
        self.ctx = None

    async def __aenter__(self):
        self.pw = await async_playwright().start()
        self.browser = await self.pw.chromium.launch(headless=self.headless)
        self.ctx = await self.browser.new_context(ignore_https_errors=True, user_agent=self.user_agent)
        return self.ctx

    async def __aexit__(self, exc_type, exc, tb):
        await self.ctx.close()
        await self.browser.close()
        await self.pw.stop()
