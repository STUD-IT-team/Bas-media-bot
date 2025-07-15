from models.event import Event
from storage.storage import BaseStorage

from aiogram import F
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from storage.storage import BaseStorage
from logging import Logger

from handlers.state import AdminEventExportStates
from handlers.usertransition import TransitToAdminDefault

from keyboards.events.events import ChooseEventKeyboard

from googlexport.report.singleton import AddExportEventRequest
from googlexport.report.service import ExportService
from googlexport.report.requests import ExportEventReportsRequest
import googlexport.report.singleton as singleton

from utils.passbot import PassBot

async def TransitToAdminExportEvent(message: Message, storage : BaseStorage, state: FSMContext):
    events = storage.GetEvents()
    await state.set_state(AdminEventExportStates.ChoosingEvent)
    await message.answer("Выберите мероприятие для экспорта", reply_markup=ChooseEventKeyboard(events).Create())


AdminExportEventRouter = Router()

@AdminExportEventRouter.message(
    AdminEventExportStates.ChoosingEvent,
    F.text == ChooseEventKeyboard.CancelOperationButtonText
)
async def AdminCancelExportEvent(message: Message, storage : BaseStorage, state: FSMContext, logger: Logger):
    await message.answer("Отмена экспорта мероприятия")
    await TransitToAdminDefault(message=message, state=state, admin=storage.GetAdminByChatID(message.chat.id))


@AdminExportEventRouter.message(AdminEventExportStates.ChoosingEvent)
async def AdminExportEvent(message: Message, storage : BaseStorage, state: FSMContext, logger: Logger):
    data = await state.get_data()
    eventName = message.text
    event = storage.GetEventByName(eventName)
    if event is None:
        await message.answer(f"Мероприятие с именем {eventName} не найдено")
        await TransitToAdminDefault(message=message, state=state, admin=storage.GetAdminByChatID(message.chat.id))
        return
    
    args = [message.chat.id, logger, event]
    kwargs = {}
    req = ExportEventReportsRequest(event.ID, EventExportCallback, args, kwargs)
    await singleton.AddExportEventRequest(req)
    await message.answer(f"Запрос на экспорт мероприятия {event.Name} создан, ожидайте ответа")
    await TransitToAdminDefault(message=message, state=state, admin=storage.GetAdminByChatID(message.chat.id))

@PassBot
async def EventExportCallback(chatID: int, logger: Logger, event: Event, **kwargs):
    if ExportService.KwargsExceptionName in kwargs and kwargs[ExportService.KwargsExceptionName] is not None:
        exc = kwargs[ExportService.KwargsExceptionName]
        logger.error(f"Error occurred while exporting event: {exc}")
        await message.answer(f"Произошла ошибка при экспорте мероприятия.")
        return

    # На подумать
    b = kwargs["_bot"]
    await b.send_message(chat_id=chatID, text=f"Мероприятие {event.Name} успешно экспортировано!")
    if ExportService.KwargsSpreadsheetUrl in kwargs:
        spreadsheetUrl = kwargs[ExportService.KwargsSpreadsheetUrl]
        await b.send_message(chat_id=chatID, text=f"Ссылка на экспортированный документ: {spreadsheetUrl}")

