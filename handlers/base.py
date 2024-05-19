import os
import aiohttp
import aiofiles
from pathlib import Path
from playwright.async_api import async_playwright

from logger import logger


class BaseParser:

    max_filename_length: int = 110

    async def __aenter__(self) -> "BaseParser":
        self.session = aiohttp.ClientSession()
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(
        self, exc_type: type, exc_value: Exception, traceback: object
    ) -> None:
        await self.browser.close()
        await self.playwright.stop()
        await self.session.close()

    def create_directory(self, path: Path) -> None:
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")

    async def save_to_file(self, filename: Path, body: str) -> None:
        async with aiofiles.open(filename, "w", encoding="utf-8") as file:
            await file.write(body)

    def sanitize_filename(self, filename: str) -> str:
        sanitized = filename[: self.max_filename_length]
        if len(filename) > self.max_filename_length:
            logger.warning(f"Filename truncated: {filename} to {sanitized}")
        return sanitized

    async def request_document(self, url: str) -> str:
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                html: str = await response.text()
                return html
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching document from {url}: {e}")
            return ""
