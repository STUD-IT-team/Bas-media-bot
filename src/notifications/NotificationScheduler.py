from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import asyncio
from typing import Dict, Optional, Callable
from aiogram import Bot
from uuid import UUID
from aiolimiter import AsyncLimiter
from weakref import WeakMethod

from models.notification import BaseNotification
from notifications.NotifFilter import BaseFilterNotif


class NotificationScheduler:
    def __init__(self, bot: Optional[Bot], setDoneNotifFunc: Callable[[UUID], None]):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        self.setDoneNotifFunc = WeakMethod(setDoneNotifFunc) # if hasattr(setDoneNotifFunc, '__self__') else setDoneNotifFunc
        self.notifications: Dict[UUID, BaseNotification] = {}
        self.limiter = AsyncLimiter(30, 60)  # 30 уведомлений в 60 секунд
        
    async def AddNotification(self, notif: BaseNotification):
        self.notifications[notif.ID] = notif

        if notif.NotifyTime <= datetime.now():
            await self._sendNotification(notif.ID)
            return

        self.scheduler.add_job(
            self._sendNotification,
            'date',
            run_date=notif.NotifyTime,
            args=(notif.ID,),
            id=notif.ID.hex
        )
    
    async def _sendNotification(self, notification_id: UUID):
        async with self.limiter:
            if self.bot and notification_id in self.notifications:
                notification = self.notifications.pop(notification_id)
                for charID in notification.ChatIDs:
                    await self.bot.send_message(
                        chat_id=charID,
                        text=notification.GetMessageText()
                    )
                callback = self.setDoneNotifFunc() # if isinstance(self.setDoneNotifFunc, WeakMethod) else self.setDoneNotifFunc
                if callback is not None:
                    await callback(notification.ID)
    
    async def RemoveNotifications(self, filter: BaseFilterNotif) -> list[BaseNotification]:
        removed = []
        for key in list(self.notifications.keys()):
            if filter.filter(self.notifications[key]):
                removed.append(self.notifications.pop(key))
        return removed  

    async def Start(self):
        self.scheduler.start()
        try:
            while True:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
    
