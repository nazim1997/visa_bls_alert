import os
import requests
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import datetime
import aiohttp
import aiofiles

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

async def save_webpage(content):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"visa_page_{timestamp}.html"
    try:
        async with aiofiles.open(filename, mode='w', encoding='utf-8') as f:
            await f.write(content)
        print(f"Saved webpage as {filename}")
        return filename
    except Exception as e:
        print(f"Error saving webpage: {e}")
        return None

async def check_website(session):
    url = "https://algeria.blsspainglobal.com/DZA/account/login"
    try:
        async with session.get(url, timeout=1.5) as response:
            if response.status != 403:
                content = await response.text()
                filename = await save_webpage(content)
                return True, filename
            return False, None
    except Exception as e:
        # Uncomment for debugging if needed
        # print(f"Check error: {e}")
        return False, None

async def main():
    print("Starting ultra-high-frequency visa monitor (Ctrl+C to stop)...")
    print(f"Monitoring started at {datetime.datetime.now()}")
    
    # Use aiohttp for better async performance
    connector = aiohttp.TCPConnector(limit_per_host=1)
    timeout = aiohttp.ClientTimeout(total=2)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        while True:
            try:
                start_time = datetime.datetime.now()
                
                available, filename = await check_website(session)
                if available:
                    message = "🚀 VISA PAGE AVAILABLE!"
                    if filename:
                        message += f"\nPage saved as: {filename}"
                    await send_telegram_alert(message)
                    # Keep monitoring after success (remove break to continue)
                    break
                
                # Calculate remaining time to maintain 1ms cycle
                elapsed = (datetime.datetime.now() - start_time).total_seconds()
                remaining_wait = max(0, 0.001 - elapsed)
                await asyncio.sleep(remaining_wait)
                
            except KeyboardInterrupt:
                print("Monitoring stopped by user.")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                await asyncio.sleep(0.1)  # Brief pause after errors

if __name__ == "__main__":
    # Increase Windows selector event loop policy if on Windows
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
