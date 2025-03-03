
# Miscellaneous
import asyncio
import redis
import logging

# Aiogram
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode

# Routers
from handlers.unknown import UnknownRouter
from handlers.admin.default import AdminDefaultRouter
from handlers.member.default import MemberDefaultRouter

# Utils
from utils.token import GetBotTokenEnv, GetRedisCredEnv, GetPgCredEnv

# Storages
from storage.pgredis import PgRedisStorage, PostgresCredentials, RedisCredentials

# Middleware
from middleware.storage import StorageMiddleware
from middleware.log import LogMiddleware
from middleware.auth import AuthMiddleware


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
    
    dp.include_router(AdminDefaultRouter)
    dp.include_router(MemberDefaultRouter)
    dp.include_router(UnknownRouter)
    
    dp.update.outer_middleware(LogMiddleware(logging.getLogger("bas-bot-logger")))
    dp.update.outer_middleware(StorageMiddleware(PgRedisStorage, pgcred, redcred))
    dp.update.outer_middleware(AuthMiddleware())
    


    asyncio.run(main())

