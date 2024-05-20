import asyncio
from typing import List
from pathlib import Path
from playwright.async_api import Page

from logger import logger
from .base import BaseParser
from .scraper import Scraper


class ParserManager(BaseParser, Scraper):

    base_url: str = "https://new.dogovor24.kz"
    base_dir: Path = Path("parsed_documents")
    max_retries: int = 2
    retry_delay: int = 3

    async def start_parsing(self) -> None:
        await self.page.goto(self.base_url + "/documents/dogovory-3")
        await self.page.wait_for_selector("#documents-menu-documents-collapse")
        sections: List[Page] = await self.page.query_selector_all(
            "#documents-menu-documents-collapse a.documents__menu-btn"
        )
        self.create_directory(self.base_dir)
        for section_link in sections:
            await section_link.click()
            await self.page.screenshot(path=self.base_dir / "headless_screenshot.png")
            await self.page.wait_for_timeout(1000)
            element = await section_link.query_selector(".d24__additional-text")
            section_title: str = await element.inner_text()
            logger.info(f"Parsing section: {section_title}")
            parent_path = self.base_dir / self.sanitize_filename(section_title)
            self.create_directory(parent_path)
            subsections: List[Page] = await self.page.query_selector_all(
                "a.documents__folder-btn"
            )
            await self.parse_sections(subsections, parent_path)

    async def parse_sections(self, sections: List[Page], parent_path: Path) -> None:
        for section_link in sections:
            for attempt in range(self.max_retries):
                try:
                    await section_link.click()
                    await self.page.wait_for_timeout(1000)
                    element = await section_link.query_selector(
                        "span.documents__folder-title"
                    )
                    subsection_title: str = await element.inner_text()
                    logger.info(f"Parsing subsection: {subsection_title}")
                    nested_parent_path = parent_path / subsection_title
                    self.create_directory(nested_parent_path)
                    parent_element = await section_link.evaluate_handle(
                        "el => el.parentElement"
                    )
                    document_links: List[str] = await self.get_document_links(
                        parent_element
                    )
                    for document_link in document_links:
                        full_url: str = self.base_url + document_link
                        await self.parse_document_in_open_tab(
                            full_url, nested_parent_path
                        )
                    last_element = await parent_element.evaluate_handle(
                        "el => el.lastElementChild"
                    )
                    sub_sections: List[Page] = await last_element.query_selector_all(
                        "a.documents__folder-btn"
                    )
                    await self.parse_sections(sub_sections, nested_parent_path)
                    break  # Если все прошло успешно, выйти из цикла повторных попыток
                except Exception as e:
                    logger.warning(f"Error parsing subsection : {e}")
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        logger.error(
                            f"Failed to parse subsection after {self.max_retries} attempts. Error:\n{e}"
                        )

    async def parse_document_in_open_tab(self, url: str, save_path: Path) -> None:
        if not self.secondary_page:
            self.secondary_page = await self.browser.new_page()
        await self.secondary_page.goto(url)
        html: str = await self.secondary_page.content()
        title, preview = self.parse_preview(html)
        try:
            document_btn = await self.secondary_page.query_selector(
                ".document-banner button.btn-warning"
            )
            btn_text: str = await document_btn.inner_text()
        except AttributeError:
            logger.warning("not found document_btn")
            document_btn = await self.secondary_page.query_selector(".document-button")
            btn_text: str = await document_btn.inner_text()
        document = ""
        if "Перейти" in btn_text:
            await document_btn.click()
            await self.secondary_page.wait_for_selector(
                ".main-document .shared-matrix__wrapper"
            )
            html: str = await self.secondary_page.content()
            document = self.parse_document(html)
        body = preview + document
        filename: Path = save_path / f"{self.sanitize_filename(title)}.txt"
        await self.save_to_file(filename, body)
        logger.info(f"Parsed document: {filename}")

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
