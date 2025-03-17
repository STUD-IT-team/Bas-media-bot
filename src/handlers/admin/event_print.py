from models.event import Event, EventActivist, EventChief
from models.activist import Activist, Admin
from handlers.state import AdminEventCreatingStates
from handlers.usertransition import TransitToAdminDefault
from keyboards.default.admin import AdminDefaultKeyboard
from keyboards.activist.choosing import MemberChoosingCancelKeyboard, MemberChoosingKeyboard
from datetime import datetime

from uuid import UUID, uuid4
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger


async def AdminPrintEvents(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    try:
        events = storage.GetActiveEvents()
    except:
        await message.answer("Ошибка при получении списка активных мероприятий")
        raise

    await message.answer("<b>Список активных мероприятий</b>")
    for event in events:
        await message.answer(f"""
        <b>{event.Name} -- {event.Date.strftime('%d-%m-%Y %H:%M')}</b>
        <b>Количество фото:</b> {event.PhotoCount}
        <b>Количество видео:</b> {event.VideoCount}
        <b>Главорг:</b> {event.Chief.Activist.Name}
        <b>Количество активистов:</b> {len(event.Activists)}
        {'\n'.join([str(i + 1) + '. ' + event.Activists[i].Activist.Name for i in range(len(event.Activists))])}
        """)
    admin = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message, state, admin)




