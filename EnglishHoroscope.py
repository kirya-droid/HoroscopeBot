import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures
import sqlite3


def get_horoscope(sign):
    url = f'https://www.aol.com/horoscopes/daily/{sign}/' #rambler
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    result = soup.find('div', class_='reading') #rambler
    data = soup.find('h1', class_='title')#rambler data
    if result is not None:
        conn = sqlite3.connect('englishhoroscope.db')
        new_text = result.text.replace("see more from tarot.com", "")
        horoscope = data.text + ".\n " + new_text
        c = conn.cursor()
        c.execute("UPDATE horoscopes SET text = ? WHERE sign = ?", (horoscope, sign))
        conn.commit()
        conn.close()
    else:
        print("Не удалось найти элемент")

def main():
    zodiac_signs = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
    conn = sqlite3.connect('englishhoroscope.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS horoscopes (sign text, text text)''')
    for sign in zodiac_signs:
        c.execute("INSERT OR REPLACE INTO horoscopes (sign) VALUES (?)", (sign,))


    conn.commit()
    conn.close()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_horoscope, zodiac_signs)