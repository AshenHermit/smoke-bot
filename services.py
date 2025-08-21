from models import User, SmokingRecord
from datetime import datetime, timedelta
from typing import List, Optional
from config import DEFAULT_REDUCTION_COEFFICIENT, DEFAULT_INITIAL_INTERVAL_HOURS, MOSCOW_TZ, RECORDS_COUNT
import pytz

class SmokingService:
    @staticmethod
    def get_moscow_time() -> datetime:
        """Получает текущее московское время"""
        utc_now = datetime.now(pytz.UTC)
        return utc_now.astimezone(MOSCOW_TZ)
    
    @staticmethod
    async def get_or_create_user(telegram_id: int, username: str, full_name: str) -> User:
        """Получает существующего пользователя или создает нового"""
        user, created = await User.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username,
                'full_name': full_name,
                'reduction_coefficient': DEFAULT_REDUCTION_COEFFICIENT,
                'initial_interval_hours': DEFAULT_INITIAL_INTERVAL_HOURS,
                'min_interval_hours': 0.5,
                'max_interval_hours': 24.0
            }
        )
        return user
    
    @staticmethod
    async def record_smoking(user_id: int) -> dict:
        """Записывает выкуренную сигарету и возвращает время следующей"""
        user = await User.get(id=user_id)
        
        # Создаем запись
        await SmokingRecord.create(user_id=user_id)
        
        # Рассчитываем время следующей сигареты
        next_time = await SmokingService._calculate_next_smoking_time(user)
        
        # Обновляем target_quit_date
        quit_date = await SmokingService._calculate_quit_date(user)
        await User.filter(id=user_id).update(target_quit_date=quit_date)

        # Проверяем, есть ли хотя бы 2 записи
        recent_records = await SmokingService.get_recent_records(user_id)
        can_predict = len(recent_records) >= 2
        
        return {
            'can_predict': can_predict,
            'next_smoking_time': next_time,
            'quit_date': quit_date,
            'current_interval': await SmokingService._get_current_average_interval(user_id)
        }

    @staticmethod
    async def get_recent_records(user_id: int) -> List[SmokingRecord]:
        """Получает последние RECORDS_COUNT записей"""
        return await SmokingRecord.filter(
            user_id=user_id
        ).order_by('-smoked_at').limit(RECORDS_COUNT)
    
    @staticmethod
    async def _calculate_next_smoking_time(user: User) -> datetime:
        """Рассчитывает время следующей сигареты"""
        # Получаем последние RECORDS_COUNT записи
        recent_records = await SmokingService.get_recent_records(user.id)
        
        if len(recent_records) < 2:
            # Если записей мало, используем базовый интервал
            moscow_now = SmokingService.get_moscow_time()
            return moscow_now + timedelta(hours=user.initial_interval_hours)
        
        # Вычисляем средний интервал
        intervals = []
        for i in range(1, len(recent_records)):
            interval = abs((recent_records[i-1].smoked_at - recent_records[i].smoked_at)).total_seconds() / 3600
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals)
        
        # Применяем коэффициент снижения дозировки:
        # коэффициент < 1 означает, что частота курения снижается,
        # поэтому интервал ДОЛЖЕН расти. Увеличиваем интервал в 1/коэфф раз.
        reduction_coefficient = float(user.reduction_coefficient)
        growth_factor = 1.0 / reduction_coefficient if reduction_coefficient > 0 else 1.0
        new_interval = avg_interval * growth_factor
        
        # Ограничиваем минимальным и максимальным значениями
        new_interval = max(user.min_interval_hours, 
                          min(user.max_interval_hours, new_interval))
        
        moscow_now = SmokingService.get_moscow_time()
        return moscow_now + timedelta(hours=new_interval)
    
    @staticmethod
    async def _get_current_average_interval(user_id: int) -> float:
        """Получает текущий средний интервал"""
        recent_records = await SmokingService.get_recent_records(user_id)
        
        if len(recent_records) < 2:
            return DEFAULT_INITIAL_INTERVAL_HOURS  # базовый интервал
        
        intervals = []
        for i in range(1, len(recent_records)):
            interval = (recent_records[i-1].smoked_at - recent_records[i].smoked_at).total_seconds() / 3600
            intervals.append(interval)
        
        return sum(intervals) / len(intervals)
    
    @staticmethod
    async def _calculate_quit_date(user: User) -> datetime.date:
        """Рассчитывает дату полного отказа"""
        current_interval = await SmokingService._get_current_average_interval(user.id)
        max_interval = user.max_interval_hours
        
        days_to_max = 0
        temp_interval = current_interval
        reduction_coefficient = float(user.reduction_coefficient)
        growth_factor = 1.0 / reduction_coefficient if reduction_coefficient > 0 else 1.0
        
        # Двигаемся к максимальному интервалу, увеличивая интервал каждый день
        # Ограничим вычисление 365 днями на случай некорректных настроек
        while temp_interval < max_interval and days_to_max < 365:
            temp_interval *= growth_factor
            days_to_max += 1
        
        moscow_now = SmokingService.get_moscow_time()
        return (moscow_now + timedelta(days=days_to_max)).date()
    
    @staticmethod
    async def get_user_progress(user_id: int) -> dict:
        """Получает прогресс пользователя"""
        user = await User.get(id=user_id)
        current_interval = await SmokingService._get_current_average_interval(user_id)
        
        return {
            'current_interval_hours': current_interval,
            'reduction_coefficient': float(user.reduction_coefficient),
            'target_quit_date': user.target_quit_date,
            'total_records': await SmokingRecord.filter(user_id=user_id).count()
        }
    
    @staticmethod
    async def update_user_settings(user_id: int, **kwargs) -> User:
        """Обновляет настройки пользователя"""
        await User.filter(id=user_id).update(**kwargs)
        return await User.get(id=user_id)
