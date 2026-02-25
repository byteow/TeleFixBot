from services import ThreeXUIClient
from db import AsyncSessionLocal, get_servers

three_xui_clients: dict[int, ThreeXUIClient] = {}

async def set_servers():
    async with AsyncSessionLocal() as session:
        servers = await get_servers(session)
        for server in servers:
            client = ThreeXUIClient(server)
            result = await client.login()
            if not result: continue
            client.start_check_thread()
            three_xui_clients[server.id] = client

def get_server() -> ThreeXUIClient | None:
    servers = list(three_xui_clients.values())
    if not servers:
        return None
    return min(servers, key=lambda s: s.loading_score)

def get_server_by_id(id: int) -> ThreeXUIClient | None:
    try:
        return three_xui_clients.get(id)
    except KeyError:
        return None