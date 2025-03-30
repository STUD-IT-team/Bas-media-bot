from aiogram import F, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from storage.storage import BaseStorage
from logging import Logger

from handlers.state import AdminStates
from keyboards.default.admin import AdminDefaultKeyboard

# Файл для обработки отмены мероприятий администратором через выбор из списка активных мероприятий

EventCancelRouter = Router()

# Хендлер для перехода к выбору мероприятия для отмены
@EventCancelRouter.message(
    AdminStates.Default,
    F.text == AdminDefaultKeyboard.CancelEventButtonText,
)
async def AdminCancelEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    # Получаем список активных мероприятий
    events = storage.GetActiveEvents()
    
    # Если активных мероприятий не найдено, информируем пользователя и возвращаемся в главное меню
    if not events:
        await message.answer("Нет активных мероприятий для отмены.", reply_markup=AdminDefaultKeyboard.Сreate())
        return

    # Формируем клавиатуру с кнопками, где каждая кнопка содержит название активного мероприятия
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=event.Name)] for event in events] + [[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # Устанавливаем состояние FSM для выбора мероприятия на отмену
    await state.set_state("AdminCancellingEvent")
    
    # Отправляем сообщение с инструкцией для выбора мероприятия для отмены
    await message.answer("Выберите мероприятие для отмены:", reply_markup=keyboard)


# Хендлер для обработки выбора мероприятия для отмены
@EventCancelRouter.message(StateFilter("AdminCancellingEvent"))
async def AdminCancelEventChoice(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    # Если пользователь нажал кнопку отмены, выходим из состояния выбора и возвращаемся в главное меню
    if message.text == "Отмена":
        await state.set_state(AdminStates.Default)
        await message.answer("Операция отменена.", reply_markup=AdminDefaultKeyboard.Сreate())
        return

    # Получаем список всех активных мероприятий
    events = storage.GetActiveEvents()
    
    # Находим мероприятие, название которого соответствует введённому пользователем
    selected_event = next((event for event in events if event.Name == message.text), None)
    
    # Если мероприятие не найдено, информируем пользователя и возвращаемся в главное меню
    if not selected_event:
        await message.answer("Мероприятие не найдено. Попробуйте снова.", reply_markup=AdminDefaultKeyboard.Сreate())
        return

    # Получаем данные администратора по chat_id из сообщения
    admin = storage.GetAdminByChatID(message.chat.id)
    
    # Если данные администратора не найдены, информируем пользователя и возвращаемся в главное меню
    if not admin:
        await message.answer("Администратор не найден.", reply_markup=AdminDefaultKeyboard.Сreate())
        return

    # Вызываем метод CancelEvent для отмены выбранного мероприятия, передавая идентификаторы мероприятия и администратора
    storage.CancelEvent(selected_event.ID, admin.ID)
    
    # Информируем пользователя об успешной отмене мероприятия и возвращаем состояние FSM в режим по умолчанию
    await message.answer(f"Мероприятие {selected_event.Name} успешно отменено!", reply_markup=AdminDefaultKeyboard.Сreate())
    await state.set_state(AdminStates.Default)