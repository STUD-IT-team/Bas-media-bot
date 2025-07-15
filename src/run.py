# Miscellaneous
import os
import sys
import asyncio
import redis
import logging
import argparse
from dotenv import load_dotenv

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
from handlers.admin.event_complete import EventCompleteRouter
from handlers.admin.add_activist import AdminNewMemberRouter
from handlers.admin.del_activist import AdminDelMemberRouter
from handlers.admin.add_notification import AdminAddNotificationRouter
from handlers.admin.event_export import AdminExportEventRouter

from handlers.member.default import MemberDefaultRouter
from handlers.member.report_adding import MemberReportAddingRouter

# Utils
from utils.token import GetBotTokenEnv, GetRedisCredEnv, GetPgCredEnv
from utils.passbot import SetBot, PassBot

# Storages
from storage.pgredis import PgRedisStorage, PostgresCredentials, RedisCredentials

# Middleware
from middleware.storage import StorageMiddleware
from middleware.log import LogMiddleware
from middleware.auth import AuthMiddleware
from middleware.agreement import AgreementMiddleware

# NotificationService
from notifications.NotificationService import NotificationService
from middleware.notifications import NotificationsMiddleware

# Google Export Service
import googlexport.report.singleton as singleton
from googlexport.report.repository import PostgresCredentials as SingletonPgCreds
from utils.token import GetGoogleExportCredsEnv

# Logging config options
LOGGING_KWARGS = {
    "format": "[%(levelname)s, %(asctime)s, %(filename)s] func %(funcName)s, line %(lineno)d: %(message)s;",
    "datefmt": "%d.%m.%Y %H:%M:%S",
    "stream": sys.stdout,
    "level": logging.INFO if (os.getenv("LOGGER_DEBUG", '0') != '1') else logging.DEBUG
}


async def main() -> None:
    await notifServ.AddStorage(PgRedisStorage(pgcred, redcred))
    # Один event loop
    scheduler_task = asyncio.create_task(notifServ.StartScheduler())    # Запуск планировщика в фоне

    # Init google export service
    singletonCreds = GetGoogleExportCredsEnv()
    await singleton.__init__(
        singletonCreds['credsFile'],
        singletonCreds['spreadsheetId'],
        SingletonPgCreds(**singletonCreds['pgcred']),
        logger,
    )

    try:
        await dp.start_polling(bot) # запуск бота в основном потоке
    finally:
        # Корректное завершение
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        await bot.session.close()


def parse():
    parser = argparse.ArgumentParser(description='Bas Media Bot')
    parser.add_argument('--env-file', type=str, default='deployment/bot.env', help='Path to env file')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse()
    with open(args.env_file) as f:
        load_dotenv(stream=f)

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
    
    dp.include_router(AdminExportEventRouter)
    dp.include_router(AdminAddNotificationRouter)
    dp.include_router(AdminNewMemberRouter)
    dp.include_router(AdminDelMemberRouter)
    dp.include_router(AdminEventCreatingRouter)
    dp.include_router(EventCancelRouter)
    dp.include_router(EventCompleteRouter)
    dp.include_router(AdminDefaultRouter)
    dp.include_router(MemberReportAddingRouter)
    dp.include_router(MemberDefaultRouter)
    dp.include_router(UnknownRouter)

    logger = logging.getLogger("bas-bot-logger")
    logging.basicConfig(**LOGGING_KWARGS)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)  # Отключаем INFO-логирование от APScheduler

    notifServ = NotificationService(bot)

    SetBot(bot)
    # asyncio.run(notifServ.AddStorage(PgRedisStorage(pgcred, redcred)))

    dp.update.outer_middleware(LogMiddleware(logger))
    dp.update.outer_middleware(StorageMiddleware(PgRedisStorage, pgcred, redcred))
    dp.update.outer_middleware(NotificationsMiddleware(notifServ))
    dp.update.outer_middleware(AgreementMiddleware())
    dp.update.outer_middleware(AuthMiddleware())

    asyncio.run(main())
