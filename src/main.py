import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
from database.database import Database
from handlers.user import router as user_router
from handlers.admin import router as admin_router
from misc.keyboard import init_buttons_mapping


bot = Bot(token=config.BOT_TOKEN)

dp = Dispatcher()
dp.include_router(user_router)
dp.include_router(admin_router)

db = Database()


async def main():
    logging.basicConfig(level=logging.INFO)
    await init_buttons_mapping()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
