import abc
from playwright.sync_api import sync_playwright
from typing import Protocol
import json


class AbstractScraper(Protocol):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc, tb):
        pass

    def run(self, url: str) -> dict:
        pass


class PlaywrightScraper:
    """Opens a chromium browser and keeps it alive until the program ends."""

    def __init__(self):
        self.browser = sync_playwright().start().chromium.launch(headless=True)
        self.browser_ctx = None

    def __enter__(self):
        self.browser_ctx = self.browser.new_context()
        return self.browser_ctx.new_page()

    def __exit__(self, exc_type, exc, tb):
        self.browser_ctx.close()

    def run(self, url: str) -> dict:
        try:
            with self as page:
                body_b = page.goto(url).body()
                body_json = json.loads(body_b.decode("utf-8"))
        except Exception as e:
            raise e
        else:
            return body_json
