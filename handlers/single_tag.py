
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import save_tag_log
from services.tag_service import (
    create_mention,
    send_tag_messages,
)
from handlers.tags import can_tag


router = Router()


@router.message(Command("tagone"))
async def tag_one_command(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        await message.reply(
            "❌ Bu komut yalnızca gruplarda kullanılabilir."
        )
        return

    if not message.reply_to_message:
        await message.reply(
            "⚠️ Etiketlemek istediğin kişinin mesajına yanıt vererek "
            "/tagone yazmalısın."
        )
        return

    target = message.reply_to_message.from_user

    if not target or target.is_bot:
        await message.reply("❌ Bu kullanıcı etiketlenemiyor.")
        return

    if not await can_tag(message):
        return

    mention = create_mention(
        target.id,
        target.full_name
    )

    sent_count = await send_tag_messages(
        message.bot,
        message.chat.id,
        [mention]
    )

    if sent_count:
        await save_tag_log(
            message.from_user.id,
            message.chat.id,
            "tagone",
            1
        )

        await message.reply(
            f"✅ {target.full_name} etiketlendi."
        )
    else:
        await message.reply(
            "❌ Etiketleme mesajı gönderilemedi."
        )
      
