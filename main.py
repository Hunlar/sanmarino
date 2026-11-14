
import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN, validate_config
from database.db import init_db, close_db
from handlers import register_handlers
from services.clone_runtime import clone_runtime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():
    validate_config()

    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()

    try:
        # Veritabanını başlat
        await init_db()
        logging.info("Veritabanı başlatıldı.")

        # Bütün komutları bağla
        register_handlers(dispatcher)
        logging.info("Komutlar yüklendi.")

        # Ana bot ve klon botları çalıştır
        await clone_runtime.start(
            dispatcher=dispatcher,
            main_bot=bot
        )

        logging.info("Sancak Tag Bot çalışıyor.")

        # Botların çalışmasını bekle
        while True:
            await asyncio.sleep(3600)

    finally:
        await clone_runtime.stop()
        await close_db()
        logging.info("Bot sistemi kapatıldı.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot durduruldu.")
        
