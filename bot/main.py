import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN  # ← config.py, НЕ cobalt!
from handlers import router

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    print("🤖 Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
