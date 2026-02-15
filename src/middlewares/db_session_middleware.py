from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from db import AsyncSessionLocal

class DatabaseSessionMiddleware(BaseMiddleware):
    def __init__(self):
        ...

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            data['session'] = session
            result = await handler(event, data)
            return result