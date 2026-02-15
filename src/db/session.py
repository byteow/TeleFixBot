from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import PG_URI

engine = create_async_engine(PG_URI, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)