import re
from datetime import datetime

def validate_email(email):
    # Перевірка формату email
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    return False

def validate_phone(phone):
    # Перевірка українського номера телефону (+380...)
    pattern = r'^\+380\d{9}$'
    if re.match(pattern, phone):
        return True
    return False

def validate_date(date_text):
    # Перевірка формату дати (РРРР-ММ-ДД)
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_int_input(prompt):
    # Безпечне отримання цілого числа від користувача
    while True:
        val = input(prompt).strip()
        if val.isdigit():
            return int(val)
        print("Помилка: введіть додатне ціле число.")