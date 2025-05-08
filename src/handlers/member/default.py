from handlers.state import MemberStates
from handlers.member.list_of_events import getListOfEvents

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger
from aiogram import F
from keyboards.default.member import MemberDefaultKeyboard

MemberDefaultRouter = Router()


@MemberDefaultRouter.message(
    MemberStates.Default,
    F.text == MemberDefaultKeyboard.EventInfoButtonText,
)
async def ActivistEventsInfo(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await getListOfEvents(message, state, storage)


@MemberDefaultRouter.message(MemberStates.Default)
async def MemberUnknown(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer("Не понял введённую команду")
    activist = storage.GetActivistByChatID(message.chat.id)
    if activist is not None:
        await message.answer(f"Активист, {activist.Name}! Что хотите сделать?", reply_markup=MemberDefaultKeyboard.Create())
