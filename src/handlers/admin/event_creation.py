from models.event import Event, EventActivist, EventChief
from models.activist import Activist, Admin
from handlers.state import AdminEventCreatingStates
from handlers.usertransition import TransitToAdminDefault
from keyboards.default.admin import AdminDefaultKeyboard
from keyboards.activist.choosing import MemberChoosingCancelKeyboard
from keyboards.confirmation.yesno import YesNoKeyboard
from keyboards.confirmation.cancel import CancelKeyboard
from datetime import datetime
from utils.strings import EnumerateStrings, NewlineJoin
from utils.date_time import GetTimeDateFormatDescription, GetTimeDateFormatExample, ParseTimeDate

from uuid import UUID, uuid4
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger
from aiogram import F
from datetime import datetime, timedelta

from notifications.NotificationService import NotificationService
from models.notification import MapperNotification, TypeNotif

AdminEventCreatingRouter = Router()

async def TransitToAdminCreatingEvent(message: Message, state: FSMContext):
    await state.set_state(AdminEventCreatingStates.EnteringName)
    await message.answer("Введите название мероприятия:", reply_markup=CancelKeyboard.Create())

@AdminEventCreatingRouter.message(
    AdminEventCreatingStates(),
    F.text == CancelKeyboard.CancelButtonText
)
async def AdminCancelCreatingEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    admin = storage.GetAdminByChatID(message.chat.id)
    await message.answer("Отмена создания мероприятия")
    await TransitToAdminDefault(message, state, admin)

@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringName)
async def AdminCreateEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    data["event-name"] = message.text

    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringDate)
    await message.answer(f"Введите дату и время мероприятия в формате {GetTimeDateFormatDescription()} (Пример: {GetTimeDateFormatExample()})", reply_markup=CancelKeyboard.Create())


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
        await message.answer(f"Неправильный формат даты и времени. Пожалуйста, введите дату и время в формате {GetTimeDateFormatDescription()} (Пример: {GetTimeDateFormatExample()})", reply_markup=CancelKeyboard.Create())
    

@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringPlace)
async def AdminEnterPlace(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    data["event-place"] = message.text
    
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringPhotoCount)
    await message.answer(f"Введите количество фотографий", reply_markup=CancelKeyboard.Create())

@AdminEventCreatingRouter.message(AdminEventCreatingStates.EnteringPhotoCount)
async def AdminEnterPhotoCount(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    try:
        data["photo-count"] = int(message.text)
    except ValueError as e:
        await message.answer(f"Не число. Пожалуйста, введите число.", reply_markup=CancelKeyboard.Create())
        raise e
    if int(message.text) < 0:
        await message.answer(f"Количество фотографий не может быть отрицательным. Пожалуйста, введите положительное число.", reply_markup=ReplyKeyboardRemove())
        raise ValueError("Negative amount input")
    
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.EnteringVideoCount)
    await message.answer(f"Введите количество видео:", reply_markup=CancelKeyboard.Create())  


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

    logger.info(f"LEN ACTS ------ {len(acts)}\n\n")
    logger.info([a.Name for a in acts])
    keyb = MemberChoosingCancelKeyboard(acts)
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
        keyb = MemberChoosingCancelKeyboard(acts)
        await message.answer(f"Выберите главного активиста", reply_markup=keyb.Create())
        raise ValueError(f"Chief {chiefName} not found")
    data["event-chief"] = act.ID.hex
    data["event-activists"] = []
    
    
    keyb = MemberChoosingCancelKeyboard(GetNotChosenActivists(storage, data))
    await state.update_data(data)
    await state.set_state(AdminEventCreatingStates.ChoosingMembers)
    await message.answer(f"Выберите активистов", reply_markup=keyb.Create())
    


