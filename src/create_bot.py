import logging
from config import API_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from db import AsyncSessionLocal, get_servers
from services import ThreeXUIClient
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

three_xui_clients: dict[int, ThreeXUIClient] = {}

async def set_servers():
    async with AsyncSessionLocal() as session:
        servers = await get_servers(session)
        for server in servers:
            client = ThreeXUIClient(
                server.inbound_id,
                server.id, 
                server.host, 
                server.port, 
                server.login, 
                server.password,
                server.sni,
                server.sid,
                server.pbk,
                server
            )
            result = await client.login()
            if not result: continue
            three_xui_clients[server.id] = client

def get_random_server():
    random_id = list(three_xui_clients.keys())[random.randint(0, len(three_xui_clients.items())-1)]
    return three_xui_clients.get(random_id)