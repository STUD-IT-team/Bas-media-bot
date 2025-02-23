import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from handlers.state import AdminStates, MemberStates
from storage.storage import BaseStorage



UnknownRouter = Router()

@UnknownRouter.message(any_state)
async def UnknownMessage(message : Message, storage : BaseStorage, state : FSMContext):
    chatID = message.chat.id
    username = message.chat.username

    try:
        storage.PutTgUser(chatID, username)
    except Exception as e:
        await message.answer(f"Внутренняя ошибка сервера {str(e)}")
        return
    try:
        activist = storage.GetActivistByChatID(chatID)
    except Exception as e:
        await message.answer(f"Внутренняя ошибка сервера {str(e)}")
        return
    
    try:
        admin = storage.GetAdminByChatID(chatID)
    except Exception as e:
        await message.answer(f"Внутренняя ошибка сервера {str(e)}")
        return
    
    if activist is None or not activist.Valid:
        await message.answer("Не могу найти вас в своих базах, если это ошибка - напишите администратору")
        return
    elif admin is None:
        await message.answer(f"Активист, {activist.Name}! Что хотите сделать?")
        await state.set_state(MemberStates.Default)
    else:
        await message.answer(f"Администратор, {activist.Name}! Что хотите сделать?")
        await state.set_state(AdminStates.Default)

    
    
