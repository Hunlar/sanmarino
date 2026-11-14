
import asyncio

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

        while True:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=30,
                    allowed_updates=allowed_updates
                )

                for update in updates:
                    offset = update.update_id + 1

                    await self.dispatcher.feed_update(
                        bot,
                        update
                    )

            except asyncio.CancelledError:
                raise

            except TelegramRetryAfter as error:
                await asyncio.sleep(error.retry_after)

            except Exception as error:
                print(
                    "Bot bağlantı hatası:",
                    type(error).__name__
                )
                await asyncio.sleep(5)

    async def add_bot(self, bot: Bot):
        info = await bot.get_me()

        async with self.lock:
            if info.id in self.bots:
                await bot.session.close()
                return

            try:
                # Webhook varsa kaldır, bekleyen güncellemeleri koru
                await bot.delete_webhook(
                    drop_pending_updates=False
                )

                self.bots[info.id] = bot

                self.tasks[info.id] = asyncio.create_task(
                    self.poll_bot(bot)
                )

            except Exception:
                self.bots.pop(info.id, None)
                self.tasks.pop(info.id, None)
                await bot.session.close()
                raise

    async def start(
        self,
        dispatcher: Dispatcher,
        main_bot: Bot
    ):
        self.dispatcher = dispatcher
        self.main_bot = main_bot

        # Ana botu başlat
        await self.add_bot(main_bot)

        # Kayıtlı klonları yükle
        try:
            saved_clones = await get_clones()
        except Exception as error:
            print(
                "Klon kayıtları yüklenemedi:",
                type(error).__name__
            )
            return

        for clone in saved_clones:
            bot = None

            try:
                bot = Bot(token=clone["token"])
                await self.add_bot(bot)

                print(
                    "Klon bot başlatıldı:",
                    clone["username"]
                )

            except Exception as error:
                print(
                    "Klon yüklenemedi:",
                    type(error).__name__
                )

                if bot is not None:
                    try:
                        await bot.session.close()
                    except Exception:
                        pass

    async def stop(self):
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


clone_runtime = CloneRuntime()
