import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv

from database import init_db, close_db
from handlers import register_handlers
from config import BOT_TOKEN

# Загружаем переменные окружения
load_dotenv()

# Инициализируем диспетчер
dp = Dispatcher()

async def main() -> None:
    """Основная функция"""
    # Инициализируем БД
    await init_db()
    logging.info("База данных инициализирована")
    
    # Регистрируем хендлеры
    register_handlers(dp)
    logging.info("Хендлеры зарегистрированы")
    
    # Инициализируем бота
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logging.info("Бот инициализирован")
    
    try:
        # Регистрируем команды в меню Telegram
        await bot.set_my_commands([
            BotCommand(command="start", description="Начало работы"),
            BotCommand(command="smoke", description="Записать выкуренную сигарету"),
            BotCommand(command="progress", description="Показать прогресс"),
            BotCommand(command="settings", description="Настройки коэффициента"),
            BotCommand(command="help", description="Справка по командам"),
        ])
        logging.info("Команды бота зарегистрированы")

        # Запускаем бота
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Ошибка в работе бота: {e}")
    finally:
        # Закрываем соединения с БД
        await close_db()
        logging.info("Соединения с БД закрыты")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    asyncio.run(main())
