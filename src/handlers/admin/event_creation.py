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


AdminEventCreatingRouter = Router()


async def TransitToAdminCreatingEvent(message: Message, state: FSMContext):
    await state.set_state(AdminEventCreatingStates.EnteringName)
    await message.answer("Введите название мероприятия:", reply_markup=ReplyKeyboardRemove())


def GetTimeDateFormatDescription() -> str:
    return "{День}-{Месяц}-{Год} {Час}:{Минуты}"

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

    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringDate)
    await message.answer(f"Введите дату и время мероприятия в формате {GetTimeDateFormatDescription()} (Пример: {GetTimeDateFormatExample()})", reply_markup=ReplyKeyboardRemove())


@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringDate)
async def AdminEnterDate(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    dt, is_valid = ParseTimeDate(message.text)
    if is_valid:
        data["event-date"] = message.text
        await state.update_data(data)
        await state.set_state(AdminEventCreatingStates.EnteringPlace)
        await message.answer(f"Введите место проведения мероприятия:", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Неправильный формат даты и времени. Пожалуйста, введите дату и время в формате {GetTimeDateFormatDescription()} (Пример: {GetTimeDateFormatExample()})", reply_markup=ReplyKeyboardRemove())
    

@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringPlace)
async def AdminEnterPlace(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    data["event-place"] = message.text
    
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringPhotoCount)
    await message.answer(f"Введите количество фотографий", reply_markup=ReplyKeyboardRemove())

@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringPhotoCount)
async def AdminEnterPhotoCount(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    try:
        data["photo-count"] = int(message.text)
    except ValueError as e:
        await message.answer(f"Не число. Пожалуйста, введите число.", reply_markup=ReplyKeyboardRemove())
        raise e
    if int(message.text) < 0:
        await message.answer(f"Количество фотографий не может быть отрицательным. Пожалуйста, введите положительное число.", reply_markup=ReplyKeyboardRemove())
        raise ValueError("Negative amount input")
    
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringVideoCount)
    await message.answer(f"Введите количество видео:", reply_markup=ReplyKeyboardRemove())  


@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringVideoCount)
async def AdminEnterVideoCount(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    try:
        data["video-count"] = int(message.text)
    except ValueError as e:
        await message.answer(f"Не число. Пожалуйста, введите число.", reply_markup=ReplyKeyboardRemove())
        raise e
    if int(message.text) < 0:
        await message.answer(f"Количество фотографий не может быть отрицательным. Пожалуйста, введите положительное число.", reply_markup=ReplyKeyboardRemove())
        raise ValueError("Negative amount input")
    acts = storage.GetValidActivists()
    if len(acts) == 0:
        admin = storage.GetAdminByChatID(message.chat.id)
        await message.answer(f"Нет активистов, которые могут участвовать в мероприятии.")
        await TransitToAdminDefault(message=message, state=state, admin=admin)
        raise Exception("No valid activists")

    keyb = MemberChoosingKeyboard(acts)
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.ChoosingChief)
    await message.answer(f"Выберите главного активиста", reply_markup=keyb.Create())
    


@AdminEventCreatingRouter.message(AdminEventCreatingStates.ChoosingChief)
async def AdminEnterChief(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    chiefName = message.text
    act = storage.GetActivistByName(chiefName)
    if act is None:
        await message.answer(f"Активист с именем {chiefName} не найден.")
        acts = storage.GetValidActivists()
        keyb = MemberChoosingKeyboard(acts)
        await message.answer(f"Выберите главного активиста", reply_markup=keyb.Create())
        raise ValueError(f"Chief {chiefName} not found")
    data["event-chief"] = act.ID.hex
    data["event-activists"] = []

    acts = storage.GetValidActivists()
    keyb = MemberChoosingCancelKeyboard(acts, exceptIDs=[act.ID])
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.ChoosingMembers)
    await message.answer(f"Выберите активистов", reply_markup=keyb.Create())
    


@AdminEventCreatingRouter.message(AdminEventCreatingStates.ChoosingMembers)
async def AdminEnterMembers(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    if message.text == MemberChoosingCancelKeyboard.StopActivistChoosingButtonText:
        creator = storage.GetAdminByChatID(message.chat.id)
        try:
            await PutEvent(storage, state, creator)
        except BaseException as e:
            await message.answer(f"Произошла ошибка при создании мероприятия.")
        admin = storage.GetAdminByChatID(message.chat.id)
        await message.answer(f"Мероприятие {data['event-name']} успешно создано!")
        await TransitToAdminDefault(message=message, state=state, admin=admin)
        return
    else:
        activistName = message.text
        act = storage.GetActivistByName(activistName)
        if act is None:
            await message.answer(f"Активист с именем {activistName} не найден.")
            acts = storage.GetValidActivists()
            keyb = MemberChoosingCancelKeyboard(acts, exceptIDs=([UUID(hex=data["event-chief"])] + [UUID(hex=actID) for actID in data["event-activists"]]))
            await message.answer(f"Выберите активистов", reply_markup=keyb.Create())
            raise ValueError(f"Activist {activistName} not found")
        
        
        data["event-activists"].append(act.ID.hex)
        acts = storage.GetValidActivists()
        keyb = MemberChoosingCancelKeyboard(acts, exceptIDs=([UUID(hex=data["event-chief"])] + [UUID(hex=actID) for actID in data["event-activists"]]))
        await state.update_data(data)
        await message.answer(f"Выберите еще активистов", reply_markup=keyb.Create())

async def PutEvent(storage: BaseStorage, state: FSMContext, creator: Admin):
    data = await state.get_data()
    eventID = uuid4()

    chief = EventChief(
        ID = uuid4(),
        EventID = eventID,
        Activist = storage.GetActivistByID(UUID(hex=data['event-chief']))
    )
    members = [
        EventActivist(
            ID = uuid4(),
            EventID = eventID,
            Activist = storage.GetActivistByID(UUID(hex=act))
            ) 
        for act in data["event-activists"]
    ]

    dt, _ = ParseTimeDate(data["event-date"])
    event = Event(
        ID = eventID,
        Name=data["event-name"], 
        Date=dt, 
        Place=data["event-place"],
        PhotoCount=data["photo-count"], 
        VideoCount=data["video-count"], 
        Chief=chief, 
        Activists=members,
        CreatedAt = datetime.now(),
        CreatedBy = creator.ID,
    )
    storage.PutEvent(event)








