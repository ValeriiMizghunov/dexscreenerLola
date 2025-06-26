
import requests
from telegram import Bot
from datetime import datetime, timezone
import time
import json

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
bot = Bot(token=TOKEN)

def fetch_new_tokens():
    url = "https://api.dexscreener.com/latest/dex/pairs"
    response = requests.get(url)
    data = response.json().get("pairs", [])
    return data

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
        except:
            continue
    return results

def send_alerts(tokens):
    for token in tokens:
        msg = (
    f"🚀💥 Новый токен: {token['baseToken']['symbol']}\n"
    f"Kana: {token['fdv']}$\n"
    f"{token['url']}"
        bot.send_message(chat_id=CHAT_ID, text=msg)

while True:
    new_tokens = fetch_new_tokens()
    filtered = filter_tokens(new_tokens)
    if filtered:
        send_alerts(filtered)
    time.sleep(60)
