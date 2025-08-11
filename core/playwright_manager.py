# core/playwright_manager.py
from playwright.async_api import async_playwright, Browser, Playwright
from typing import Optional

class PlaywrightManager:
    def __init__(self, browser_type: str = 'chromium', headless: bool = True):
        if browser_type not in ['chromium', 'firefox', 'webkit']:
            raise ValueError("不支持的浏览器类型。请从'chromium'、'firefox'、'webkit'中选择。")
        self.browser_type = browser_type
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None

    async def start(self):
        """启动Playwright实例并启动浏览器。"""
        print(f"正在初始化Playwright并启动{self.browser_type}...")
        self.playwright = await async_playwright().start()
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = await browser_launcher.launch(headless=self.headless)
        print(f"{self.browser_type.capitalize()}浏览器已启动。")
        return self.browser

    async def stop(self):
        """关闭浏览器并停止Playwright实例。"""
        if self.browser and self.browser.is_connected():
            await self.browser.close()
            print("浏览器已关闭。")
        if self.playwright:
            await self.playwright.stop()
            print("Playwright已停止。")

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

# 使用示例：
#
# async def main():
#     async with PlaywrightManager(browser_type='firefox', headless=False) as browser:
#         page = await browser.new_page()
#         await page.goto("http://example.com")
#         print(await page.title())
#         await page.close()
#
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
