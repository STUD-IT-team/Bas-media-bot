import asyncio
from logger import logger
from handlers import dp
from handlers.base import bot


async def main() -> None:
    await dp.start_polling(bot)
    logger.info('Started in [normal] mode')


if __name__ == "__main__":
    asyncio.run(main())
