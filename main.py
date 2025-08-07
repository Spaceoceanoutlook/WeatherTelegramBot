import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import telebot
from telebot import types
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("TOKEN", '')
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = 'Екатеринбург'
UNITS = 'metric'
LANG = 'ru'

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    types.BotCommand("weather", "Получить прогноз"),
])

def fetch_weather(endpoint: str, params: dict):
    url = f"http://api.openweathermap.org/data/2.5/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка запроса к {endpoint}: {e}")
        return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "<b>Меню</b> ➡️ Получить прогноз", parse_mode="HTML")

@bot.message_handler(commands=['weather'])
def get_weather(message):
    params = {
        'q': CITY,
        'appid': API_KEY,
        'units': UNITS,
        'lang': LANG
    }

    current_data = fetch_weather("weather", params)
    forecast_data = fetch_weather("forecast", params)

    if not current_data or not forecast_data:
        bot.reply_to(message, "❌ Ошибка получения данных о погоде")
        return

    try:
        temp = round(current_data["main"]["temp"])
        description = current_data["weather"][0]["description"].capitalize()
        humidity = current_data["main"]["humidity"]

        tz = ZoneInfo("Asia/Yekaterinburg")
        sunrise = datetime.fromtimestamp(current_data["sys"]["sunrise"], tz=tz).strftime('%H:%M')
        sunset = datetime.fromtimestamp(current_data["sys"]["sunset"], tz=tz).strftime('%H:%M')

        forecast_list = forecast_data.get("list", [])[:12]
        forecast_lines = [
            f"{datetime.fromtimestamp(item['dt'], tz=tz).strftime('%H:%M')}: "
            f"{round(item['main']['temp'])}°C, {item['weather'][0]['description']}"
            for item in forecast_list
        ]

        weather_message = (
            f"🏙️ Погода в {CITY}e\n\n"
            f"🌡️ Сейчас: {temp}°C\n"
            f"☁️ {description}\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌅 Восход: {sunrise} | 🌇 Закат: {sunset}\n\n"
            f"📅 Прогноз на 36 часов:\n" + "\n".join(forecast_lines)
        )

        bot.reply_to(message, weather_message)

    except Exception as e:
        bot.reply_to(message, f"⚠️ Произошла ошибка при обработке данных: {e}")

if __name__ == '__main__':
    print("🤖 Бот погоды Екатеринбурга запущен...")
    bot.infinity_polling()
