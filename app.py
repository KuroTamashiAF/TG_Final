from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.strategy import FSMStrategy

import asyncio
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from database.engine import create_db, session_marker, drop_db
from middlewares.db import DataBaseSession
from handlers.user_private import user_private_router
from handlers.admin_private import admin_router


from handlers.user_group import user_group_router


bot = Bot(
    token=os.getenv("TG_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
bot.my_admins_list = []



dp = Dispatcher()


dp.include_routers(
    user_private_router,
)
dp.include_router(user_group_router)
dp.include_router(admin_router)


async def main():
    await create_db()
    # await drop_db()
    dp.update.middleware(DataBaseSession(session_pool=session_marker))
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
