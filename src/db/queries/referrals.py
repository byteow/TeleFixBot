from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from db import Referral

async def create_referral(
    session: AsyncSession, 
    referrer_id: int,
    invited_id: int
):
    referral = Referral(
        referrer_id=referrer_id,
        invited_id=invited_id
    )
    session.add(referral)
    await session.commit()
    await session.refresh(referral)
    return referral

async def get_referrals_count(
    session: AsyncSession,
    referrer_id: int
):
    query = select(func.count())\
        .select_from(Referral)\
        .where(Referral.referrer_id == referrer_id)
    
    result = await session.execute(query)
    return result.scalar() or 0

async def get_referral(
    session: AsyncSession,
    refferer_id: int,
    invited_id: int
):
    query = select(Referral)\
        .where(and_(Referral.referrer_id == refferer_id, Referral.invited_id == invited_id))
    result = await session.execute(query)
    return result.scalar_one_or_none()