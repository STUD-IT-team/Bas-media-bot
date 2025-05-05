from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
from typing import List, Dict, Optional, Callable
import uuid
from aiogram import Bot
from uuid import UUID
from aiolimiter import AsyncLimiter
from weakref import WeakMethod

from models.notification import BaseNotification
from notifications.NotifFilter import BaseFilterNotif
# from models.notification import Notification


class NotificationScheduler:
    def __init__(self, bot: Optional[Bot], setDoneNotifFunc: Callable[[UUID], None]):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        self.setDoneNotifFunc = WeakMethod(setDoneNotifFunc) # if hasattr(setDoneNotifFunc, '__self__') else setDoneNotifFunc
        self.notifications: Dict[UUID, BaseNotification] = {}
        self.limiter = AsyncLimiter(30, 60)  # 30 уведомлений в 60 секунд
        
    async def AddNotification(self, notif: BaseNotification):
        """Добавляет уведомление и планирует его вывод"""
        print(f"{notif}")

        self.notifications[notif.ID] = notif

        # Если время уведомления уже прошло, отправляем сразу
        if notif.NotifyTime <= datetime.now():
            # print('-----here------')
            await self._sendNotification(notif.ID)
            return

        # Планируем задачу
        self.scheduler.add_job(
            self._sendNotification,
            'date',
            run_date=notif.NotifyTime,
            args=(notif.ID,),
            id=notif.ID.hex
        )
        
        # return notification_id
    
    async def _sendNotification(self, notification_id: UUID):
        """Внутренний метод для отправки уведомления"""
        async with self.limiter:
            if self.bot and notification_id in self.notifications:
                notification = self.notifications.pop(notification_id)
                print("------------------------1\n")
                for charID in notification.ChatIDs:
                    await self.bot.send_message(
                        chat_id=charID,
                        text=notification.GetMessageText()
                    )
                print("------------------------2\n")
                callback = self.setDoneNotifFunc() # if isinstance(self.setDoneNotifFunc, WeakMethod) else self.setDoneNotifFunc
                if callback is not None:
                    await callback(notification.ID)
    
    async def RemoveNotifications(self, filter: BaseFilterNotif) -> list[BaseNotification]:
        # remaining = []
        removed = []
        for key in list(self.notifications.keys()):
            if filter.filter(self.notifications[key]):
                # remaining.append(n)
            # else:
                removed.append(self.notifications.pop(key))
        # self.notifications = remaining[:]
        return removed  

    async def Start(self):
        """Запускает планировщик"""
        self.scheduler.start()
        print("Сервис уведомлений запущен. Ожидание запланированных сообщений...")
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            print("Сервис уведомлений остановлен.")
    
