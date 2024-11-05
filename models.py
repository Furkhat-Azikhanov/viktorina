from flask_sqlalchemy import SQLAlchemy  # Импортируем SQLAlchemy для работы с базой данных

db = SQLAlchemy()  # Создаем объект SQLAlchemy

class User(db.Model):  # Определяем модель пользователя
    id = db.Column(db.Integer, primary_key=True)  # Первичный ключ
    username = db.Column(db.String(80), unique=True, nullable=False)  # Логин пользователя, должен быть уникальным
    display_name = db.Column(db.String(80), unique=True, nullable=False)  # Отображаемое имя, должно быть уникальным
    password = db.Column(db.String(120), nullable=False)  # Хэшированный пароль
    score = db.Column(db.Integer, default=0)  # Счет пользователя, по умолчанию 0
