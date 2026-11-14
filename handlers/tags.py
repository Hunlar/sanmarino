
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import TAG_COOLDOWN
from database.db import get_members, save_tag_log
from services.tag_service import (
    create_mention,
    create_username_mention,
    create_emoji_mention,
    send_tag_messages,
)


router = Router()

last_tag_time = {}


async def is_group_admin(message: Message) -> bool:
    if message.chat.type not in ("group", "supergroup"):
        return False

    try:
        member = await message.bot.get_chat_member(
            message.chat.id,
            message.from_user.id
        )

        return member.status in ("administrator", "creator")

    except Exception:
        return False


async def can_tag(message: Message) -> bool:
    if not await is_group_admin(message):
        await message.reply("❌ Bu komutu yalnızca grup yöneticileri kullanabilir.")
        return False

    now = time.time()
    last_time = last_tag_time.get(message.chat.id, 0)

    if now - last_time < TAG_COOLDOWN:
        remaining = int(TAG_COOLDOWN - (now - last_time))
        await message.reply(
            f"⏳ Tekrar etiketleme için {remaining} saniye beklemelisin."
        )
        return False

    last_tag_time[message.chat.id] = now
    return True


async def run_tag(message: Message, mode: str):
    if not message.from_user:
        return

    if not await can_tag(message):
        return

    members = await get_members(message.chat.id)

    if not members:
        await message.reply(
            "❌ Henüz kayıtlı üye bulunamadı. "
            "Bot üyeleri mesajlardan tanıdıkça kaydedecek."
        )
        return

    mentions = []

    for user in members:
        user_id = user["user_id"]
        username = user["username"]
        full_name = user["full_name"]

        if mode == "tag":
            mentions.append(
                create_mention(user_id, full_name)
            )

        elif mode == "utag":
            if username:
                mentions.append(
                    create_username_mention(username)
                )

        elif mode == "etag":
            mentions.append(
                create_emoji_mention(user_id)
            )

    if not mentions:
        await message.reply("❌ Etiketlenecek uygun üye bulunamadı.")
        return

    sent_count = await send_tag_messages(
        message.bot,
        message.chat.id,
        mentions
    )

    await save_tag_log(
        message.from_user.id,
        message.chat.id,
        mode,
        len(mentions)
    )

    await message.reply(
        f"✅ Etiketleme tamamlandı.\n"
        f"Etiketlenen kayıt: {len(mentions)}\n"
        f"Gönderilen mesaj: {sent_count}"
    )


@router.message(Command("tag"))
async def tag_command(message: Message):
    await run_tag(message, "tag")


@router.message(Command("utag"))
async def username_tag_command(message: Message):
    await run_tag(message, "utag")


@router.message(Command("etag"))
async def emoji_tag_command(message: Message):
    await run_tag(message, "etag")
  
