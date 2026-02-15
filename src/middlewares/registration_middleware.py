from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from db import get_user_by_tg_id, create_user
from services import ThreeXUIClient
from create_bot import get_random_server, three_xui_clients

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
            server: ThreeXUIClient | None = get_random_server()
            server_id = None
            uuid = None

            if server:
                server_id = server.data["server_id"]
                uuid = await server.add_client(0, 1)

            user = await create_user(
                session,
                telegram_id=user_id,
                uuid=uuid,
                server_id=server_id
            )
            user.server = None if not server.model else server.model
            is_reg = True

        server = three_xui_clients[user.server_id]
        sub_info = await server.get_client_stats(user.uuid)

        data['user'] = user
        data['is_reg'] = is_reg
        data['sub_info'] = sub_info
        data['server_data'] = server.data

        return await handler(event, data)
