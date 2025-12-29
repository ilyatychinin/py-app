import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token="8548525980:AAHLrQDeli8RqgH6DnmQ3xsmlRpBcn3TnKg")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    print("🤖 Bot started!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
