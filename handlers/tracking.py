
from aiogram import Router, F
from aiogram.enums import ChatType

from database.db import save_member

router = Router()


@router.message(F.chat.type.in_({
    ChatType.GROUP,
    ChatType.SUPERGROUP
}))
async def track_group_members(message):
    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    try:
        await save_member(
            group_id=message.chat.id,
            user=message.from_user
        )
    except Exception as error:
        print(f"Üye kaydedilemedi: {type(error).__name__}")
      
