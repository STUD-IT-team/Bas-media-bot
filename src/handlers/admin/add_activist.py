
from handlers.state import AdminNewMemberStates
from handlers.usertransition import TransitToAdminDefault
from aiogram import F
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f
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
    or_f(
        AdminNewMemberStates.EnteringTelegramID,
        AdminNewMemberStates.EnteringName
    ),
    F.text == CancelAddMemberKeyboard.CancelAddMemberButtonText
)
async def AdminCancelAddMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    admin = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, admin=admin)


@AdminNewMemberRouter.message(AdminNewMemberStates.EnteringTelegramID)
async def AdminEnteringId(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    username = re.search(r'@(\w+)', message.text)
    if username is None:
        await message.answer(f"Никнейм должен начинаться с @")
        tmptext = "Введите никнейм пользователя (в формате @name): "
        await message.answer(tmptext, reply_markup=CancelAddMemberKeyboard.Create())
        return
    tguser = storage.GetTgUserByUName(username.group(1))
    if tguser is None or not tguser.Agreed:
        await message.answer(f"Для добавления пользователя, он должен написать боту и согласиться на обработку персональных данных")
        admin = storage.GetAdminByChatID(message.chat.id)
        await TransitToAdminDefault(message=message, state=state, admin=admin)
        return
    
    activist = storage.GetActivistByTgUserID(tguser.ID)
    if activist:
        await message.answer(f"Пользователь с ником @{tguser.Username} уже добавлен, его зовут {activist.Name}.")
        admin = storage.GetAdminByChatID(message.chat.id)
        await TransitToAdminDefault(message=message, state=state, admin=admin)
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

    storage.PutActivist(UUID(data["tgID"]), data["acname"])
    await message.answer(f"Пользователь {data["acname"]} добавлен.")

    admin = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, admin=admin)
