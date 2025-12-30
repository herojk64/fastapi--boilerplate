from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.configs.db import get_database_url

DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session

async def close_db():
    await engine.dispose()


# Import models to ensure mappers are configured and relationship string
# lookups like "Roles" are resolvable at import time.
try:
    import src.models  # noqa: F401
except Exception:
    # Avoid failing imports in contexts that don't need models
    pass
