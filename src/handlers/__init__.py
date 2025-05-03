

from aiogram import Dispatcher

from aiogram.fsm.storage.redis import RedisStorage

from storage import redcred
from .prepare_dispatcher import prepare_dispatcher



dp = Dispatcher(
    storage=RedisStorage.from_url(
        f"redis://{redcred.user}:{redcred.password}@{redcred.host}:{redcred.port}/1"
    )
)

# dp = Dispatcher(bot)
prepare_dispatcher(dp)
