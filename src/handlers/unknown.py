from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from handlers.state import AdminStates, MemberStates
from storage.storage import BaseStorage
from logging import Logger

class UnknownRouterError(Exception):
    def __str__(self):
        return "user got in unknown router"

UnknownRouter = Router()

@UnknownRouter.message(any_state)
async def UnknownMessage(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer("Что-то пошло не так... Вы не должны были сюда попасть... Позовите админа...")
    logger.critical(f"{message.chat.id}:{message.chat.username} got in unknown router state")
    raise UnknownRouterError
    
    
