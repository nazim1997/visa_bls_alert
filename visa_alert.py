import os
import requests
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

load_dotenv()
# Telegram Bot Settings
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Validate credentials
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Missing Telegram credentials in .env file!")

async def send_telegram_alert(message):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print("Alert sent!")
    except TelegramError as e:
        print(f"Telegram error: {e}")

def check_website() -> bool:
    url = "https://algeria.blsspainvisa.com/"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code != 403
    except Exception as e:
        print(f"Check error: {e}")
        return False

async def main():
    print("Starting visa monitor (Ctrl+C to stop)...")
    while True:
        if check_website():
            await send_telegram_alert("🚀 VISA PAGE AVAILABLE!")
            break  # Remove this line to keep monitoring after success
        await asyncio.sleep(0.1)  # Tiny delay to prevent CPU meltdown

if __name__ == "__main__":
    asyncio.run(main())