@AdminEventCreatingRouter.message(
    AdminEventCreatingStates.ChoosingMembers,
    F.text == MemberChoosingCancelKeyboard.StopActivistChoosingButtonText
)
async def AdminEnterMembersStop(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    eventName = data["event-name"]
    eventDate = data["event-date"]
    eventPlace = data["event-place"]
    eventPhotoCount = data["photo-count"]
    eventVideoCount = data["video-count"]

    eventChiefID = UUID(hex=data["event-chief"])
    eventActivistsIds = [UUID(hex=actID) for actID in data["event-activists"]]

    eventChief = storage.GetActivistByID(eventChiefID)
    eventActivists = [storage.GetActivistByID(actID) for actID in eventActivistsIds]
    await message.answer(NewlineJoin(
        f"<b>Название:</b> {eventName}",
        f"<b>Дата:</b> {eventDate}",
        f"<b>Место проведения:</b> {eventPlace}",
        f"<b>Количество фотографий:</b> {eventPhotoCount}",
        f"<b>Количество видео:</b> {eventVideoCount}",
        f"<b>Главный активист:</b> {eventChief.Name}",
        f"<b>Активисты:</b>",
        *EnumerateStrings(*[act.Name for act in eventActivists]),
        ""
        "Данные верны?"
    ), reply_markup=YesNoKeyboard.Create())
    await state.set_state(AdminEventCreatingStates.Confirmation)

def GetNotChosenActivists(storage : BaseStorage, context : dict[str, any]) -> list[Activist]:
    acts = storage.GetValidActivists()
    chosenEventActivistsIds = [UUID(hex=actID) for actID in context["event-activists"]]
    chosenEventActivistsIds.append(UUID(hex=context["event-chief"]))
    acts = list(filter(lambda a: a.ID not in chosenEventActivistsIds, acts))
    return acts

@AdminEventCreatingRouter.message(AdminEventCreatingStates.ChoosingMembers)
async def AdminEnterMembers(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    activistName = message.text
    act = storage.GetActivistByName(activistName)
    if act is None:
        await message.answer(f"Активист с именем {activistName} не найден.")
        keyb = MemberChoosingCancelKeyboard(GetNotChosenActivists(storage, data))
        await message.answer(f"Выберите активистов", reply_markup=keyb.Create())
        raise ValueError(f"Activist {activistName} not found")
    
    data["event-activists"].append(act.ID.hex)

    keyb = MemberChoosingCancelKeyboard(GetNotChosenActivists(storage, data))
    await state.update_data(data)
    await message.answer(f"Выберите еще активистов", reply_markup=keyb.Create())

@AdminEventCreatingRouter.message(
    AdminEventCreatingStates.Confirmation,
    F.text == YesNoKeyboard.YesButtonText
)
async def AdminConfirmedEvent(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger, notifServ: NotificationService):
    data = await state.get_data()
    creator = storage.GetAdminByChatID(message.chat.id)
    try:
        event = await PutEvent(storage, state, creator)
        await message.answer(f"Мероприятие {data['event-name']} успешно создано!")
    except BaseException as e:
        # TODO: Подумать над более подробной обработкой ошибок
        logger.error(f"Error occurred while creating event: {str(e)}")
        await message.answer(f"Произошла ошибка при создании мероприятия.")
        await TransitToAdminDefault(message=message, state=state, admin=creator)
        return

    eventChiefID = UUID(hex=data["event-chief"])
    eventActivistsIds = [UUID(hex=actID) for actID in data["event-activists"]]
    eventChief = storage.GetActivistByID(eventChiefID)
    eventActivists = [storage.GetActivistByID(actID) for actID in eventActivistsIds]
    chatIDs = [eventChief.ChatID] + [a.ChatID for a in eventActivists]

    try:
        for cntDays in [1, 3]:
            if event.Date - timedelta(days=cntDays) >= datetime.now():
                n = MapperNotification.CreateNotification(
                    TypeNotif.EVENT_REMINDER, 
                    uuid4(),
                    "",
                    datetime.now() + timedelta(days=cntDays),
                    chatIDs,
                    event)
                await notifServ.AddNotification(n)
        n = MapperNotification.CreateNotification(
            TypeNotif.ASSIGNMENT, 
            uuid4(),
            "",
            datetime.now(),
            chatIDs,
            event)
        await notifServ.AddNotification(n)
    except BaseException as e:
        logger.error(f"Error occurred while creating notification: {str(e)}")
        await message.answer(f"Произошла ошибка при создании уведомлениий о событии.")
        await TransitToAdminDefault(message=message, state=state, admin=creator)
        return

    await TransitToAdminDefault(message=message, state=state, admin=creator)


@AdminEventCreatingRouter.message(
    AdminEventCreatingStates.Confirmation,
    F.text == YesNoKeyboard.NoButtonText
)
async def AdminCanceledEventCreation(message: Message, storage: BaseStorage, state: FSMContext, logger: Logger):
    admin = storage.GetAdminByChatID(message.chat.id)
    await message.answer(f"Мероприятие не создано.")
    await TransitToAdminDefault(message=message, state=state, admin=admin)


async def PutEvent(storage: BaseStorage, state: FSMContext, creator: Admin) -> Event:
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

    creatorActivistID = storage.GetActivistByChatID(creator.ChatID)
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
        CreatedBy = creatorActivistID.ID,
    )
    storage.PutEvent(event)

    return event








