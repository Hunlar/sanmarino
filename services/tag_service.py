
import os
from telethon import TelegramClient
from telethon.sessions import StringSession


class MTProtoService:
    def __init__(self):
        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        session_string = os.getenv("SESSION_STRING")

        self.client = None
        self.enabled = bool(api_id and api_hash and session_string)

        if self.enabled:
            self.client = TelegramClient(
                StringSession(session_string),
                int(api_id),
                api_hash
            )

    async def start(self):
        if not self.enabled:
            print("MTPROTO: API_ID, API_HASH veya SESSION_STRING eksik.")
            return

        await self.client.start()
        print("MTPROTO KULLANICI OTURUMU BASARILI")

    async def stop(self):
        if self.client and self.client.is_connected():
            await self.client.disconnect()

    async def get_group_members(self, chat):
        if not self.enabled or not self.client.is_connected():
            return None

        try:
            entity = await self.client.get_entity(chat)

            participants = await self.client.get_participants(
                entity,
                limit=None
            )

            members = []

            for user in participants:
                if user.bot or user.deleted:
                    continue

                full_name = " ".join(
                    part for part in [
                        user.first_name,
                        user.last_name
                    ] if part
                )

                members.append({
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": full_name or "İsimsiz Kullanıcı"
                })

            return members

        except Exception as error:
            print("MTPROTO UYE LISTESI HATASI:", repr(error))
            return None


mtproto_service = MTProtoService()
