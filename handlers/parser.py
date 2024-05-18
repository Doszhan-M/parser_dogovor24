import aiohttp
import os
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Playwright


class ParserManager:

    def __init__(self) -> None:
        self.url = "https://new.dogovor24.kz/documents/dogovory-3"
        self.base_dir = Path("parsed_documents")

    async def save_to_file(self, soup, filename):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(str(soup))

    async def get_document_links(self, page):
        document_links = []
        documents = await page.query_selector_all("a.documents__file")
        for document in documents:
            link = await document.get_attribute("href")
            document_links.append(link)
        return document_links

    def create_directory(self, path):
        a = os.makedirs(path, exist_ok=True)
        print('a: ', a)
        
    async def start_parsing(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(self.url)
            await page.wait_for_selector("#documents-menu-documents-collapse")
            sections = await page.query_selector_all(
                "#documents-menu-documents-collapse a.documents__menu-btn"
            )
            self.create_directory(self.base_dir)
            for section_link in sections:
                await section_link.click()
                await page.wait_for_timeout(1000)
                element = await section_link.query_selector(".d24__additional-text")
                section_title = await element.inner_text()
                parent_path = self.base_dir / section_title
                self.create_directory(parent_path)
                
                subsections = await page.query_selector_all("a.documents__folder-btn")
                for subsection_link in subsections:
                    await subsection_link.click()
                    await page.wait_for_timeout(1000)
                    element = await subsection_link.query_selector("span.documents__folder-title")
                    subsection_title = await element.inner_text()
                    sub_parent_path = parent_path / subsection_title
                    self.create_directory(sub_parent_path)
                    parent_element = await subsection_link.evaluate_handle('el => el.parentElement')
                    last_element = await parent_element.evaluate_handle('el => el.lastElementChild')
                    nested_sections = await last_element.query_selector_all(
                        "a.documents__folder-btn"
                    )
                    for nested_link in nested_sections:
                        await nested_link.click()
                        await page.wait_for_timeout(1000)
                        element = await nested_link.query_selector("span.documents__folder-title")
                        subsection_title = await element.inner_text()
                        nested_parent_path = sub_parent_path / subsection_title
                        self.create_directory(nested_parent_path)
                        parent_element = await nested_link.evaluate_handle('el => el.parentElement')
                        last_element = await parent_element.evaluate_handle('el => el.lastElementChild')
                        sub_nested_sections = await last_element.query_selector_all(
                            "a.documents__folder-btn"
                        )   
                        for sub_nested_link in sub_nested_sections:
                            await sub_nested_link.click()
                            await page.wait_for_timeout(1000)
                            element = await sub_nested_link.query_selector("span.documents__folder-title")
                            subsection_title = await element.inner_text()
                            sub_nested_parent_path = nested_parent_path / subsection_title
                            self.create_directory(sub_nested_parent_path)
                        
                        
                                             
            await browser.close()

            # content = await page.inner_html('#documents-menu-documents-collapse')
            # soup = BeautifulSoup(content, 'html.parser')
            # await self.save_to_file(soup, "parsed_documents.html")
import aiohttp
import os
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Playwright


class ParserManager:

    def __init__(self) -> None:
        self.url = "https://new.dogovor24.kz/documents/dogovory-3"
        self.base_dir = Path("parsed_documents")

    async def save_to_file(self, soup, filename):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(str(soup))

    async def get_document_links(self, page):
        document_links = []
        documents = await page.query_selector_all("a.documents__file")
        for document in documents:
            link = await document.get_attribute("href")
            document_links.append(link)
        return document_links

    def create_directory(self, path):
        os.makedirs(path, exist_ok=True)
    
    async def expand(self, sections, page, sub_parent_path, selector):
        for section_link in sections:
            await section_link.click()
            await page.wait_for_timeout(1000)
            element = await section_link.query_selector(selector)
            subsection_title = await element.inner_text()
            nested_parent_path = sub_parent_path / subsection_title
            self.create_directory(nested_parent_path)
            parent_element = await section_link.evaluate_handle('el => el.parentElement')
            last_element = await parent_element.evaluate_handle('el => el.lastElementChild')
            sub_sections = await last_element.query_selector_all(
                "a.documents__folder-btn"
            ) 
            return sub_sections
                                  
    async def start_parsing(self):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.goto(self.url)
            await page.wait_for_selector("#documents-menu-documents-collapse")
            sections = await page.query_selector_all(
                "#documents-menu-documents-collapse a.documents__menu-btn"
            )
            self.create_directory(self.base_dir)
            for section_link in sections:
                await section_link.click()
                await page.wait_for_timeout(1000)
                element = await section_link.query_selector(".d24__additional-text")
                section_title = await element.inner_text()
                parent_path = self.base_dir / section_title
                self.create_directory(parent_path)
                
                subsections = await page.query_selector_all("a.documents__folder-btn")
                for subsection_link in subsections:
                    await subsection_link.click()
                    await page.wait_for_timeout(1000)
                    element = await subsection_link.query_selector("span.documents__folder-title")
                    subsection_title = await element.inner_text()
                    sub_parent_path = parent_path / subsection_title
                    self.create_directory(sub_parent_path)
                    parent_element = await subsection_link.evaluate_handle('el => el.parentElement')
                    last_element = await parent_element.evaluate_handle('el => el.lastElementChild')
                    nested_sections = await last_element.query_selector_all(
                        "a.documents__folder-btn"
                    )
                    for nested_link in nested_sections:
                        await nested_link.click()
                        await page.wait_for_timeout(1000)
                        element = await nested_link.query_selector("span.documents__folder-title")
                        subsection_title = await element.inner_text()
                        nested_parent_path = sub_parent_path / subsection_title
                        self.create_directory(nested_parent_path)
                        parent_element = await nested_link.evaluate_handle('el => el.parentElement')
                        last_element = await parent_element.evaluate_handle('el => el.lastElementChild')
                        sub_nested_sections = await last_element.query_selector_all(
                            "a.documents__folder-btn"
                        )   
                        for sub_nested_link in sub_nested_sections:
                            await sub_nested_link.click()
                            await page.wait_for_timeout(1000)
                            element = await sub_nested_link.query_selector("span.documents__folder-title")
                            subsection_title = await element.inner_text()
                            sub_nested_parent_path = nested_parent_path / subsection_title
                            self.create_directory(sub_nested_parent_path)
                        
                        
                                             
            await browser.close()

            # content = await page.inner_html('#documents-menu-documents-collapse')
            # soup = BeautifulSoup(content, 'html.parser')
            # await self.save_to_file(soup, "parsed_documents.html")
