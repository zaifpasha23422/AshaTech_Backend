from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession 
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from core.Config import settings

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession, autoflush=False, expire_on_commit =False )

Base = declarative_base()

async def get_db()-> AsyncGenerator[AsyncSession,None]:
    async with AsyncSessionLocal() as session:
        yield session
        
