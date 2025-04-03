from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from utils.token import GetBotTokenEnv

bot = Bot(
    token=GetBotTokenEnv(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
