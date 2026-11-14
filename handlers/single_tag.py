
import logging

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
        mention = create_mention(
            target.id,
            target.full_name
        )

        await message.answer(
            f"🎯 {mention}",
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
