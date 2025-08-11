# core/keyword_engine.py
import logging
from playwright.async_api import Page, expect
from typing import Dict, Any, Optional
import os
import time

logger = logging.getLogger(__name__)

class KeywordEngine:
    # 可用关键词的字典，包含中文解释和所需参数。
    KEYWORD_DEFINITIONS = {
        "goto":              {"description": "跳转", "params": ["value"]},
        "click":             {"description": "点击", "params": ["locator"]},
        "fill":              {"description": "输入", "params": ["locator", "value"]},
        "press":             {"description": "按键", "params": ["locator", "value"]},
        "select_option":     {"description": "选择选项", "params": ["locator", "value"]},
        "wait_for_selector": {"description": "等待元素", "params": ["locator"]},
        "wait_for_url":      {"description": "等待URL", "params": ["value"]},
        "expect_text":       {"description": "验证文本", "params": ["locator", "value"]},
        "expect_title":      {"description": "验证标题", "params": ["value"]},
        "screenshot":        {"description": "截图", "params": ["value"]},
    }
    KEYWORDS = list(KEYWORD_DEFINITIONS.keys())

    def __init__(self, page: Page, base_url: str = "", output_dir: str = "reports"):
        self.page = page
        self.base_url = base_url
        self.output_dir = output_dir
        self.screenshot_dir = os.path.join(self.output_dir, "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def execute_step(self, step: Dict[str, Any]) -> (bool, str, Optional[str]):
        """
        执行单个测试步骤。
        返回元组：(成功, 消息, 截图路径)
        """
        keyword = step.get("keyword")
        locator = step.get("locator")
        value = step.get("value")
        description = step.get("description") or f"{keyword} {'on ' + locator if locator else ''}"

        logger.info(f"Executing step: {description}")

        try:
            if keyword not in self.KEYWORDS:
                raise ValueError(f"Unsupported keyword: {keyword}")

            # Dynamically get the corresponding method
            method = getattr(self, keyword)
            await method(locator=locator, value=value)
            
            message = f"SUCCESS: {description}"
            logger.info(message)
            
            return True, message, None

        except Exception as e:
            message = f"FAILURE: {description}. Error: {e}"
            logger.error(message, exc_info=True)
            screenshot_path = await self.screenshot(f"step_{step.get('id', 'unknown')}_failure.png")
            return False, message, screenshot_path

    def _get_locator(self, locator: str):
        if locator.startswith("/") or locator.startswith("("):
            return f"xpath={locator}"
        return locator

    async def goto(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not value:
            raise ValueError("'goto'关键词需要'value'字段中的URL。")
        url = value if value.startswith("http") else f"{self.base_url}{value}"
        # Navigate and wait for the network to be idle
        await self.page.goto(url, wait_until="networkidle")
        # Also wait for the body to be visible to ensure content is rendered
        await self.page.locator("body").wait_for(state="visible")

    async def click(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not locator:
            raise ValueError("'click'关键词需要'locator'。")
        await self.page.locator(self._get_locator(locator)).click()

    async def fill(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not locator or value is None:
            raise ValueError("'fill'关键词需要'locator'和'value'。")
        await self.page.locator(self._get_locator(locator)).fill(value)

    async def press(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not locator or not value:
            raise ValueError("'press'关键词需要'locator'和'value'中的按键。")
        await self.page.locator(self._get_locator(locator)).press(value)

    async def select_option(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not locator or not value:
            raise ValueError("'select_option'关键词需要'locator'和'value'。")
        await self.page.locator(self._get_locator(locator)).select_option(value)

    async def wait_for_selector(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not locator:
            raise ValueError("'wait_for_selector'关键词需要'locator'。")
        await self.page.wait_for_selector(self._get_locator(locator), state="visible")

    async def wait_for_url(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not value:
            raise ValueError("'wait_for_url'关键词需要'value'中的URL模式。")
        await self.page.wait_for_url(value)

    async def expect_text(self, locator: Optional[str] = None, value: Optional[str] = None):
        if not locator or value is None:
            raise ValueError("'expect_text'关键词需要'locator'和'value'。")
        await expect(self.page.locator(self._get_locator(locator))).to_have_text(value)

    async def expect_title(self, locator: Optional[str] = None, value: Optional[str] = None):
        if value is None:
            raise ValueError("'expect_title'关键词需要'value'中的标题。")
        await expect(self.page).to_have_title(value)

    async def screenshot(self, value: Optional[str] = None, **kwargs) -> str:
        """截图并保存。"""
        filename = value or f"screenshot_{int(time.time())}.png"
        path = os.path.join(self.screenshot_dir, filename)
        await self.page.screenshot(path=path)
        logger.info(f"截图已保存到 {path}")
        return path
