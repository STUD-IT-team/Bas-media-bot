from aiogram.types import Message
from aiogram import Router, F
from handlers.state import MemberStates
from storage.storage import BaseStorage
from utils.strings import NewlineJoin
from aiogram.fsm.context import FSMContext
from keyboards.default.member import MemberDefaultKeyboard

MemberGetListOfEventsRouter = Router()

@MemberGetListOfEventsRouter.message(F.text == MemberDefaultKeyboard.EventInfoButtonText)
async def getListOfEvents(message: Message, state: FSMContext, storage: BaseStorage):

    try:
        act = storage.GetActivistByChatID(message.chat.id)
        events = storage.GetEventsByActivistID(act.ID)

    except:
        await message.answer("Ошибка при получении списка ваших мероприятий")
        await state.set_state(MemberStates.Default)
        raise
    if len(events) == 0:
        await message.answer("У Вас нет активных мероприятий")
    else:
        await message.answer(f"Всего мероприятий: {len(events)}")
        await message.answer("<b>Список ваших активных мероприятий</b>")
        for event in events: 
            await message.answer(NewlineJoin(
            f"<b>{event.Name} -- {event.Date.strftime('%d-%m-%Y %H:%M')}</b>",
            f"<b>Количество фото:</b> {event.PhotoCount}",
            f"<b>Количество видео:</b> {event.VideoCount}",
            f"<b>Главорг:</b> {event.Chief.Name}  @{event.ChiefTgNick}"))

    await state.set_state(MemberStates.Default)