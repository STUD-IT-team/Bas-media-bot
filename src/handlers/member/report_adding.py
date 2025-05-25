from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from storage.storage import BaseStorage

# Переход в дефолтную стейт машину:
from handlers.usertransition import TransitToMemberDefault

# Стейты:
from handlers.state import MemberReportAddingStates

# Клавиатуры и кнопки:
from keyboards.report_adding.cancel_button import CancelButton
from keyboards.report_adding.activist_events import ActivistEventsKeyboard
from keyboards.report_adding.cancel_link import CancelLinkKeyboard
from keyboards.report_adding.report_type import ReportTypeKeyboard
from keyboards.report_adding.report_confirm import ReportConfirmKeyboard

# Модели:
from models.activist import Activist
from models.event import EventForActivist

# Дополнительно:
from utils.strings import NewlineJoin, IsCorrectReportUrl
from utils.date_time import TIME_FORMAT

MemberReportAddingRouter = Router()


# Получение активиста с проверкой и выводом ошибки в чат
async def getActivist(message: Message, storage: BaseStorage) -> Activist:
    try:
        activist = storage.GetActivistByChatID(message.chat.id)

        if activist is None: # Активист не может быть None, Должна была сработать AuthMiddleware
            raise ValueError("activist can't be None")
    except:
        message.answer("Ошибка при получении информации о вашей роли.")
        raise

    return activist


# Создание актуальной клавиатуры мероприятий с выводом ошибки в чат
async def getActivistEventsKeyboard(message: Message, storage: BaseStorage, activist: Activist) -> ReplyKeyboardMarkup:
    try:
        if not isinstance(activist, Activist):
            raise ValueError("activist should be instance of Activist")

        # Нужно заменить на Get Active Events By Activist ID.
        # Иначе будут выводится закрытые и отменённые меро.
        activistEvents = storage.GetEventsByActivistID(activist.ID)
        activistEventsKeyboard = ActivistEventsKeyboard(activistEvents)
    except:
        message.answer("Ошибка при получении информации о ваших мероприятиях.")
        raise

    return activistEventsKeyboard


