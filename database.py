from tortoise import Tortoise
from config import DATABASE_URL

async def init_db():
    """Инициализация подключения к базе данных"""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

async def close_db():
    """Закрытие подключения к базе данных"""
    await Tortoise.close_connections()
