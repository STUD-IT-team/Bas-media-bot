from models.event import Event, EventActivist, EventChief
from models.activist import Activist, Admin
from handlers.state import AdminEventCreatingStates
from handlers.usertransition import TransitToAdminDefault
from keyboards.default.admin import AdminDefaultKeyboard
from keyboards.activist.choosing import MemberChoosingCancelKeyboard, MemberChoosingKeyboard
from utils.strings import NewlineJoin, EnumerateStrings
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
        await message.answer(NewlineJoin(
        f"<b>{event.Name} -- {event.Date.strftime('%d-%m-%Y %H:%M')}</b>",
        f"<b>Количество фото:</b> {event.PhotoCount}",
        f"<b>Количество видео:</b> {event.VideoCount}",
        f"<b>Главорг:</b> {event.Chief.Activist.Name}",
        f"<b>Количество активистов:</b> {len(event.Activists)}",
        *EnumerateStrings(*[act.Activist.Name for act in event.Activists]),
        ))
    admin = storage.GetAdminByChatID(message.chat.id)
    await TransitToAdminDefault(message, state, admin)
