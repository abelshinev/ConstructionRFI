import os

from dotenv import load_dotenv

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool,  # Disable connection pooling for simplicity
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()