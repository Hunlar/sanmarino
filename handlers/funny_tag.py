
import random

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import get_members, save_tag_log
from services.tag_service import (
    create_mention,
    send_tag_messages,
)
from handlers.tags import can_tag


router = Router()


FUNNY_MESSAGES = [
    "🚨 SANCAK ALARMI! Herkes buraya toplansın!",
    "😂 Yoklama var! Kaçan olursa tek tek bulacağız!",
    "🔥 Sancak meydanında toplanıyoruz!",
    "📢 Duyduk duymadık demeyin! Herkes buraya!",
    "😎 Reis çağırıyor, kimse kaybolmasın!",
    "🐺 Kurtlar sofrasına herkes davetli!",
]


@router.message(Command("ktag"))
async def funny_tag_command(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        await message.reply(
            "❌ Bu komut yalnızca gruplarda kullanılabilir."
        )
        return

    if not await can_tag(message):
        return

    members = await get_members(message.chat.id)

    if not members:
        await message.reply(
            "❌ Henüz kayıtlı üye bulunamadı."
        )
        return

    mentions = []

    for user in members:
        if user["user_id"] == message.from_user.id:
            continue

        mentions.append(
            create_mention(
                user["user_id"],
                user["full_name"]
            )
        )

    if not mentions:
        await message.reply(
            "❌ Etiketlenecek başka üye bulunamadı."
        )
        return

    await message.answer(
        random.choice(FUNNY_MESSAGES)
    )

    sent_count = await send_tag_messages(
        message.bot,
        message.chat.id,
        mentions
    )

    await save_tag_log(
        message.from_user.id,
        message.chat.id,
        "ktag",
        len(mentions)
    )

    await message.reply(
        f"😂 Ktag tamamlandı!\n"
        f"Etiketlenen kayıt: {len(mentions)}\n"
        f"Gönderilen etiket mesajı: {sent_count}"
    )
