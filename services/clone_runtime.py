
import asyncio
import traceback

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramRetryAfter

from database.clone_db import get_clones


class CloneRuntime:
    def __init__(self):
        self.dispatcher = None
        self.main_bot = None
        self.bots = {}
        self.tasks = {}
        self.lock = asyncio.Lock()

    async def poll_bot(self, bot: Bot):
        offset = None
        allowed_updates = self.dispatcher.resolve_used_update_types()

        print("BOT POLLING BASLADI:", bot.id)
        print("DINLENEN GUNCELLEMELER:", allowed_updates)

        while True:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=30,
                    allowed_updates=allowed_updates
                )

                for update in updates:
                    offset = update.update_id + 1

                    if update.message:
                        print(
                            "GELEN MESAJ:",
                            "BOT:", bot.id,
                            "SOHBET:", update.message.chat.type,
                            "CHAT ID:", update.message.chat.id,
                            "METIN:", repr(update.message.text)
                        )
                    else:
                        print(
                            "GELEN GUNCELLEME:",
                            "BOT:", bot.id,
                            "TUR:", update.event_type
                        )

                    await self.dispatcher.feed_update(bot, update)

            except asyncio.CancelledError:
                raise

            except TelegramRetryAfter as error:
                print("TELEGRAM BEKLEME HATASI:", error.retry_after)
                await asyncio.sleep(error.retry_after)

            except Exception:
                print("BOT POLLING HATASI:", bot.id)
                traceback.print_exc()
                await asyncio.sleep(5)

    async def add_bot(self, bot: Bot):
        info = await bot.get_me()

        async with self.lock:
            if info.id in self.bots:
                await bot.session.close()
                return

            try:
                await bot.delete_webhook(drop_pending_updates=False)

                self.bots[info.id] = bot

                self.tasks[info.id] = asyncio.create_task(
                    self.poll_bot(bot)
                )

                print(
                    "BOT SISTEME EKLENDI:",
                    info.username,
                    info.id
                )

            except Exception:
                self.bots.pop(info.id, None)
                self.tasks.pop(info.id, None)

                await bot.session.close()
                raise

    async def start(self, dispatcher: Dispatcher, main_bot: Bot):
        self.dispatcher = dispatcher
        self.main_bot = main_bot

        print("ANA BOT BASLATILIYOR...")

        await self.add_bot(main_bot)

        try:
            saved_clones = await get_clones()

        except Exception:
            print("KLON KAYITLARI YUKLENEMEDI:")
            traceback.print_exc()
            return

        for clone in saved_clones:
            bot = None

            try:
                bot = Bot(token=clone["token"])

                await self.add_bot(bot)

                print(
                    "KLON BOT BASLATILDI:",
                    clone["username"]
                )

            except Exception:
                print(
                    "KLON YUKLENEMEDI:",
                    clone.get("username", "Bilinmeyen")
                )
                traceback.print_exc()

                if bot is not None:
                    try:
                        await bot.session.close()
                    except Exception:
                        pass

    async def stop(self):
        print("BOTLAR KAPATILIYOR...")

        for task in self.tasks.values():
            task.cancel()

        if self.tasks:
            await asyncio.gather(
                *self.tasks.values(),
                return_exceptions=True
            )

        for bot in self.bots.values():
            try:
                await bot.session.close()
            except Exception:
                pass

        self.tasks.clear()
        self.bots.clear()

        self.main_bot = None
        self.dispatcher = None

        print("BOTLAR KAPATILDI.")


clone_runtime = CloneRuntime()
