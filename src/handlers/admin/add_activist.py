
from handlers.state import AdminNewMemberStates
from handlers.usertransition import TransitToAdminDefault
from aiogram import F
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger
from keyboards.default.admin import CancelAddMemberKeyboard
import re
from uuid import UUID, uuid4 

AdminNewMemberRouter = Router()


async def TransitToAdminNewMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    await state.set_state(AdminNewMemberStates.EnteringTelegramID)
    tmptext = "Введите никнейм пользователя (в формате @name): "
    await message.answer(tmptext, reply_markup=CancelAddMemberKeyboard.Create())

@AdminNewMemberRouter.message(
    F.text == CancelAddMemberKeyboard.CancelAddMemberButtonText,
)
async def AdminCancelAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    act = storage.GetActivistByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, activist=act)


@AdminNewMemberRouter.message(AdminNewMemberStates.EnteringTelegramID)
async def AdminEnteringId(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    username = re.search(r'@(\w+)', message.text)
    if username is None:
        await message.answer(f"Никнейм должен начинаться с @")
        return
    tguser = storage.GetTgUserByUName(username.group(1))
    if tguser is None or not tguser.Agreed:
        await message.answer(f"Для добавления пользователя, он должен написать боту и согласиться на обработку персональных данных")
        return
    data = await state.get_data()
    data["tgID"] = str(tguser.ID)
    await state.update_data(data)
    await state.set_state(AdminNewMemberStates.EnteringName)
    await message.answer("Введите имя активиста: ", reply_markup=CancelAddMemberKeyboard.Create())


@AdminNewMemberRouter.message(AdminNewMemberStates.EnteringName)
async def AdminEnteringName(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    data = await state.get_data()
    data["acname"] = message.text

    activist = storage.PutActivist(UUID(data["tgID"]), data["acname"])
    if activist:
        await message.answer(f"Пользователь с таким Telegram ID уже добавлен, его зовут {activist.Name}.")
    else:
        await message.answer(f"Пользователь {data["acname"]} добавлен.")

    act = storage.GetActivistByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, activist=act)