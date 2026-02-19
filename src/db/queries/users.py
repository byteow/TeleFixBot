from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from db import User
from sqlalchemy.orm import joinedload

async def create_user(
    session: AsyncSession, 
    telegram_id: int, 
    uuid: str, 
    server_id: int
):
    new_user = User(
        telegram_id=telegram_id,
        uuid=uuid,
        server_id=server_id
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def get_user_by_tg_id(
    session: AsyncSession, 
    telegram_id: int
):
    query = select(User).where(User.telegram_id == telegram_id).options(joinedload(User.server))
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_all_users_on_server(
    session: AsyncSession, 
    server_id: int
):
    query = select(User).where(User.server_id == server_id)
    result = await session.execute(query)
    return result.scalars().all()

async def update_user_server(
    session: AsyncSession, 
    telegram_id: int, 
    new_server_id: int
):
    query = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(server_id=new_server_id)
    )
    await session.execute(query)
    await session.commit()

async def update_user_uuid(
    session: AsyncSession, 
    telegram_id: int, 
    new_uuid: str
):
    query = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(uuid=new_uuid)
    )
    await session.execute(query)
    await session.commit()

async def delete_user(
    session: AsyncSession, 
    telegram_id: int
):
    query = delete(User).where(User.telegram_id == telegram_id)
    await session.execute(query)
    await session.commit()

async def get_users_telegram_ids(
    session: AsyncSession
):
    query = select(User.telegram_id)
    result = await session.execute(query)
    return result.scalars().all()