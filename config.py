import os
from dotenv import load_dotenv
import pytz

load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "smoke_bot")

DATABASE_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Default smoking settings
DEFAULT_REDUCTION_COEFFICIENT = 0.95
DEFAULT_INITIAL_INTERVAL_HOURS = 2.0
DEFAULT_MIN_INTERVAL_HOURS = 0.5
DEFAULT_MAX_INTERVAL_HOURS = 24.0
RECORDS_COUNT = 5

# Timezone settings
MOSCOW_TZ = pytz.timezone('Europe/Moscow')
