import asyncio
import redis
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from handlers.unknown import UnknownRouter
from utils.token import GetBotTokenEnv, GetRedisCredEnv, GetPgCredEnv
from storage.pgredis import PgRedisStorage, PostgresCredentials, RedisCredentials
from middleware.storage import StorageMiddleware


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
    
    # red = redis.Redis(
    #         host=redcred.host,
    #         port=redcred.port,
    #         username=redcred.user,
    #         password=redcred.password,
    #         db=1,
    #         decode_responses=True
    #     )
    # if not red.ping():
    #     print("Ошибка при подключении к Redis")
    #     exit(1)
    

    bot = Bot(token=GetBotTokenEnv(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=RedisStorage.from_url(f"redis://{redcred.user}:{redcred.password}@{redcred.host}:{redcred.port}/1"))
    dp.include_router(UnknownRouter)

    dp.update.outer_middleware(StorageMiddleware(PgRedisStorage, pgcred, redcred))


    asyncio.run(main())

