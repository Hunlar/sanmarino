
import os
from telethon import TelegramClient

class MTProtoService:
    def __init__(self):
        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        bot_token = os.getenv("BOT_TOKEN")

        self.client = None
        self.enabled = bool(api_id and api_hash and bot_token)

        if self.enabled:
            self.client = TelegramClient(
                "sancak_mtproto",
                int(api_id),
                api_hash
            )

    async def start(self):
        if not self.enabled:
            print("MTPROTO: API bilgileri eksik.")
            return

        await self.client.start(bot_token=os.getenv("BOT_TOKEN"))
        print("MTPROTO BAGLANTISI BASARILI")

    async def stop(self):
        if self.client and self.client.is_connected():
            await self.client.disconnect()

    async def get_group_members(self, chat):
        if not self.enabled or not self.client.is_connected():
            return []

        try:
            participants = await self.client.get_participants(
                chat,
                limit=None
            )
            return participants
        except Exception as error:
            print("MTPROTO UYE LISTESI HATASI:", repr(error))
            return []

mtproto_service = MTProtoService()
