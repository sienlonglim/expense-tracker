import asyncio
import os

from dotenv import load_dotenv

from expense_tracker_bot import start_polling

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    DB_PATH = os.getenv("DB_PATH")
    if not TOKEN:
        raise ValueError("BOT_TOKEN not set in .env")
    if not DB_PATH:
        raise ValueError("DB_PATH not set in .env")
    asyncio.run(start_polling(TOKEN))
