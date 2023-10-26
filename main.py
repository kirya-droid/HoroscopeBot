import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import RussianHoroscope
import EnglishHoroscope
import other_functions
logging.basicConfig(level=logging.INFO)
import sqlite3
import asyncio
import nasa_img
from subprocess import call
API_TOKEN = 'Yor Token'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT,
            sign TEXT,
            subscribe_horoscope INTEGER
        )
    ''')
conn.commit()


@dp.message_handler(commands=['start'])
async def chose_language(message: types.Message):
    keyboard = other_functions.create_buttons_from_json('menu', 'button.json')
    c.execute("INSERT OR REPLACE INTO users (user_id) VALUES (?)", (message.chat.id,))
    conn.commit()
    await message.answer("Choose your language: ", reply_markup=keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@dp.callback_query_handler(lambda c: c.data == 'RussianButton')
async def process_callback_russian(callback_query: types.CallbackQuery):
    c.execute('UPDATE users SET language = ? WHERE user_id = ?',
              ('Russian', callback_query.from_user.id))
    conn.commit()
    keyboard = other_functions.create_buttons_from_json('menu', 'Russian_button.json')
    await bot.send_message(callback_query.from_user.id, 'Меню:', reply_markup=keyboard)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data == 'EnglandButton')
async def process_callback_english(callback_query: types.CallbackQuery):
    # Сохранение выбранного языка в базе данных
    c.execute('UPDATE users SET language = ? WHERE user_id = ?',
              ('English', callback_query.from_user.id))
    conn.commit()
    keyboard = other_functions.create_buttons_from_json('menu', 'English_button.json')
    await bot.send_message(callback_query.from_user.id, 'Menu:', reply_markup=keyboard)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


@dp.callback_query_handler(lambda c: c.data == 'Horoscope')
async def chose_sign(callback_query: types.CallbackQuery):
    chose = other_functions.translate_text("choose_your_sign","messages.json",callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, chose, reply_markup=other_functions.button_sign(callback_query.from_user.id))
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

@dp.callback_query_handler(lambda c: c.data.startswith('zodiac:'))
async def process_callback_zodiac(callback_query: types.CallbackQuery):
    try:
        sign = callback_query.data.split(':')[1]
        c.execute('UPDATE users SET sign = ? WHERE user_id = ?',
                  (f'{sign}', callback_query.from_user.id))
        conn.commit()
    except :
        print('Знак зодиака уже выбран')
    finally:
        menu = other_functions.translate_text("menu", "messages.json", callback_query.from_user.id)
        keyboard = other_functions.create_buttons_from_json('horoscope', other_functions.checking_the_language(callback_query.from_user.id))
        await bot.send_message(callback_query.from_user.id, menu, reply_markup=keyboard)
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

@dp.callback_query_handler(lambda c: c.data == 'HoroscopeDay')
async def send_horoscope_day(callback_query: types.CallbackQuery):
    sign = other_functions.get_sign(callback_query.from_user.id)
    horoscope_day = other_functions.connect_bd(sign, callback_query.from_user.id)
    back_submenu = InlineKeyboardButton(
        text=other_functions.translate_text('back', 'messages.json', callback_query.from_user.id),
        callback_data="back_submenu")
    keyboard = InlineKeyboardMarkup().add(back_submenu)
    await bot.send_photo(callback_query.from_user.id,caption=horoscope_day, reply_markup=keyboard, photo=f'{nasa_img.api_nasa()}')
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)



@dp.callback_query_handler(lambda c: c.data == 'UnsubscribeHoroscope')
async def unsubscribe_horoscope_day(callback_query: types.CallbackQuery):
    # Update the database to indicate that the user has unsubscribed
    c.execute('UPDATE users SET subscribe_horoscope = ? WHERE user_id = ?',
              (0, callback_query.from_user.id))
    conn.commit()
    unsubscribe = other_functions.translate_text("unsubscribe", "messages.json", callback_query.from_user.id)

    # Send a confirmation message to the user
    back_submenu = InlineKeyboardButton(
        text=other_functions.translate_text('back', 'messages.json', callback_query.from_user.id),
        callback_data="back_submenu")
    keyboard = InlineKeyboardMarkup().add(back_submenu)
    await bot.send_message(callback_query.from_user.id, unsubscribe, reply_markup=keyboard)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

@dp.callback_query_handler(lambda c: c.data == 'SubscribeHoroscope')
async def subscribe_horoscope_day(callback_query: types.CallbackQuery):
    # Update the database to indicate that the user has subscribed
    c.execute('UPDATE users SET subscribe_horoscope = ? WHERE user_id = ?',
              (1, callback_query.from_user.id))
    conn.commit()
    back_submenu = InlineKeyboardButton(text=other_functions.translate_text('back','messages.json',callback_query.from_user.id), callback_data="back_submenu")
    keyboard = InlineKeyboardMarkup().add(back_submenu)
    subscribe = other_functions.translate_text("subscribe", "messages.json", callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, subscribe, reply_markup=keyboard)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

async def send_horoscope():
    while True:
        try:
            # Get all users who are subscribed to the horoscope
            c.execute('SELECT user_id FROM users WHERE subscribe_horoscope = 1')
            subscribed_users = c.fetchall()
            sleep_time = other_functions.dispatch_time(9, 0)
            await asyncio.sleep(sleep_time)

            for user in subscribed_users:
                back_submenu = InlineKeyboardButton(
                    text=other_functions.translate_text('back', 'messages.json', user[0]),
                    callback_data="back_submenu")
                keyboard = InlineKeyboardMarkup().add(back_submenu)
                sign = other_functions.get_sign(user[0])
                horoscope_day = other_functions.connect_bd(sign, user[0])
                await bot.send_photo(user[0], caption=horoscope_day, reply_markup=keyboard,
                                     photo=f'{nasa_img.api_nasa()}')
        except Exception as e:
            await bot.send_message('admin_id', f"horosope errore{e}")



@dp.message_handler(commands=['menu'])
@dp.callback_query_handler(lambda c: c.data == 'back')
async def back_callback_handler(callback_query: types.CallbackQuery):
    c.execute('SELECT language FROM users WHERE user_id = ?', (callback_query.from_user.id,))
    language = c.fetchone()[0]
    if language == "Russian":
        await process_callback_russian(callback_query)
    else:
        await process_callback_english(callback_query)
@dp.callback_query_handler(lambda c: c.data == 'back_submenu')
async def back_submenu_callback_handler(callback_query: types.CallbackQuery):
    await process_callback_zodiac(callback_query)
async def call_bd_horoscope():
    while True:
        sleep_time = other_functions.dispatch_time(8, 0)
        await asyncio.sleep(sleep_time)
        RussianHoroscope.main()
        EnglishHoroscope.main()

async def main():
    asyncio.create_task(call_bd_horoscope())
    asyncio.create_task(send_horoscope())
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
