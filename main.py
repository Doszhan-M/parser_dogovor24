import asyncio

from handlers import ParserManager


async def parse_documents() -> None:
    parser = ParserManager()
    await parser.start_parsing()


if __name__ == "__main__":
    asyncio.run(parse_documents())
    
    
    
            # content = await page.inner_html('#documents-menu-documents-collapse')
            # soup = BeautifulSoup(content, 'html.parser')
            # await self.save_to_file(soup, "parsed_documents.html")