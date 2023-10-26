import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
from datetime import datetime, timedelta


import RussianHoroscope
conn = sqlite3.connect('users.db')
c = conn.cursor()
def create_buttons_from_json(key: str, json_name: str):
    with open(f"json/{json_name}", 'r', encoding='utf-8') as f:
        data = json.load(f)
    buttons = data.get(key, [])
    keyboard = InlineKeyboardMarkup()
    for button in buttons:
        keyboard.add(InlineKeyboardButton(button['text'], callback_data=button['callback_data']))
    return keyboard
def translate_text(key: str, json_name: str, user_id: int):
    c.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    language = c.fetchone()[0]
    with open(f"json/{json_name}", 'r', encoding='utf-8') as f:
        data = json.load(f)
    text = data[key][language]
    return text
def button_sign(id):
    c.execute('SELECT language FROM users WHERE user_id = ?', (id,))
    language = c.fetchone()[0]
    zodiac_signs = {
        'Russian': {
            'Aries': 'Овен ♈️',
            'Taurus': 'Телец ♉️',
            'Gemini': 'Близнецы ♊️',
            'Cancer': 'Рак ♋️',
            'Leo': 'Лев ♌️',
            'Virgo': 'Дева ♍️',
            'Libra': 'Весы ♎️',
            'Scorpio': 'Скорпион ♏️',
            'Sagittarius': 'Стрелец ♐️',
            'Capricorn': 'Козерог ♑️',
            'Aquarius': 'Водолей ♒️',
            'Pisces': 'Рыбы ♓️'
        },
        'English': {
            'Aries': 'Aries ♈️',
            'Taurus': 'Taurus ♉️',
            'Gemini': 'Gemini ♊️',
            'Cancer': 'Cancer ♋️',
            'Leo': 'Leo ♌️',
            'Virgo': 'Virgo ♍️',
            'Libra': 'Libra ♎️',
            'Scorpio': 'Scorpio ♏️',
            'Sagittarius': 'Sagittarius ♐️',
            'Capricorn': 'Capricorn ♑️',
            'Aquarius': 'Aquarius ♒️',
            'Pisces': 'Pisces ♓️'
        }
    }
    keyboard = InlineKeyboardMarkup()
    for sign, text in zodiac_signs[language].items():
        keyboard.add(InlineKeyboardButton(text, callback_data=f'zodiac:{sign}'))
    return keyboard
def checking_the_language(user_id):
    c.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    language = c.fetchone()[0]
    if language == 'Russian':
        file = 'Russian_button.json'
    else:
        file = 'English_button.json'
    return file

def get_sign(user_id):
    c.execute('SELECT sign FROM users WHERE user_id = ?', (user_id,))

    sign = c.fetchone()[0]
    sign_lower = sign.lower()
    return sign_lower
def connect_bd(sign, user_id):
    c.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    language = c.fetchone()[0]
    if language == "Russian":
        conn = sqlite3.connect('russianhoroscope.db')
    else:
        conn = sqlite3.connect('englishhoroscope.db')
    co = conn.cursor()
    co.execute('SELECT text FROM horoscopes WHERE sign = ?', (sign,))
    result = co.fetchone()[0]
    conn.commit()
    conn.close()
    return result
def function_subscribe(user_id, subscribe_field):# потом допишу "!!!!!!!!"!!"
    c.execute(f'UPDATE users SET {subscribe_field} = ? WHERE user_id = ?',
              (1, user_id))
    conn.commit()

def  function_unsubscribe():
    pass

def dispatch_time(hour,minute):
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target_time:
        target_time += timedelta(days=1)
    sleep_time = (target_time - now).total_seconds()
    return  sleep_time