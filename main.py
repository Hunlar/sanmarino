
import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, validate_config
from database.db import init_db, close_db
from handlers import register_handlers
from services.clone_runtime import clone_runtime
from services.ban_service import GlobalBanMiddleware, init_ban_db
from services.mtproto_service import mtproto_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    validate_config()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()

    dispatcher.update.middleware(GlobalBanMiddleware())

    try:
        await init_db()
        await init_ban_db()

        register_handlers(dispatcher)

        try:
            await mtproto_service.start()
        except Exception:
            logging.exception("MTProto bağlantısı başlatılamadı.")

        await clone_runtime.start(
            dispatcher=dispatcher,
            main_bot=bot
        )

        while True:
            await asyncio.sleep(3600)

    finally:
        await mtproto_service.stop()
        await clone_runtime.stop()
        await bot.session.close()
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot kapatıldı.")
