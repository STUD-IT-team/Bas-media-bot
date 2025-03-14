
from handlers.state import AdminNewMemberStates
from handlers.usertransition import TransitToAdminDefault
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger

from re import search

AdminNewMemberRouter = Router()

async def TransitToAdminNewMember(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    logger.info("AdminNewMemberStates.EnteringName")
    await state.set_state(AdminNewMemberStates.EnteringName)
    await message.answer("Введите имя активиста: ", reply_markup=ReplyKeyboardRemove())

@AdminNewMemberRouter.message(AdminNewMemberStates.EnteringName)
async def AdminEnteringName(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    data = await state.get_data()
    data["acname"] = message.text

    await state.update_data(data)
    await state.set_state(AdminNewMemberStates.EnteringTelegramID)
    tmptext = """Введите Telegram ID пользователя (Telegram ID — это некоторое число. Для его получения нужно воспользоваться ботом (например, @GetChatID_IL_BOT))"""
    await message.answer(tmptext, reply_markup=ReplyKeyboardRemove())


@AdminNewMemberRouter.message(AdminNewMemberStates.EnteringTelegramID)
async def AdminEnteringId(message : Message, storage : BaseStorage, state : FSMContext, logger : Logger):
    try:
        chat_id = int(message.text)
    except Exception as e:
        await message.answer(f"Telegram ID пользователя должен быть как минимум числом.")
        return

    tguser = storage.GetTgUser(chat_id)
    if tguser is None or not tguser.Agreed:
        await message.answer(f"Для добавления активиста, он должен согласиться на сбор и обработку своих персональных данных согласно закону 152-ФЗ")
        return

    
    data = await state.get_data()
    logger.info("1")
    activist = storage.PutActivist(tguser.ID, data["acname"])
    logger.info("2")
    if activist:
        await message.answer(f"Пользователь с таким Telegram ID уже добавлен, его зовут {activist.Name}.")
    else:
        await message.answer(f"Пользователь {data["acname"]} добавлен.")
    logger.info("3")
    act = storage.GetActivistByChatID(message.chat.id)
    await TransitToAdminDefault(message=message, state=state, activist=act)