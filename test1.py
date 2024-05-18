import os
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright

class ParserManager:

    def __init__(self) -> None:
        self.url = "https://new.dogovor24.kz/documents/dogovory-3"
        self.expanded_elements = set()
        self.base_dir = Path("parsed_documents")

    def create_directory(self, path):
        os.makedirs(path, exist_ok=True)

    async def save_links_to_file(self, links, directory, filename):
        self.create_directory(directory)
        filepath = directory / filename
        with open(filepath, "w", encoding="utf-8") as file:
            for link in links:
                file.write(f"{link}\n")
                        
    async def get_document_links(self, page):
        document_links = []
        documents = await page.query_selector_all('a.documents__file')
        for document in documents:
            link = await document.get_attribute('href')
            document_links.append(link)
        return document_links

    async def expand_and_collect_links(self, page, selector):
        all_document_links = []

        elements = await page.query_selector_all(selector)
        for element in elements:
            element_id = await element.get_attribute('href') or await element.inner_text()
            if element_id in self.expanded_elements:
                continue

            self.expanded_elements.add(element_id)
            await element.click()
            await page.wait_for_timeout(1000)

            document_links = await self.get_document_links(page)
            all_document_links.extend(document_links)

            sublinks = await self.expand_and_collect_links(page, 'a.documents__folder-btn')
            all_document_links.extend(sublinks)

        return all_document_links

    async def start_parsing(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(self.url)
            await page.wait_for_selector('#documents-menu-documents-collapse')
            self.create_directory(self.base_dir)
            all_document_links = await self.expand_and_collect_links(page, 'a.documents__menu-btn')

            await browser.close()
            return all_document_links


async def parse_documents() -> None:
    parser = ParserManager()
    document_links = await parser.start_parsing()
    print("Found document links:", document_links)


if __name__ == "__main__":
    asyncio.run(parse_documents())



есть ли метод playwright который получает текст из элемента, Например если:
playwright_el=<a data-v-686141b7="" data-v-4d2481ff="" class="documents__menu-btn p-2 d-flex align-items-center documents__menu-btn--active"><span data-v-686141b7="" class="d24__additional-text">Трудовые отношения</span></a>
как получить Трудовые отношения