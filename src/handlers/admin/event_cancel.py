from aiogram import F, Router
from aiogram.types import  Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger

from handlers.usertransition import TransitToAdminDefault
from handlers.state import AdminStates
from keyboards.default.admin import AdminDefaultKeyboard
from keyboards.events.activeevents import ActiveEventsKeyboard

EventCancelRouter = Router()


async def CancelOperationHandle(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    admin = storage.GetAdminByChatID(message.chat.id)
    await message.answer("Операция отменена.", reply_markup=AdminDefaultKeyboard.Create())
    await TransitToAdminDefault(message, state, admin)


@EventCancelRouter.message(
    AdminStates.AdminCancellingEvent,
    F.text == "Отмена операции"
)
async def CancelEventOperation(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    await CancelOperationHandle(message,storage,state,logger)


@EventCancelRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.CancelEventButtonText,
)
async def AdminCancelEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):

    events = storage.GetActiveEvents()
    if not events:
        await message.answer("Нет активных мероприятий для отмены.", reply_markup=AdminDefaultKeyboard.Create())
        await TransitToAdminDefault(message, state, admin = storage.GetAdminByChatID(message.chat.id))
        return

    await state.set_state(AdminStates.AdminCancellingEvent)
    await message.answer("Выберите мероприятие для отмены:", reply_markup=ActiveEventsKeyboard(events).Create())


@EventCancelRouter.message(AdminStates.AdminCancellingEvent)
async def AdminCancelEventChoice(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):

    admin = storage.GetAdminByChatID(message.chat.id)
    if not admin:
        await message.answer("Администратор не найден.", reply_markup=AdminDefaultKeyboard.Create())
        return
    
    selected_event = storage.GetActiveEventByName(message.text)
   
    if not selected_event:
        await message.answer("Мероприятие не найдено.", reply_markup=AdminDefaultKeyboard.Create())
        await TransitToAdminDefault(message, state, admin)
        return

    storage.CancelEvent(selected_event.ID, admin.ID)

    await message.answer(f"Мероприятие {selected_event.Name} успешно отменено!", reply_markup=AdminDefaultKeyboard.Create())
    await TransitToAdminDefault(message, state, admin)
