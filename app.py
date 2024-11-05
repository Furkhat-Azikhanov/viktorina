import random  # Импортируем модуль для случайного выбора вопроса
from flask import Flask, render_template, redirect, url_for, request, session  # Импортируем необходимые функции Flask
from werkzeug.security import generate_password_hash, check_password_hash  # Для безопасного хэширования паролей
from models import db, User  # Импортируем базу данных и модель пользователя
from config import Config  # Импортируем конфигурационный файл
import requests  # Импортируем библиотеку для выполнения HTTP-запросов (погода)

app = Flask(__name__)  # Создаем экземпляр Flask приложения
app.config.from_object(Config)  # Загружаем конфигурации из файла config.py
db.init_app(app)  # Инициализируем базу данных с нашим приложением

# Создаем все таблицы в базе данных, если они не существуют
with app.app_context():
    db.create_all()

# Пример вопросов для викторины
questions = [
    {"question": "Что такое Flask?", "options": ["Фреймворк", "Язык программирования", "База данных", "Операционная система"], "answer": "Фреймворк"},
    {"question": "Какой метод используется для добавления элемента в конец списка?", "options": ["insert()", "append()", "push()", "add()"], "answer": "append()"},
    {"question": "Что делает метод 'pop()'?", "options": ["Удаляет последний элемент", "Добавляет элемент", "Обновляет элемент", "Клонирует список"], "answer": "Удаляет последний элемент"},
]

# Маршрут для главной страницы с прогнозом погоды
@app.route('/')
def home():
    city = request.args.get('city', 'Almaty')  # Получаем название города из параметра запроса, по умолчанию "Almaty"
    weather_data = get_weather(city)  # Получаем данные о погоде для указанного города
    return render_template('home.html', weather_data=weather_data)  # Отправляем данные в шаблон

# Функция для получения прогноза погоды через API
def get_weather(city):
    api_key = app.config['WEATHER_API_KEY']  # Берем API-ключ из конфигурации
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=3"  # URL для API с параметрами
    try:
        response = requests.get(url).json()  # Выполняем запрос и получаем JSON-ответ
        print("Ответ от API погоды:", response)  # Отладка: выводим ответ от API
        if 'forecast' in response:  # Проверяем, есть ли в ответе ключ 'forecast'
            return response['forecast']['forecastday']  # Возвращаем данные прогноза
        else:
            print("Ошибка: поле 'forecast' отсутствует в ответе API.")  # Отладка: сообщение об ошибке
            return []
    except requests.RequestException as e:
        print(f"Ошибка при подключении к API погоды: {e}")  # Обработка ошибок соединения
        return []
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")  # Обработка других ошибок
        return []

# Маршрут для страницы регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':  # Если метод POST, обрабатываем данные формы
        username = request.form['username']
        display_name = request.form['display_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:  # Проверяем, совпадают ли пароли
            return "Пароли не совпадают"
        if User.query.filter_by(username=username).first():  # Проверяем уникальность логина
            return "Логин уже существует"
        if User.query.filter_by(display_name=display_name).first():  # Проверяем уникальность отображаемого имени
            return "Отображаемое имя уже занято"
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Хэшируем пароль
        new_user = User(username=username, display_name=display_name, password=hashed_password)  # Создаем нового пользователя
        db.session.add(new_user)  # Добавляем в базу данных
        db.session.commit()  # Сохраняем изменения
        return redirect(url_for('login'))  # Перенаправляем на страницу входа
    return render_template('register.html')  # Если метод GET, отображаем форму регистрации

# Маршрут для страницы входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Если метод POST, обрабатываем данные формы
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()  # Ищем пользователя по логину
        if user and check_password_hash(user.password, password):  # Проверяем пароль
            session['user_id'] = user.id  # Сохраняем идентификатор пользователя в сессии
            session['username'] = user.display_name  # Сохраняем имя пользователя в сессии
            return redirect(url_for('home'))  # Перенаправляем на главную страницу
        return "Неверный логин или пароль"
    return render_template('login.html')  # Если метод GET, отображаем форму входа

# Маршрут для выхода из системы
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем user_id из сессии
    session.pop('username', None)  # Удаляем имя пользователя из сессии
    return redirect(url_for('home'))  # Перенаправляем на главную страницу

# Маршрут для викторины
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:  # Проверяем, вошел ли пользователь
        return redirect(url_for('login'))
    
    if 'current_question' not in session or session.get('correct_answered', False):  # Если новый вопрос нужен
        question = random.choice(questions)  # Выбираем случайный вопрос
        session['current_question'] = question  # Сохраняем вопрос в сессии
        session['correct_answered'] = False  # Сбрасываем флаг правильного ответа

    question = session['current_question']  # Получаем текущий вопрос из сессии
    incorrect_answer = False  # Флаг для отслеживания неправильного ответа

    if request.method == 'POST':  # Если POST, обрабатываем ответ
        selected_option = request.form.get('option')  # Получаем выбранный ответ
        print(f"Выбранный ответ: {selected_option}")  # Отладка: выводим выбранный ответ
        print(f"Правильный ответ: {question['answer']}")  # Отладка: выводим правильный ответ
        
        if selected_option.strip().lower() == question["answer"].strip().lower():  # Проверка ответа
            user = User.query.get(session['user_id'])  # Получаем пользователя по ID из сессии
            if user:
                user.score += 1  # Увеличиваем счет пользователя
                db.session.commit()  # Сохраняем изменения в базе данных
            session['correct_answered'] = True  # Устанавливаем флаг, что ответ верный
            return redirect(url_for('quiz'))  # Перезагружаем страницу для нового вопроса
        else:
            incorrect_answer = True  # Если ответ неверный, показываем кнопку "Продолжить опрос"

    return render_template('quiz.html', question=question, incorrect_answer=incorrect_answer)  # Отображаем вопрос

# Маршрут для таблицы лидеров
@app.route('/leaderboard')
def leaderboard():
    leaders = User.query.order_by(User.score.desc()).limit(10).all()  # Получаем топ-10 пользователей по счету
    return render_template('leaderboard.html', leaders=leaders)  # Отправляем данные в шаблон таблицы лидеров

if __name__ == '__main__':
    app.run(debug=True)  # Запускаем приложение в режиме отладки
