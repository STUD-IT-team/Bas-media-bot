from aiogram.types import Message

async def get_list_of_events(message: Message):
    Activist = storage.GetActivistByChatID(message.chat.id)
    try:
        events = GetEventsByActivist(Activist.ID)
    except:
        await message.answer("Ошибка при получении списка ваших активных мероприятий")
        raise
    
    message.answer(f"Всего мероприятий: {len(events)}")
    await message.answer("<b>Список ваших активных мероприятий</b>")
    for event in events: 
        await message.answer(f"""
            {event.Name} - {event.Date}
            Количество фото: {event.Photocount}
            Количество видео: {event.Videocount}
        """)

