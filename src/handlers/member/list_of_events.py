from aiogram.types import Message
from aiogram import Router, F
from storage.pgredis import GetEventsByActivist

getListOfEventsRouter = Router()

@getListOfEventsRouter.message(F.text == "Инфа о мероприятиях")
async def getListOfEvents(message: Message):
    Activist = storage.GetActivistByChatID(message.chat.id)
    try:
        events = GetEventsByActivist(Activist.ID)
    except:
        await message.answer("Ошибка при получении списка ваших мероприятий")
        raise
    
    message.answer(f"Всего мероприятий: {len(events)}")
    await message.answer("<b>Список ваших активных мероприятий</b>")
    for event in events: 
        await message.answer(f"""
            {event.Name} - {event.Date}
            Ответственный за мероприятие:{event.ChiefName} {event.ChiefTgNick}
            Количество фото: {event.Photocount}
            Количество видео: {event.Videocount}
        """)

