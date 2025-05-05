import uuid
from aiogram import Bot
from typing import List, Dict, Optional
from datetime import datetime

from storage.storage import BaseStorage
from notifications.NotificationScheduler import NotificationScheduler
from models.notification import BaseNotification
from models.event import Event

from uuid import UUID, uuid4
from models.event import EventChief, EventActivist
from models.activist import Activist
from datetime import timedelta
from models.notification import MapperNotification
from notifications.NotifFilter import BaseFilterNotif

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
        self.notifScheduler = NotificationScheduler(bot, self.SetDoneNotifications)
        self.storage = None

    async def AddStorage(self, storage: Optional[BaseStorage]):
        self.storage = storage
        notifications = storage.GetAllNotDoneNotifs()
        i = 1
        # for _ in range(4):
        # n = notifications[0]
        # n.ChatIDs = [937944297]
        # n.NotifyTime = datetime.now().replace(day=datetime.now().day - 1)
        # await self.notifScheduler.AddNotification(n)
        for n in notifications:
            n.Text = n.Text + f'\n{i}'
            i += 1
            n.ChatIDs = [937944297]
            n.NotifyTime = datetime.now().replace(day=datetime.now().day + 1)
            n.Text = "--------------------------"
            await self.notifScheduler.AddNotification(n)


        # TODO удалить тестовые события
        # dataDB = [{
        #     'type': 'info',
        #     'data': [
        #         uuid.uuid4(), 
        #         "Пора пить кофе!", 
        #         datetime.now().replace(second=datetime.now().second), 
        #         [937944297]]
        # }, {
        #     'type': 'event_reminder',
        #     'data': [uuid.uuid4(), 
        #             "Проверить почту", 
        #             datetime.now().replace(second=datetime.now().second), 
        #             [937944297],
        #             create_test_event()]
        # }]
        # for data in dataDB:
        #     n = MapperNotification.CreateNotification(data['type'], *data['data'])
        #     await self.notifScheduler.AddNotification(n)
            # n = notifClass(*data['data'])
            # print(n.Text, FilterNotif.TypeFilter(n, 'Info'))
            # print(n.Text, FilterNotif.TypeFilter(n, 'EventReminder'))
            # print(n.Text, FilterNotif.EventFilter(n, event_id))
    
    async def AddNotification(self, notif: BaseNotification):
        await self.notifScheduler.AddNotification(notif)
        if self.storage is not None:
            self.storage.PutNotification(notif)

    async def RemoveNotifications(self, filter: BaseFilterNotif):
        if self.storage is not None:
            removed = await self.notifScheduler.RemoveNotifications(filter)
            for n in removed:
                self.storage.RemoveNotification(n.ID)

    async def SetDoneNotifications(self, notifID: UUID):
        print("SetDoneNotifications\n")
        if self.storage is not None:
            print(f"SET_DONE - {notifID}\n")
            self.storage.SetDoneNotification(notifID)

    async def StartScheduler(self):
        await self.notifScheduler.Start()

    