# Ручка перехода в составление отчёта
async def TransitToMemberReportAdding(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    await state.set_state(MemberReportAddingStates.ChoosingEvent)

    activist = await getActivist(message, storage)

    activistEventsKeyboard = await getActivistEventsKeyboard(message, storage, activist)

    await message.answer("Выберите мероприятие для составления отчёта:", \
            reply_markup=activistEventsKeyboard.Create())
    
    return


# Отмена составления отчёта
@MemberReportAddingRouter.message(
    MemberReportAddingStates(),
    F.text == CancelButton.CancelButtonText
)
async def CancelReportAdding(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    await message.answer("Создание отчёта отменено.", reply_markup=ReplyKeyboardRemove())
    
    activist = await getActivist(message, storage)

    await TransitToMemberDefault(message=message, state=state, activist=activist)
    
    return

# Выбор мероприятия для составления отчёта
@MemberReportAddingRouter.message(
    MemberReportAddingStates.ChoosingEvent
)
async def MemberChoosingEvent(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    data = await state.get_data()
    eventName = message.text

    activist = await getActivist(message, storage)
    
    try:
        # Заменить на Get Active Event By Chat ID And Name.
        # Иначе пользователь может получить не своё мероприятие.
        # А также тут есть потенциальная SQL инъекция.
        event = storage.GetActiveEventByName(eventName)
    except:
        message.answer("Ошибка при получении информации о мероприятии.")
        raise
    
    # Меро не найдено
    if event is None:
        # Произвожу актуализацию списка мероприятий.
        activistEventsKeyboard = await getActivistEventsKeyboard(message, storage, activist)

        await message.answer(f"Мероприятие с названием '{eventName}' не найдено. Попробуйте ещё раз.", \
                    reply_markup=activistEventsKeyboard.Create())
        return

    # Меро найдено:
    await message.answer(NewlineJoin(
        "Мероприятие найдено!",
        "",
        f"Название: <b>{event.Name}</b>",
        "Ответственный: <b>{event.Chief.Name} @{event.Chief.Username}</b>", # код будет работать с EventForActivist а не с Event
        f"Дата и время: <b>{event.Date.strftime(TIME_FORMAT)}</b>",
        f"Количество Фото: <b>{str(event.PhotoCount)}</b>",
        f"Количество Видео: <b>{str(event.VideoCount)}</b>"
    ), reply_markup=ReplyKeyboardRemove())

    await message.answer("Выберите тип отчёта:", reply_markup=ReportTypeKeyboard.Create())

    data["event-id"] = str(event.ID) # Должен бы быть event-member-id
    await state.update_data(data)
    await state.set_state(MemberReportAddingStates.ChoosingType)

    return


# Выбор типа отчёта
@MemberReportAddingRouter.message(
    MemberReportAddingStates.ChoosingType,
    or_f(
        F.text == ReportTypeKeyboard.PhotoButtonText, 
        F.text == ReportTypeKeyboard.VideoButtonText
        )
)
async def MemberChoosingReportType(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    data = await state.get_data()
    reportType = message.text

    await message.answer(f"Выбран тип отчёта: {reportType}.", reply_markup=ReplyKeyboardRemove())

    await message.answer(NewlineJoin(
        "Отправьте ссылку на Яндекс Диск с отчётом.",
        "",
        "<b>Формат: https://disk.yandex.ru/d/randomletters</b>"
    ), reply_markup=CancelLinkKeyboard.Create())

    # Переписать это когда будут нормальные модели:
    if reportType == ReportTypeKeyboard.PhotoButtonText:
        data["report-type"] = "photo"
    else:
        data["report-type"] = "video"
    
    await state.update_data(data)
    await state.set_state(MemberReportAddingStates.EnteringLink)

    return


# Ввод ссылки на отчёт
@MemberReportAddingRouter.message(
    MemberReportAddingStates.EnteringLink
)
async def MemberEnteringLink(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    data = await state.get_data()
    reportURL = message.text

    if not IsCorrectReportUrl(reportURL):
        await message.answer("Ссылка не соответствует формату, попробуйте ещё раз.")
        
        return
    
    await message.answer("Подтвердите информацию: тут будет информация", reply_markup=ReportConfirmKeyboard.Create()) # черновое
    
    data["report-url"] = reportURL
    await state.update_data(data)
    await state.set_state(MemberReportAddingStates.Confirmation)

    return


# Подтверждение отчёта
@MemberReportAddingRouter.message(
    MemberReportAddingStates.Confirmation,
    F.text == ReportConfirmKeyboard.ConfirmButtonText
)
async def MemberConfirm(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    # черновик
    await message.answer("Отчёт сохранён.", reply_markup=ReplyKeyboardRemove())

    activist = await getActivist(message, storage)

    await TransitToMemberDefault(message=message, state=state, activist=activist)

    return

# Подтверждение отчёта
@MemberReportAddingRouter.message(
    MemberReportAddingStates.Confirmation,
    F.text == ReportConfirmKeyboard.RetryButtonText
)
async def MemberRetry(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    # черновик
    await message.answer("Начинаю с начала.", reply_markup=ReplyKeyboardRemove())

    activist = await getActivist(message, storage)

    await TransitToMemberReportAdding(message=message, storage=storage, state=state)

    return


# Не сработало ни одной ручки составления отчёта
@MemberReportAddingRouter.message(MemberReportAddingStates())
async def UnknownReportAdding(message: Message, storage: BaseStorage, state: FSMContext) -> None:
    await message.answer("Неизвестный вариант ответа. Попробуйте ещё раз.")

    return

# Добавить попытки ошибок, и авто перекидывание на Default.

# Дописать новые модели и storage.

# Исправить работу с базой. (Нет поля Photo/Video у Report)