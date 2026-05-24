from storage.database.connect import AsyncSessionLocal

async def get_db():
    """Dependency to get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
