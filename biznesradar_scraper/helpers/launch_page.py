from playwright.sync_api import sync_playwright, Page
from typing import Any

from ..lib.logger import logger


class LaunchPage:

    def __init__(self, url: str) -> None:
        self._url = url
        self._playwright = None
        self._browser = None

    def __enter__(self) -> Page:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)
        page = self._browser.new_page(viewport={"width": 1920, "height": 1080})
        logger.info(f"Loading {self._url}")
        page.goto(self._url)

        return page

    def __exit__(self, *args: Any) -> None:
        self._browser.close()
        self._playwright.stop()
