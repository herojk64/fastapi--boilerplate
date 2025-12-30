import os
from dotenv import load_dotenv

load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "postgres").lower()
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME", "fastapi_db")

def get_database_url(async_: bool = True) -> str:
    """
    Builds a dynamic DB URL for Postgres or MySQL.
    Use async_=False for Alembic migrations.
    """
    if DB_TYPE == "postgres":
        port = DB_PORT or "5432"
        driver = "asyncpg" if async_ else ""
        return f"postgresql+{driver}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/{DB_NAME}" if driver else f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/{DB_NAME}"
    elif DB_TYPE == "mysql":
        port = DB_PORT or "3306"
        driver = "aiomysql" if async_ else "pymysql"
        return f"mysql+{driver}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{port}/{DB_NAME}"
    else:
        raise ValueError("DB_TYPE must be 'postgres' or 'mysql'")
