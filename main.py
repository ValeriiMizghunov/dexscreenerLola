import requests
from datetime import datetime, timezone
import time
import traceback

TOKEN = 7570198764:AAHHQQCc0ZDzyYRnDPPjxVFe-020KXhUYXc
CHAT_ID = 5949980225  

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

def fetch_new_tokens():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Ошибка при запросе к API: {response.status_code}")
        return response.json().get("pairs", [])
    except Exception as e:
        send_message(f"❌ Ошибка при запросе:\n<pre>{traceback.format_exc()}</pre>")
        return []

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
            send_message(f"⚠️ Ошибка в фильтрации:\n<pre>{traceback.format_exc()}</pre>")
            continue
    return results

def send_alerts(tokens):
    for token in tokens:
        try:
            msg = (
                f"🚀💥 Новый токен: {token['baseToken']['symbol']}\n"
                f"Капитализация: {token['fdv']}$\n"
                f"Ссылка: {token['url']}"
            )
            send_message(msg)
        except Exception as e:
            send_message(f"⚠️ Ошибка при отправке токена:\n<pre>{traceback.format_exc()}</pre>")

while True:
    new_tokens = fetch_new_tokens()
    filtered = filter_tokens(new_tokens)
    if filtered:
        send_alerts(filtered)
    time.sleep(60)
