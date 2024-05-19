from pathlib import Path
from typing import List
from playwright.async_api import Page

from logger import logger
from .base import BaseParser
from .scraper import Scraper


class ParserManager(BaseParser, Scraper):

    base_url: str = "https://new.dogovor24.kz"
    base_dir: Path = Path("parsed_documents")

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
