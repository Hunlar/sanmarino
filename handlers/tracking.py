
import logging

from aiogram import Router, F
from aiogram.enums import ChatType

from database.db import save_member, save_bot_group

router = Router()
logger = logging.getLogger(__name__)


@router.message(
    F.chat.type.in_({
        ChatType.GROUP,
        ChatType.SUPERGROUP
    })
)
async def track_group_members(message):

    print(
        "GROUP MESSAGE:",
        repr(message.text),
        "BOT ID:",
        message.bot.id
    )

    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    try:
        await save_member(
            group_id=message.chat.id,
            user=message.from_user
        )

        await save_bot_group(
            bot_id=message.bot.id,
            group_id=message.chat.id
        )

    except Exception:
        logger.exception("Grup üyesi kaydedilemedi.")
