
import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, validate_config
from database.db import init_db, close_db
from handlers import register_handlers
from services.clone_runtime import clone_runtime
from services.ban_service import (
    GlobalBanMiddleware,
    init_ban_db
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    validate_config()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()

    # Bütün botların güncellemelerinde ortak ban kontrolü
    dispatcher.update.middleware(
        GlobalBanMiddleware()
    )

    try:
        await init_db()
        await init_ban_db()

        register_handlers(dispatcher)

        await clone_runtime.start(
            dispatcher=dispatcher,
            main_bot=bot
        )

        while True:
            await asyncio.sleep(3600)

    finally:
        await clone_runtime.stop()
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot kapatıldı.")
