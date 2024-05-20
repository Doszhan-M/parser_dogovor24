import time
import asyncio

from logger import logger
from handlers import ParserManager


async def parse_documents() -> None:
    start_time = time.time()
    logger.info("Start parsing")
    async with ParserManager() as parser:
        await parser.start_parsing()
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Total parsing duration: {duration:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(parse_documents())
