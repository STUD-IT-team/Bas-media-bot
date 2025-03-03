from handlers.state import AdminStates
from handlers.usertransition import TransitToAdminDefault
from keyboards.default.admin import AdminDefaultKeyboard

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger

AdminDefaultRouter = Router()

@AdminDefaultRouter.message(AdminStates.Default)
async def AdminUnknown(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer("Не понял введённую команду")
    activist = storage.GetActivistByChatID(message.chat.id)
    if activist is not None:
        await message.answer(f"Админ, {activist.Name}! Что хотите сделать?", reply_markup=AdminDefaultKeyboard.Сreate())
