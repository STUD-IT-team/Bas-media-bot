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

from pydantic import BaseModel
from uuid import UUID, uuid4
from models.event import EventChief, EventActivist
from models.activist import Activist
from datetime import timedelta

class Event(BaseModel):
    ID: UUID
    Name: str
    Date: datetime
    Place: str
    PhotoCount: int
    VideoCount: int
    Chief: EventChief
    Activists: List[EventActivist]
    IsCancelled: bool = False
    IsCompleted: bool = False
    CreatedBy: UUID
    CreatedAt: datetime

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

    # ID события
    event_id = uuid4()
    
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
        # TODO заполнить  self.notifScheduler данными из БД
        print(NotifRegistryBase.GetClassByName('InfoNotif').__name__)
        dataDB = [{
            'type': 'InfoNotif',
            'data': [uuid.uuid4(), "Пора пить кофе!", datetime.now().replace(second=datetime.now().second + 5), 937944297]
            # 'ID': uuid.uuid4(), 
            # 'Text': "Пора пить кофе!", 
            # 'NotifyTime': datetime.now().replace(second=datetime.now().second + 5),
            # 'ChatID': 937944297
        }, {
            'type': 'EventReminderNotif',
            'data': [uuid.uuid4(), 
                    "Проверить почту", 
                    datetime.now().replace(second=datetime.now().second + 7), 
                    937944297,
                    create_test_event()]
        }]
        for data in dataDB:
            notifClass = NotifRegistryBase.GetClassByName(data['type'])
            await self.AddNotification(notifClass(*data['data']))
    
    async def AddNotification(self, notif: BaseNotification):
        if not self.storage is None:
            #TODO на каждое добавление уведо можно дополнительно повесить удаление старых уведо при необходимости
            pass # TODO add note

        await self.notifScheduler.AddNotification(notif)

    async def StartScheduler(self):
        await self.notifScheduler.Start()

    