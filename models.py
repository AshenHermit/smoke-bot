from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime

class User(models.Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    reduction_coefficient = fields.DecimalField(max_digits=3, decimal_places=2, default=0.95)
    target_quit_date = fields.DateField(null=True)
    
    # Настройки интервалов
    initial_interval_hours = fields.FloatField(default=2.0)
    min_interval_hours = fields.FloatField(default=0.5)
    max_interval_hours = fields.FloatField(default=24.0)
    
    class Meta:
        table = "users"

class SmokingRecord(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='smoking_records')
    smoked_at = fields.DatetimeField(auto_now_add=True)
    interval_minutes = fields.FloatField(null=True)  # интервал до следующей сигареты
    
    class Meta:
        table = "smoking_records"

# Pydantic модели для валидации данных
User_Pydantic = pydantic_model_creator(User, name="User")
SmokingRecord_Pydantic = pydantic_model_creator(SmokingRecord, name="SmokingRecord")
