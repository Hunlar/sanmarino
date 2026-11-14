
import logging
from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.tag_service import create_mention
from handlers.tags import can_tag
from database.db import save_tag_log


router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("tagone"))
async def tag_one_command(message: Message):
    print(
        "TAGONE HANDLER CALISTI:",
        repr(message.text),
        "BOT ID:",
        message.bot.id
    )

    if message.chat.type not in ("group", "supergroup"):
        await message.reply(
            "❌ Bu komut yalnızca gruplarda kullanılabilir."
        )
        return

    if not message.from_user:
        return

    if not message.reply_to_message:
        await message.reply(
            "⚠️ Etiketlemek istediğin kişinin mesajına yanıt vererek "
            "/tagone yazmalısın."
        )
        return

    target = message.reply_to_message.from_user

    if not target:
        await message.reply(
            "❌ Bu mesajın sahibini tespit edemedim."
        )
        return

    if target.is_bot:
        await message.reply(
            "❌ Botları etiketleyemezsin."
        )
        return

    if not await can_tag(message):
        return

    try:
        # Komuttaki özel mesajı al: /tagone - mesaj
        custom_text = ""

        if message.text:
            parts = message.text.split(maxsplit=1)

            if len(parts) > 1:
                argument = parts[1].strip()

                if argument.startswith("-"):
                    custom_text = argument[1:].strip()

        mention = create_mention(
            target.id,
            target.full_name
        )

        if custom_text:
            response = (
                f"🎯 {escape(custom_text)}\n\n"
                f"{mention}"
            )
        else:
            response = f"🎯 {mention}"

        await message.answer(
            response,
            parse_mode="HTML"
        )

        await save_tag_log(
            message.from_user.id,
            message.chat.id,
            "tagone",
            1
        )

    except Exception:
        logger.exception("Tagone işlemi başarısız.")
        await message.reply(
            "❌ Tekli etiketleme sırasında hata oluştu. "
            "Heroku loglarını kontrol et."
        )
