from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database.database import Database


class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        self.db = Database()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        if not isinstance(event, Message):
            return await handler(event, data)

        if (event.from_user is None) or (event.from_user.id is None):
            return

        user = await self.db.get_user(event.from_user.id)
        
        if (user is None) or (not user.is_admin):
            return

        return await handler(event, data)
