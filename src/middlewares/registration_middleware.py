from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject
from db import get_user_by_tg_id, create_user
from cachetools import TTLCache
from services import ThreeXUIClient, get_server, get_server_by_id
from constants import MAX_LOADING_SCORE

stats_cache = TTLCache(maxsize=1000, ttl=300)

async def check_server(telegram_id: int, bot: Bot, server: ThreeXUIClient | None):
    if server and server.loading_score < MAX_LOADING_SCORE:
        return True
    
    await bot.send_message(
        chat_id=telegram_id, 
        text=(
            "⚠️ <b>Внимание! Не удаётся продолжить так как Ваш сервер перегружен или не отвечает.</b>\n\n"
            "<b>Попробуйте повторить попытку позже.</b>"
        ),
        parse_mode="HTML"
    )
    return False

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_tg = data.get("event_from_user")

        if not user_tg:
            return await handler(event, data)
        session = data["session"]
        user_id = user_tg.id
        is_reg = False

        user = await get_user_by_tg_id(session, user_id)
        
        if not user:
            server = get_server()
            server_id = None
            uuid = None

            success = await check_server(user_id, data['bot'], server)
            if not success:
                return

            if server:
                server_id = server.data["server_id"]
                uuid = await server.add_client(user_id, 0, 1)

            user = await create_user(
                session,
                telegram_id=user_id,
                uuid=uuid,
                server_id=server_id
            )
            user.server = None if not server.model else server.model
            is_reg = True

        server = get_server_by_id(user.server_id)
        success = await check_server(user_id, data['bot'], server)
        if not success:
            return

        if user_id in stats_cache:
            sub_info = stats_cache[user_id]
        else:
            sub_info = await server.get_client_stats(user.telegram_id)
            stats_cache[user_id] = sub_info

        data['user'] = user
        data['is_reg'] = is_reg
        data['sub_info'] = sub_info
        data['server_data'] = server.data

        return await handler(event, data)
