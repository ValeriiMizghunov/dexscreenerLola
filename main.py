import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from telegram import Bot

# === НАСТРОЙКИ ===
TOKEN = '7570198764:AAHHQQCc0ZDzyYRnDPPjxVFe-020KXhUYXc'
CHAT_ID = 5949980225 

DEXSCREENER_URL = 'https://api.dexscreener.com/latest/dex/pairs/solana'

MIN_CAP = 4700
MIN_LIQUIDITY = 8900
MAX_AGE_MINUTES = 5
MIN_BUY = 12
MAX_SELL = 1
MIN_HOLDERS = 74

# === Функция для проверки, подходит ли токен ===
def is_token_valid(token):
    try:
        info = token['pairCreatedAt']
        created_at = datetime.fromtimestamp(info / 1000)
        age_minutes = (datetime.utcnow() - created_at).total_seconds() / 60

        cap = float(token.get('fdv', 0) or 0)
        liquidity = float(token.get('liquidity', {}).get('usd', 0) or 0)
        buys = int(token.get('txns', {}).get('m5', {}).get('buys', 0))
        sells = int(token.get('txns', {}).get('m5', {}).get('sells', 0))
        holders = int(token.get('holders', 0) or 0)
        is_mintable = token.get('isMintable', True)
        is_renounced = token.get('isRenounced', False)

        return (
            cap <= MIN_CAP and
            liquidity >= MIN_LIQUIDITY and
            age_minutes <= MAX_AGE_MINUTES and
            buys >= MIN_BUY and
            sells <= MAX_SELL and
            holders >= MIN_HOLDERS and
            not is_mintable and
            not is_renounced
        )
    except Exception as e:
        logging.warning(f"Ошибка при проверке токена: {e}")
        return False

# === Основная функция ===
async def monitor():
    bot = Bot(token=TOKEN)
    seen = set()

    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DEXSCREENER_URL) as resp:
                    data = await resp.json()
                    pairs = data.get('pairs', [])

                    for token in pairs:
                        pair_address = token.get('pairAddress')
                        if pair_address in seen:
                            continue

                        if is_token_valid(token):
                            seen.add(pair_address)

                            name = token.get('baseToken', {}).get('name')
                            symbol = token.get('baseToken', {}).get('symbol')
                            url = token.get('url')
                            msg = f"🚀 Новый токен: {name} ({symbol})\n🔗 {url}"
                            await bot.send_message(chat_id=CHAT_ID, text=msg)

        except Exception as e:
            logging.error(f"❌ Ошибка: {e}")
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Ошибка при запросе к API:\n{e}")

        await asyncio.sleep(10)

# === Запуск ===
if __name__ == '__main__':
    asyncio.run(monitor())
