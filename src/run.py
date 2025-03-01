import asyncio
import redis
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from handlers.unknown import UnknownRouter
from utils.token import GetBotTokenEnv, GetRedisCredEnv, GetPgCredEnv
from storage.pgredis import PgRedisStorage, PostgresCredentials, RedisCredentials
from middleware.storage import StorageMiddleware
from middleware.log import LogMiddleware


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":

    pgcred = PostgresCredentials(**GetPgCredEnv())
    redcred = RedisCredentials(**GetRedisCredEnv(), db=0)
    try:
        storage = PgRedisStorage(pgcred, redcred)
        del storage
    except Exception as e:
        print(f"Ошибка при создании хранилища: {str(e)}")
        exit(1)

    bot = Bot(token=GetBotTokenEnv(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=RedisStorage.from_url(f"redis://{redcred.user}:{redcred.password}@{redcred.host}:{redcred.port}/1"))
    dp.include_router(UnknownRouter)

    dp.update.outer_middleware(StorageMiddleware(PgRedisStorage, pgcred, redcred))
    dp.update.outer_middleware(LogMiddleware(logging.getLogger("bas-bot-logger")))


    asyncio.run(main())

