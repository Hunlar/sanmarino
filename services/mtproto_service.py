
import os
import logging

from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)


class MTProtoService:

    def __init__(self):
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")
        self.clients = {}

        self.enabled = bool(self.api_id and self.api_hash)

        if self.api_id:
            self.api_id = int(self.api_id)

    async def _get_client(self, bot_token):

        if not self.enabled:
            raise RuntimeError(
                "API_ID veya API_HASH eksik."
            )

        if not bot_token:
            raise RuntimeError("BOT_TOKEN bulunamadı.")

        client = self.clients.get(bot_token)

        if client and client.is_connected():
            if await client.is_user_authorized():
                return client

        if client:
            try:
                await client.disconnect()
            except Exception:
                pass

        client = TelegramClient(
            StringSession(),
            self.api_id,
            self.api_hash
        )

        await client.start(bot_token=bot_token)

        self.clients[bot_token] = client

        logger.info(
            "MTProto bot bağlantısı hazır: %s",
            (await client.get_me()).id
        )

        return client

    async def start(self):

        if not self.enabled:
            logger.warning(
                "MTProto kapalı: API_ID/API_HASH eksik."
            )
            return

        bot_token = os.getenv("BOT_TOKEN")

        if bot_token:
            try:
                await self._get_client(bot_token)
                logger.info("Ana bot MTProto bağlantısı hazır.")
            except Exception:
                logger.exception(
                    "MTProto başlatılamadı."
                )

    async def stop(self):

        for client in list(self.clients.values()):
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                logger.exception(
                    "MTProto bağlantısı kapatılamadı."
                )

        self.clients.clear()

    async def get_group_members(self, chat, bot_token=None):

        if bot_token is None:
            bot_token = os.getenv("BOT_TOKEN")

        client = await self._get_client(bot_token)

        try:
            entity = await client.get_entity(chat)

            participants = await client.get_participants(
                entity,
                limit=None
            )

            members = []
            seen_ids = set()

            for user in participants:

                if getattr(user, "bot", False):
                    continue

                if getattr(user, "deleted", False):
                    continue

                if user.id in seen_ids:
                    continue

                seen_ids.add(user.id)

                full_name = " ".join(
                    part for part in (
                        getattr(user, "first_name", None),
                        getattr(user, "last_name", None)
                    ) if part
                ).strip()

                members.append({
                    "user_id": user.id,
                    "username": getattr(user, "username", None),
                    "full_name": full_name or "İsimsiz Kullanıcı"
                })

            logger.info(
                "Grup üyeleri listelendi: %s kişi",
                len(members)
            )

            return members

        except Exception as error:

            logger.exception(
                "Grup üyeleri alınamadı."
            )

            raise RuntimeError(
                f"{type(error).__name__}: {error}"
            ) from error


mtproto_service = MTProtoService()
                
