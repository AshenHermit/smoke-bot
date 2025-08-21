# Smoke Bot - Telegram бот для отказа от курения

собрано при помощи cursor

Бот, который помогает постепенно снижать дозировку курения, анализируя ваши привычки и рассчитывая оптимальные интервалы между сигаретами.

## Возможности

- 🚬 Запись выкуренных сигарет
- 📊 Анализ последних 3 записей для расчета интервалов
- ⚙️ Настройка коэффициента снижения (90%, 92%, 95%, 98%)
- 🎯 Прогноз даты полного отказа от курения
- 👥 Многопользовательский режим
- 🗄️ PostgreSQL для хранения данных
- 🕐 Все времена отображаются в московском часовом поясе

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <your-repo-url>
cd smoke-bot
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
# Bot configuration
BOT_TOKEN=your_bot_token_here

# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=smoke_bot

# Docker compose ports
DB_EXTERNAL_PORT=5432
PGADMIN_EXTERNAL_PORT=8080
PGADMIN_PASSWORD=admin123
```

### 4. Запуск базы данных
```bash
docker-compose up -d
```

### 5. Запуск бота
```bash
python main.py
```

## Контейнеризация и деплой

### Docker

Собрать локально и запустить:
```bash
docker compose up -d --build
```

Сервисы:
- `db` — PostgreSQL
- `bot` — Telegram бот

Переменные окружения читаются из `.env` (на сервере задайте `BOT_TOKEN`, `DB_*`).

### GitHub Actions: деплой на сервер

Workflow: `.github/workflows/deploy.yml` — триггер на push в ветку `main`.

Требуемые GitHub Secrets:
- `SSH_HOST` — адрес сервера
- `SSH_PORT` — порт SSH (например, 22)
- `SSH_USER` — пользователь SSH
- `SSH_PRIVATE_KEY` — приватный ключ (PEM) для подключения
- `DEPLOY_PATH` — путь на сервере (например, `/opt/smoke-bot`)
- `BOT_TOKEN` — токен Telegram бота (как секрет репозитория, для compose — задайте на сервере в `.env` или в системе)
- `DB_USER`, `DB_PASSWORD`, `DB_NAME` — при необходимости

Что делает pipeline:
1. Клонирует репозиторий
2. Устанавливает SSH-агент
3. Передает файлы на сервер через `rsync`
4. На сервере выполняет `docker compose build` и `docker compose up -d`

### Подготовка сервера

1. Установите Docker и Docker Compose v2
2. Создайте каталог деплоя, например `/opt/smoke-bot`
3. Настройте переменные окружения (в `.env` рядом с `docker-compose.yml`):
```env
BOT_TOKEN=... 
DB_USER=postgres
DB_PASSWORD=...
DB_NAME=smoke_bot
DB_PORT=5432
DB_EXTERNAL_PORT=5432
PGADMIN_EXTERNAL_PORT=8080
PGADMIN_PASSWORD=admin123
```
4. Первый запуск можно выполнить руками: `docker compose up -d --build`


## Команды бота

- `/start` - Начало работы с ботом
- `/smoke` - Записать выкуренную сигарету
- `/progress` - Показать текущий прогресс
- `/settings` - Настройки коэффициента снижения
- `/help` - Справка по командам

## Как это работает

1. **Анализ привычек**: Бот анализирует последние 3 записи о курении
2. **Расчет интервалов**: Вычисляет средний интервал между сигаретами
3. **Применение коэффициента**: Уменьшает интервал на заданный процент
4. **Прогресс**: Постепенно увеличивает время между сигаретами
5. **Цель**: Достижение минимального интервала (30 минут)

## Структура проекта

```
smoke-bot/
├── main.py              # Основной файл бота
├── models.py            # Модели базы данных
├── database.py          # Подключение к БД
├── services.py          # Бизнес-логика
├── handlers.py          # Обработчики команд
├── config.py            # Конфигурация
├── requirements.txt     # Зависимости Python
├── docker-compose.yml   # Конфигурация Docker
└── README.md           # Документация
```

## Технологии

- **Python 3.8+**
- **aiogram** - Telegram Bot API
- **Tortoise ORM** - Асинхронная ORM для PostgreSQL
- **PostgreSQL** - База данных
- **Docker** - Контейнеризация

## Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

## Устранение неполадок

### Ошибка подключения к БД
- Убедитесь, что Docker контейнер запущен: `docker-compose ps`
- Проверьте настройки в файле `.env`
- Проверьте логи: `docker-compose logs db`

### Бот не отвечает
- Проверьте токен бота в файле `.env`
- Убедитесь, что бот запущен: `python main.py`
- Проверьте логи на наличие ошибок

## Лицензия

MIT License
