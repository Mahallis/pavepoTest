from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.general import settings as conf

Base = declarative_base()

DATABASE_URL = (
    f"postgresql+asyncpg://{conf.POSTGRES_USER}:{conf.POSTGRES_PASSWORD}"
    f"@{conf.DB_HOST}:{conf.DB_PORT}/{conf.POSTGRES_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
