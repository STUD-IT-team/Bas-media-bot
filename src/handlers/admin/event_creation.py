from handlers.state import AdminEventCreatingStates
from handlers.usertransition import TransitToAdminDefault
from keyboards.default.admin import AdminDefaultKeyboard
from datetime import datetime

from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger

AdminEventCreatingRouter = Router()


async def TransitToAdminCreatingEvent(message: Message, state: FSMContext):
    await state.set_state(AdminEventCreatingStates.EnteringName)
    await message.answer("Введите название мероприятия:", reply_markup=ReplyKeyboardRemove())
    await state.set_data({"event-name": ""})


def GetTimeDateFormatDescription() -> str:
    return "(День)-(Месяц)-(Год) (Час):(Минуты)"

def GetTimeDateFormatExample() -> str:
    return "15-05-2022 18:00"

def ParseTimeDate(dtstr : str) -> (datetime, bool):
    try:
        dt = datetime.strptime(dtstr, "%d-%m-%Y %H:%M")
        return dt, True
    except ValueError:
        return None, False


@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringName)
async def AdminCreateEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    data["event-name"] = message.text
    await message.answer(f"Введите дату и время мероприятия в формате {GetTimeDateFormatDescription()} (Пример: {GetTimeDateFormatExample})", reply_markup=ReplyKeyboardRemove())
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringDate)


@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringDate)
async def AdminEnterDate(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    dt, is_valid = ParseTimeDate(message.text)
    if is_valid:
        data["event-date"] = dt
        await message.answer(f"Введите место проведения мероприятия:", reply_markup=ReplyKeyboardRemove())
        await state.update_data(data)
        await state.set_state(AdminEventCreatingStates.EnteringPlace)
    else:
        await message.answer(f"Неправильный формат даты и времени. Пожалуйста, введите дату и время в формате {GetTimeDateFormatDescription()} (Пример: {GetTimeDateFormatExample})", reply_markup=ReplyKeyboardRemove())
    

@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringPlace)
async def AdminEnterPlace(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    data["event-place"] = message.text
    await message.answer(f"Введите количество фотографий:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringPhotoCount)


@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringPhotoCount)
async def AdminEnterPhotoCount(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    try:
        data["photo-count"] = int(message.text)
    except ValueError as e:
        await message.answer(f"Неправильное число. Пожалуйста, введите число.", reply_markup=ReplyKeyboardRemove())
        raise e
    await message.answer(f"Введите количество видео:", reply_markup=ReplyKeyboardRemove())
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringVideoCount)


@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringVideoCount)
async def AdminEnterVideoCount(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    try:
        data["video-count"] = int(message.text)
        await message.answer(f"Выберите участников мероприятия:", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=f"Участник {i+1}") for i in range(data['photo-count'])]], resize_keyboard=True))
        await state.update_data(data)
        await state.set_state(AdminEventCreatingStates.ChoosingMembers)
    except ValueError as e:
        await message.answer(f"Неправильное число. Пожалуйста, введите число.", reply_markup=ReplyKeyboardRemove())
        raise e
    await state.set_state(AdminEventCreatingStates.ChoosingMembers)
    await TransitToAdminDefault(message=message, state=state, activist=storage.GetActivistByChatID(message.chat.id))
    await state.set_state(AdminEventCreatingStates.Default)
    await message.answer(f"Мероприятие '{data['event-name']}' успешно создано!")




