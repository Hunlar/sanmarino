
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import REQUIRED_CHANNELS


async def check_subscription(bot: Bot, user_id: int) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status not in ("member", "administrator", "creator"):
                return False

        except (TelegramBadRequest, TelegramForbiddenError):
            return False
        except Exception:
            return False

    return True


async def missing_channels(bot: Bot, user_id: int) -> list:
    missing = []

    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status not in ("member", "administrator", "creator"):
                missing.append(channel)

        except Exception:
            missing.append(channel)

    return missing
