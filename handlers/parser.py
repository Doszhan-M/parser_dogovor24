import os
import aiohttp
import aiofiles
import html2text
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Tuple
from playwright.async_api import async_playwright, Page

from logger import logger


class ParserManager:

    base_url: str = "https://new.dogovor24.kz"
    base_dir: Path = Path("parsed_documents")
    max_filename_length: int = 110

    async def __aenter__(self) -> "ParserManager":
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

    async def start_parsing(self) -> None:
        await self.page.goto(self.base_url + "/documents/dogovory-3")
        await self.page.wait_for_selector("#documents-menu-documents-collapse")
        sections: List[Page] = await self.page.query_selector_all(
            "#documents-menu-documents-collapse a.documents__menu-btn"
        )
        self.create_directory(self.base_dir)
        for section_link in sections:
            await section_link.click()
            await self.page.wait_for_timeout(1000)
            element = await section_link.query_selector(".d24__additional-text")
            section_title: str = await element.inner_text()
            logger.info(f"Parsing section: {section_title}")
            parent_path = self.base_dir / section_title
            self.create_directory(parent_path)
            subsections: List[Page] = await self.page.query_selector_all(
                "a.documents__folder-btn"
            )
            await self.parse_sections(subsections, parent_path)
        # try:
        # except Exception as e:
        #     logger.error(f"Error in start_parsing: {e}")

    async def parse_sections(self, sections: List[Page], parent_path: Path) -> None:
        for section_link in sections:
            await section_link.click()
            await self.page.wait_for_timeout(1000)
            element = await section_link.query_selector("span.documents__folder-title")
            subsection_title: str = await element.inner_text()
            logger.info(f"Parsing subsection: {subsection_title}")
            nested_parent_path = parent_path / subsection_title
            self.create_directory(nested_parent_path)
            parent_element = await section_link.evaluate_handle(
                "el => el.parentElement"
            )
            document_links: List[str] = await self.get_document_links(parent_element)
            for document_link in document_links:
                full_url: str = self.base_url + document_link
                html: str = await self.request_document(full_url)
                if html:
                    title, body = await self.parse_document(html)
                    filename: Path = (
                        nested_parent_path / f"{self.sanitize_filename(title)}.txt"
                    )
                    await self.save_to_file(filename, body)
            last_element = await parent_element.evaluate_handle(
                "el => el.lastElementChild"
            )
            sub_sections: List[Page] = await last_element.query_selector_all(
                "a.documents__folder-btn"
            )
            await self.parse_sections(sub_sections, nested_parent_path)
            # try:
            # except Exception as e:
            #     logger.error(f"Error in parse_sections: {e}")

    async def get_document_links(self, page: Page) -> List[str]:
        document_links: List[str] = []
        try:
            documents: List[Page] = await page.query_selector_all("a.documents__file")
            for document in documents:
                link: str = await document.get_attribute("href")
                if link:
                    document_links.append(link)
                else:
                    logger.warning("Document link not found")
        except Exception as e:
            logger.error(f"Error in get_document_links: {e}")
        return document_links

    async def request_document(self, url: str) -> str:
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                html: str = await response.text()
                return html
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching document from {url}: {e}")
            return ""

    async def parse_document(self, html: str) -> Tuple[str, str]:
        soup = BeautifulSoup(html, "html.parser")
        title_element = soup.find(class_="document-banner__title")
        body_element = soup.find(class_="document__document-body")
        if title_element:
            title: str = title_element.text.strip()
        else:
            title_element = soup.find(class_="document-title")
            title: str = title_element.text.strip()
        if body_element:
            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = True
            body = text_maker.handle(str(body_element))
            logger.info(f"Parsed document: {title}")
        return title, body

    def create_directory(self, path: Path) -> None:
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")

    async def save_to_file(self, filename: Path, body: str) -> None:
        async with aiofiles.open(filename, "w", encoding="utf-8") as file:
            await file.write(body)
            logger.info(f"Saved document to {filename}")

    def sanitize_filename(self, filename: str) -> str:
        sanitized = filename[: self.max_filename_length]
        if len(filename) > self.max_filename_length:
            logger.warning(f"Filename truncated: {filename} to {sanitized}")
        return sanitized
