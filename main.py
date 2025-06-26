import asyncio
import requests
from telegram import Bot

TOKEN = "7570198764:AAHHQQCc0ZDzyYRnDPPjxVFe-020KXhUYXc"
CHAT_ID = "5949980225"

bot = Bot(token=TOKEN)

async def send_error_to_telegram(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print("Ошибка при отправке в Telegram:", e)

async def main():
    try:
        # СПЕЦИАЛЬНАЯ ОШИБКА для теста:
        1 / 0
    except Exception as e:
        await send_error_to_telegram(f"🧨 Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
