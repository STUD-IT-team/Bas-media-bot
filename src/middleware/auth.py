from aiogram import BaseMiddleware
from storage.storage import BaseStorage
from collections.abc import Callable, Awaitable
from aiogram.types import Update, Message
from typing import Dict, Any
from logging import Logger

from handlers.state import MemberStates, AdminStates

class UnauthorizedError(Exception):
    def __str__(self):
        return "Unauthorized User"


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if not 'storage' in data:
            raise ValueError("AuthMiddleware: Storage middleware used in auth middleware")
        storage = data['storage']
        if not isinstance(storage, BaseStorage):
            raise ValueError("AuthMiddleware: Storage middleware used with non-storage object")
        logger = data['logger']
        if not isinstance(logger, Logger):
            raise ValueError("AuthMiddleware: Logger must be instance of Logger")
        
        state = data['state']
        # Для проверки на изменение статуса активиста
        userType = (await state.get_data()).get('user-type', None) 

        
        message = event.message
        try:
            storage.PutTgUser(message.chat.id, message.chat.username)
            activist = storage.GetActivistByChatID(message.chat.id)
            admin = storage.GetAdminByChatID(message.chat.id)
        except Exception:
            await message.answer(f"Не удалось проверить вашу авторизацию, повторите позднее")
            raise

        if activist is None or not activist.Valid:
            await message.answer("Не могу найти вас в своих базах, если это ошибка - напишите администратору")
            await state.clear()
            raise UnauthorizedError()

        elif admin is None and (userType is None or userType != "activist"):
            await state.clear()
            await state.set_data({"user-type": "activist"})
            # TODO: Заменить на вызов функции по смену статуса в дефолтные ручки
            await message.answer("Ваш статус поменялся")
            await message.answer(f"Активист, {activist.Name}! Что хотите сделать?")
            await state.set_state(MemberStates.Default)
            logger.info(f"{message.chat.id}:{message.chat.username} changed status to activist")
            return

        elif admin is not None and (userType is None or userType != "admin"):
            await state.clear()
            await state.set_data({"user-type": "admin"})
            # TODO: Заменить на вызов функции по смену статуса в дефолтные ручки
            await message.answer("Ваш статус поменялся")
            await message.answer(f"Администратор, {activist.Name}! Что хотите сделать?")
            await state.set_state(AdminStates.Default)
            logger.info(f"{message.chat.id}:{message.chat.username} changed status to admin")
            return

        return await handler(event, data)
