import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from common.text_for_db import categories, description_for_info_pages
from database.orm_qerry import  orm_create_categories, orm_add_banner_description


from database.models import Base, Product

engine = create_async_engine(os.getenv("DB_LITE"), echo=True)
# engine = create_async_engine(os.getenv("DB_URL"), echo=True)
session_marker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_marker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, description_for_info_pages)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
