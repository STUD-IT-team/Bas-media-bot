from aiogram import BaseMiddleware
from storage.storage import BaseStorage
from collections.abc import Callable, Awaitable
from aiogram.types import Update, Message
from typing import Dict, Any
from logging import Logger

from handlers.state import MemberStates, AdminStates
from handlers.usertransition import TransitToMemberDefault, TransitToAdminDefault, TransitToUnauthorized

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
            await TransitToUnauthorized(message=message, state=state)
            raise UnauthorizedError()

        elif admin is None and (userType is None or userType != "activist"):
            await message.answer("Ваш статус поменялся")
            await TransitToMemberDefault(message=message, state=state, activist=activist)
            logger.info(f"{message.chat.id}:{message.chat.username} changed status to activist")
            return

        elif admin is not None and (userType is None or userType != "admin"):
            await message.answer("Ваш статус поменялся")
            await TransitToAdminDefault(message=message, state=state, activist=activist)
            logger.info(f"{message.chat.id}:{message.chat.username} changed status to admin")
            return

        return await handler(event, data)
