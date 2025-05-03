# Miscellaneous
import os
import sys
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
from handlers.admin.event_creation import AdminEventCreatingRouter
from handlers.admin.event_cancel import EventCancelRouter
from handlers.admin.add_activist import AdminNewMemberRouter
from handlers.admin.del_activist import AdminDelMemberRouter
from handlers.member.default import MemberDefaultRouter


# Utils
from utils.token import GetBotTokenEnv, GetRedisCredEnv, GetPgCredEnv

# Storages
from storage.pgredis import PgRedisStorage, PostgresCredentials, RedisCredentials

# Middleware
from middleware.storage import StorageMiddleware
from middleware.log import LogMiddleware
from middleware.auth import AuthMiddleware
from middleware.agreement import AgreementMiddleware

# Logging config options
LOGGING_KWARGS = {
    "format": "[%(levelname)s, %(asctime)s, %(filename)s] func %(funcName)s, line %(lineno)d: %(message)s;",
    "datefmt": "%d.%m.%Y %H:%M:%S",
    "stream": sys.stdout,
    "level": logging.INFO if (os.getenv("LOGGER_DEBUG", '0') != '1') else logging.DEBUG
}


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
    
    dp.include_router(AdminNewMemberRouter)
    dp.include_router(AdminDelMemberRouter)
    dp.include_router(AdminEventCreatingRouter)
    dp.include_router(EventCancelRouter)
    dp.include_router(AdminDefaultRouter)
    dp.include_router(MemberDefaultRouter)
    dp.include_router(UnknownRouter)

    logger = logging.getLogger("bas-bot-logger")
    logging.basicConfig(**LOGGING_KWARGS)

    dp.update.outer_middleware(LogMiddleware(logger))
    dp.update.outer_middleware(StorageMiddleware(PgRedisStorage, pgcred, redcred))
    dp.update.outer_middleware(AgreementMiddleware())
    dp.update.outer_middleware(AuthMiddleware())


    asyncio.run(main())
