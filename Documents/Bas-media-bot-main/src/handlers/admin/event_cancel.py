from aiogram import F, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from storage.storage import BaseStorage
from logging import Logger

from handlers.state import AdminStates
from keyboards.default.admin import AdminDefaultKeyboard
#сорри что так долго не убивайте 你好^)
EventCancelRouter = Router()

@EventCancelRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.CancelEventButtonText,
)
async def AdminCancelEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    events = storage.GetActiveEvents()
    
    if not events:
        await message.answer("Нет активных мероприятий для отмены.", reply_markup=AdminDefaultKeyboard.Сreate())
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=event.Name)] for event in events] + [[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await state.set_state("AdminCancellingEvent")
    
    await message.answer("Выберите мероприятие для отмены:", reply_markup=keyboard)


@EventCancelRouter.message(StateFilter("AdminCancellingEvent"))
async def AdminCancelEventChoice(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    
    if message.text == "Отмена":
        await state.set_state(AdminStates.Default)
        await message.answer("Операция отменена.", reply_markup=AdminDefaultKeyboard.Сreate())
        return


    events = storage.GetActiveEvents()
   
    selected_event = next((event for event in events if event.Name == message.text), None)
    
    if not selected_event:
        await message.answer("Мероприятие не найдено. Попробуйте снова.", reply_markup=AdminDefaultKeyboard.Сreate())
        return

    admin = storage.GetAdminByChatID(message.chat.id)
    
    if not admin:
        await message.answer("Администратор не найден.", reply_markup=AdminDefaultKeyboard.Сreate())
        return

    storage.CancelEvent(selected_event.ID, admin.ID)
    
    await message.answer(f"Мероприятие {selected_event.Name} успешно отменено!", reply_markup=AdminDefaultKeyboard.Сreate())
    await state.set_state(AdminStates.Default)