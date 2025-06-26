import requests
from telegram import Bot
from datetime import datetime, timezone
import time

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # <-- Заменить на переменную окружения, если используешь Railway
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"  # <-- Тоже заменить на переменную

bot = Bot(token=TOKEN)

def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Ошибка при запросе к API: {response.status_code}")
        return []

    try:
        data = response.json().get("pairs", [])
    except Exception as e:
        print(f"Ошибка при разборе JSON: {e}")
        return []

    return data

def filter_tokens(tokens):
    results = []
    now = datetime.now(timezone.utc)
    for token in tokens:
        try:
            cap = token.get("fdv", 0)
            created_at = datetime.fromtimestamp(token["pairCreatedAt"] / 1000, tz=timezone.utc)
            age_minutes = (now - created_at).total_seconds() / 60
            info_links = [
                token.get("info", {}).get("website"),
                token.get("info", {}).get("telegram")
            ]
            if cap and cap <= 50000 and age_minutes <= 10 and any(info_links):
                results.append(token)
        except:
            continue
    return results

def send_alerts(tokens):
    for token in tokens:
        msg = (
            f"🚀💥 Новый токен: {token['baseToken']['symbol']}\n"
            f"Капа: {token['fdv']}$\n"
            f"{token['url']}"
        )
        bot.send_message(chat_id=CHAT_ID, text=msg)

while True:
    new_tokens = fetch_new_tokens()
    filtered = filter_tokens(new_tokens)
    if filtered:
        send_alerts(filtered)
    time.sleep(60)
