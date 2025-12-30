from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.db import close_db,Base,engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # The code here will run before the server is stopped
    await close_db()
    print("🚪 Database connections closed.")
