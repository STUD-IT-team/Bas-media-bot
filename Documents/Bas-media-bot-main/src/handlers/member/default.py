from handlers.state import MemberStates

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger

from keyboards.default.member import MemberDefaultKeyboard


MemberDefaultRouter = Router()

@MemberDefaultRouter.message(MemberStates.Default)
async def MemberUnknown(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer("Не понял введённую команду")
    activist = storage.GetActivistByChatID(message.chat.id)
    if activist is not None:
        await message.answer(f"Активист, {activist.Name}! Что хотите сделать?", reply_markup=MemberDefaultKeyboard.Сreate())