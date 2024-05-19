import html2text
from typing import Tuple
from bs4 import BeautifulSoup


class Scraper:

    def parse_preview(self, html: str) -> Tuple[str, str]:
        soup = BeautifulSoup(html, "html.parser")
        title_element = soup.find(class_="document-banner__title")
        body_element = soup.find(class_="document__document-body")
        if title_element:
            title: str = title_element.text.strip()
        else:
            title_element = soup.find(class_="document-title")
            title: str = title_element.text.strip()
        body = ""
        if body_element:
            text_maker = html2text.HTML2Text()
            text_maker.ignore_links = True
            body = text_maker.handle(str(body_element))
        return title, body

    def parse_document(self, html: str) -> Tuple[str, str]:
        soup = BeautifulSoup(html, "html.parser")
        document_body = soup.find(class_="main-document")
        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = True
        document = text_maker.handle(str(document_body))
        return document
