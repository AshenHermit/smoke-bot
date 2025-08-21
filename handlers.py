from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services import SmokingService
from datetime import datetime

def register_handlers(dp: Dispatcher):
    """Регистрирует все хендлеры"""
    
    @dp.message(CommandStart())
    async def start_command(message: Message):
        """Обработчик команды /start"""
        user = await SmokingService.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name
        )
        
        welcome_text = f"""
Привет, <b>{message.from_user.full_name}</b>! 

Я бот, который поможет тебе бросить курить. Вот что я умею:

🚬 /smoke - Записать выкуренную сигарету
⚙️ /settings - Настройки коэффициента снижения
📊 /progress - Показать прогресс
❓ /help - Помощь

Твой текущий коэффициент снижения: <b>{float(user.reduction_coefficient):.0%}</b>
Начальный интервал: <b>{user.initial_interval_hours} часов</b>

Давай начнем! Нажми /smoke когда выкуришь сигарету.
        """
        
        await message.answer(welcome_text, parse_mode="HTML")
    
    @dp.message(Command("smoke"))
    async def smoke_command(message: Message):
        """Обработчик команды /smoke"""
        try:
            # Получаем пользователя
            user = await SmokingService.get_or_create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )
            
            # Записываем выкуренную сигарету
            result = await SmokingService.record_smoking(user.id)
            
            # Форматируем время (уже в московском времени)
            next_time = result['next_smoking_time']
            next_time_str = next_time.strftime("%d.%m.%Y в %H:%M (МСК)")

            can_predict = result['can_predict']
            
            # Форматируем дату отказа
            quit_date = result['quit_date']
            quit_date_str = quit_date.strftime("%d.%m.%Y")
            
            response_text = f"""
🚬 Сигарета записана!

⏰ Следующую можно выкурить: <b>{next_time_str if can_predict else 'Неизвестно, пока нет данных'}</b>
📊 Текущий интервал: <b>{result["current_interval"]:.1f} часов</b>
🎯 Примерная дата отказа: <b>{quit_date_str}</b>

Продолжай в том же духе! 💪
            """
            
            await message.answer(response_text, parse_mode="HTML")
            
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")
    
    @dp.message(Command("progress"))
    async def progress_command(message: Message):
        """Обработчик команды /progress"""
        try:
            user = await SmokingService.get_or_create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )
            
            progress = await SmokingService.get_user_progress(user.id)
            
            progress_text = f"""
📊 Твой прогресс:

⏰ Текущий интервал: <b>{progress["current_interval_hours"]:.1f} часов</b>
📉 Коэффициент снижения: <b>{progress["reduction_coefficient"]:.0%}</b>
🚬 Всего записей: <b>{progress["total_records"]}</b>
🎯 Целевая дата отказа: <b>{progress["target_quit_date"].strftime("%d.%m.%Y") if progress["target_quit_date"] else "Не рассчитана"}</b>

Продолжай работать над собой! 💪
            """
            
            await message.answer(progress_text, parse_mode="HTML")
            
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")
    
    @dp.message(Command("settings"))
    async def settings_command(message: Message):
        """Обработчик команды /settings"""
        try:
            user = await SmokingService.get_or_create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name
            )
            
            # Создаем клавиатуру с настройками
            builder = InlineKeyboardBuilder()
            
            # Коэффициенты снижения
            coefficients = [0.90, 0.92, 0.95, 0.98]
            for coef in coefficients:
                is_current = abs(float(user.reduction_coefficient) - coef) < 0.01
                text = f"{coef:.0%} {'✅' if is_current else ''}"
                builder.add(InlineKeyboardButton(
                    text=text,
                    callback_data=f"set_coef_{coef}"
                ))
            
            builder.adjust(2)  # 2 кнопки в ряду
            
            settings_text = f"""
⚙️ Настройки

Текущий коэффициент снижения: <b>{float(user.reduction_coefficient):.0%}</b>

Выбери новый коэффициент:
• 90% - быстрое снижение (агрессивный режим)
• 92% - умеренное снижение
• 95% - медленное снижение (рекомендуется)
• 98% - очень медленное снижение (щадящий режим)
            """
            
            await message.answer(settings_text, parse_mode="HTML", reply_markup=builder.as_markup())
            
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")
    
    @dp.message(Command("help"))
    async def help_command(message: Message):
        """Обработчик команды /help"""
        help_text = """
❓ Помощь по командам:

🚬 /smoke - Записать выкуренную сигарету
   Бот рассчитает, когда можно выкурить следующую

⚙️ /settings - Настройки
   Изменить коэффициент снижения дозировки

📊 /progress - Прогресс
   Показать текущую статистику

❓ /help - Эта справка

Как это работает:
1. Нажми /smoke когда выкуришь сигарету
2. Бот проанализирует твои последние 3 записи
3. Рассчитает новый интервал с учетом коэффициента снижения
4. Покажет, когда можно выкурить следующую
5. Постепенно интервал будет увеличиваться
        """
        
        await message.answer(help_text)
    
    # Обработчик callback'ов для настроек
    @dp.callback_query(lambda c: c.data.startswith('set_coef_'))
    async def process_coefficient_setting(callback: CallbackQuery):
        """Обработчик изменения коэффициента снижения"""
        try:
            coefficient = float(callback.data.split('_')[2])
            
            user = await SmokingService.get_or_create_user(
                telegram_id=callback.from_user.id,
                username=callback.from_user.username,
                full_name=callback.from_user.full_name
            )
            
            # Обновляем коэффициент
            await SmokingService.update_user_settings(user.id, reduction_coefficient=coefficient)
            
            await callback.message.edit_text(
                f"✅ Коэффициент снижения изменен на {coefficient:.0%}!\n\n"
                f"Теперь твоя дозировка будет снижаться быстрее.",
                reply_markup=None
            )
            
        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}")
        
        await callback.answer()
