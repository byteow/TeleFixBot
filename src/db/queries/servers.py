from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db import Server

async def get_random_server(session: AsyncSession):
    result = await session.execute(
        select(Server).order_by(func.random()).limit(1)
    )
    server = result.scalar_one_or_none()
    return server

async def get_servers(session: AsyncSession):
    result = await session.execute(
        select(Server)
    )
    servers = result.scalars().all()
    return servers