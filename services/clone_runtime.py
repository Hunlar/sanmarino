
import asyncio

from aiogram import Bot, Dispatcher

from database.clone_db import get_clones


class CloneRuntime:
    def __init__(self):
        self.dispatcher = None
        self.main_bot = None
        self.clone_bots = {}
        self.polling_task = None
        self.lock = asyncio.Lock()

    async def start(self, dispatcher: Dispatcher, main_bot: Bot):
        self.dispatcher = dispatcher
        self.main_bot = main_bot

        saved_clones = await get_clones()

        for clone in saved_clones:
            try:
                bot = Bot(token=clone["token"])
                info = await bot.get_me()
                self.clone_bots[info.id] = bot
            except Exception as error:
                print(
                    "Klon yüklenemedi:",
                    type(error).__name__
                )

        self.polling_task = asyncio.create_task(
            self._poll()
        )

    async def _poll(self):
        bots = [
            self.main_bot,
            *self.clone_bots.values()
        ]

        await self.dispatcher.start_polling(
            *bots,
            handle_signals=False,
            close_bot_session=False
        )

    async def add_clone(self, token: str):
        async with self.lock:
            bot = Bot(token=token)

            try:
                info = await bot.get_me()

                if info.id in self.clone_bots:
                    await bot.session.close()
                    return True

                if self.polling_task:
                    self.polling_task.cancel()

                    try:
                        await self.polling_task
                    except asyncio.CancelledError:
                        pass

                self.clone_bots[info.id] = bot

                self.polling_task = asyncio.create_task(
                    self._poll()
                )

                return True

            except Exception:
                await bot.session.close()
                raise

    async def stop(self):
        if self.polling_task:
            self.polling_task.cancel()

            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass

        for bot in self.clone_bots.values():
            await bot.session.close()

        self.clone_bots.clear()


clone_runtime = CloneRuntime()
