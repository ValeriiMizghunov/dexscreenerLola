import requests
from telegram import Bot
from datetime import datetime, timezone
import time

# 🔐 Твои данные
TOKEN = "7570198764:AAHHQQCc0ZDzyYRnDPPjxVFe-020KXhUYXc"        
CHAT_ID = "5949980225"          

bot = Bot(token=TOKEN)

# ✅ Получение токенов
def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs"  # или /solana и т.д.
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("pairs", [])
        return data
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"❌ Ошибка при запросе к API:\n{e}")
        return []

# ✅ Фильтрация по условиям
def filter_tokens(tokens):
    results = []
    now = datetime.now(timezone.utc)
    for token in tokens:
        try:
            cap = token.get("fdv", 0)
            created_at = datetime.fromtimestamp(token["pairCreatedAt"] / 1000, tz=timezone.utc)
            age_minutes = (now - created_at).total_seconds() / 60
            info_links = [token.get("info", {}).get("website"), token.get("info", {}).get("telegram")]

            if cap and cap <= 50000 and age_minutes <= 10 and any(info_links):
                results.append(token)
        except Exception as e:
            continue
    return results

# ✅ Отправка алертов в Telegram
def send_alerts(tokens):
    for token in tokens:
        try:
            msg = (
                f"🚀💥 Новый токен: {token['baseToken']['symbol']}\n"
                f"Капа: {token.get('fdv', '❓')}$\n"
                f"{token.get('url', 'Нет ссылки')}"
            )
            bot.send_message(chat_id=CHAT_ID, text=msg)
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"❌ Ошибка при отправке алерта:\n{e}")

# 🔁 Цикл: каждые 60 секунд
while True:
    new_tokens = fetch_new_tokens()
    filtered = filter_tokens(new_tokens)
    if filtered:
        send_alerts(filtered)
    time.sleep(60)
