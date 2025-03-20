from handlers.state import AdminStates
from handlers.usertransition import TransitToAdminDefault
from keyboards.default.admin import AdminDefaultKeyboard
from handlers.admin.event_creation import TransitToAdminCreatingEvent
from handlers.admin.event_print import AdminPrintEvents
from handlers.admin.add_activist import TransitToAdminNewMember
from handlers.admin.del_activist import TransitToAdminDelMember

from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger



AdminDefaultRouter = Router()


@AdminDefaultRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.AddEventButtonText,
)
async def AdminAddEvent(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await TransitToAdminCreatingEvent(message, state)



@AdminDefaultRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.InfoEventButtonText,
)
async def AdminInfoEvent(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await AdminPrintEvents(message, storage, state, logger)


@AdminDefaultRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.AddMemberButtonText,
)
async def AdminAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await TransitToAdminNewMember(message, storage, state, logger)

@AdminDefaultRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.DeleteMemberButtonText,
)
async def AdminDelMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await TransitToAdminDelMember(message, storage, state, logger)

@AdminDefaultRouter.message(
    AdminStates.Default,
)
async def AdminUnknown(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await message.answer("Не понял введённую команду")
    activist = storage.GetActivistByChatID(message.chat.id)
    if activist is not None:
        await message.answer(f"Админ, {activist.Name}! Что хотите сделать?", reply_markup=AdminDefaultKeyboard.Сreate())
