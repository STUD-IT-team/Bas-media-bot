import uuid
from aiogram import Bot
from typing import List, Dict, Optional
from collections.abc import Callable
from datetime import datetime

from storage.storage import BaseStorage
from notifications.NotificationScheduler import NotificationScheduler
from models.notification import BaseNotification
from notifications.NotifRegistry import NotifRegistryBase
from models.event import Event

from uuid import UUID, uuid4
from models.event import EventChief, EventActivist
from models.activist import Activist
from datetime import timedelta
from models.notification import MapperNotification
from notifications.NotifFilter import FilterNotif

# ID события
event_id = uuid4()

# Функция для создания тестового события
def create_test_event():
    # Создаем активистов
    chief_activist = Activist(
        ID=uuid4(),
        ChatID=123456789,
        Name="Иванов Иван Иванович",
        Valid=True
    )
    
    activist1 = Activist(
        ID=uuid4(),
        ChatID=987654321,
        Name="Петров Петр Петрович",
        Valid=True
    )
    
    activist2 = Activist(
        ID=uuid4(),
        ChatID=555666777,
        Name="Сидорова Мария Васильевна",
        Valid=True
    )
    # Создаем событие
    event = Event(
        ID=event_id,
        Name="Митинг за экологию",
        Date=datetime.now() + timedelta(days=7),
        Place="Парк Горького, главный вход",
        PhotoCount=3,
        VideoCount=1,
        Chief=EventChief(
            ID=uuid4(),
            EventID=event_id,
            Activist=chief_activist
        ),
        Activists=[
            EventActivist(
                ID=uuid4(),
                EventID=event_id,
                Activist=activist1
            ),
            EventActivist(
                ID=uuid4(),
                EventID=event_id,
                Activist=activist2
            )
        ],
        CreatedBy=chief_activist.ID,
        CreatedAt=datetime.now()
    )
    
    return event


class NotificationService:
    def __init__(self, bot: Optional[Bot]):
        self.notifScheduler = NotificationScheduler(bot)
        self.storage = None

    async def AddStorage(self, storage: Optional[BaseStorage]):
        self.storage = storage
        notifications = storage.GetAllNotDoneNotifs()
        for n in notifications:
            n.ChatIDs = [937944297]
            n.NotifyTime = datetime.now().replace(second=datetime.now().second)
            await self.notifScheduler.AddNotification(n)


        # TODO удалить тестовые события
        dataDB = [{
            'type': 'Info',
            'data': [
                uuid.uuid4(), 
                "Пора пить кофе!", 
                datetime.now().replace(second=datetime.now().second + 5), 
                [937944297]]
        }, {
            'type': 'EventReminder',
            'data': [uuid.uuid4(), 
                    "Проверить почту", 
                    datetime.now().replace(second=datetime.now().second + 7), 
                    [937944297],
                    create_test_event()]
        }]
        for data in dataDB:
            notifClass = NotifRegistryBase.GetClassByName(MapperNotification.GetClassNameByType(data['type']))
            n = notifClass(*data['data'])
            await self.notifScheduler.AddNotification(n)
            # n = notifClass(*data['data'])
            # print(n.Text, FilterNotif.TypeFilter(n, 'Info'))
            # print(n.Text, FilterNotif.TypeFilter(n, 'EventReminder'))
            # print(n.Text, FilterNotif.EventFilter(n, event_id))
    
    async def AddNotification(self, notif: BaseNotification):
        if not self.storage is None:
            #TODO на каждое добавление уведо можно дополнительно повесить удаление старых уведо при необходимости
            pass # TODO add note

        await self.notifScheduler.AddNotification(notif)

    async def StartScheduler(self):
        await self.notifScheduler.Start()

    