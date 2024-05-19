import html2text
from typing import Tuple
from bs4 import BeautifulSoup

from logger import logger


class Scraper():

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
