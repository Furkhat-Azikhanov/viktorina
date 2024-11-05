import os

class Config:  # Конфигурационный класс
    SECRET_KEY = 'your_secret_key'  # Ключ для защиты сессий
    SQLALCHEMY_DATABASE_URI = 'sqlite:///quiz.db'  # Путь к базе данных SQLite
    WEATHER_API_KEY = 'af8b81ead662430e89a181234240511'  # Ваш API-ключ для погоды
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Отключаем предупреждения о модификациях
