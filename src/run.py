import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from handlers.unknown import UnknownRouter
from utils.token import GetBotTokenEnv, GetRedisCredEnv, GetPgCredEnv
from storage.pgredis import PgRedisStorage, PostgresCredentials, RedisCredentials
from middleware.storage import StorageMiddleware


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":

    pgcred = PostgresCredentials(**GetPgCredEnv())
    redcred = RedisCredentials(**GetRedisCredEnv())
    try:
        storage = PgRedisStorage(pgcred, redcred)
    except Exception as e:
        print(f"Ошибка при создании хранилища: {str(e)}")
        exit(1)

    bot = Bot(token=GetBotTokenEnv(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(UnknownRouter)

    dp.update.outer_middleware(StorageMiddleware(PgRedisStorage, pgcred, redcred))


    asyncio.run(main())

