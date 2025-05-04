from aiogram import F, Router
from aiogram.types import  Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger

from handlers.usertransition import TransitToAdminDefault
from handlers.state import AdminStates
from keyboards.default.admin import AdminDefaultKeyboard
from keyboards.events.activeevents import ActiveEventsKeyboard



EventCompleteRouter = Router()

async def CompleteOperationHandle(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    admin = storage.GetAdminByChatID(message.chat.id)
    await message.answer("Операция отменена.", reply_markup=AdminDefaultKeyboard.Create())
    await TransitToAdminDefault(message, state, admin)

@EventCompleteRouter.message(
    AdminStates.AdminCompletingEvent,
    F.text == "Отмена операции"
)
async def CompleteEventOperation(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    await CompleteOperationHandle(message,storage,state,logger)


@EventCompleteRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.CompleteEventButtonText,
)
async def AdminCompleteEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):

    events = storage.GetActiveEvents()
    if not events:
        await message.answer("Нет активных мероприятий для завершения.", reply_markup=AdminDefaultKeyboard.Create())
        await TransitToAdminDefault(message, state, admin = storage.GetAdminByChatID(message.chat.id))
        return
    
    await state.set_state(AdminStates.AdminCompletingEvent)
    await message.answer("Выберите мероприятие для завершения:", reply_markup=ActiveEventsKeyboard(events).Create())


@EventCompleteRouter.message(AdminStates.AdminCompletingEvent)
async def AdminCompleteEventChoice(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):

    admin = storage.GetAdminByChatID(message.chat.id)
    if not admin:
        await message.answer("Администратор не найден.", reply_markup=AdminDefaultKeyboard.Create())
        return
    
    selected_event = storage.GetActiveEventByName(message.text)

    if not selected_event:
        await message.answer("Мероприятие не найдено.", reply_markup=AdminDefaultKeyboard.Create())
        await TransitToAdminDefault(message, state, admin)
        return

    storage.CompleteEvent(selected_event.ID, admin.ID)

    await message.answer(f"Мероприятие {selected_event.Name} успешно завершено!", reply_markup=AdminDefaultKeyboard.Create())
    await TransitToAdminDefault(message, state, admin)