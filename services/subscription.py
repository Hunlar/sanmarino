
from aiogram import Bot
from services.clone_runtime import clone_runtime
from config import REQUIRED_CHANNELS


def get_membership_bot(bot: Bot) -> Bot:
    # Klon botlarda üyelik kontrolü ana bot üzerinden yapılır.
    return clone_runtime.main_bot or bot


async def check_subscription(bot: Bot, user_id: int) -> bool:
    membership_bot = get_membership_bot(bot)

    for channel in REQUIRED_CHANNELS:
        try:
            member = await membership_bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status not in (
                "member",
                "administrator",
                "creator"
            ):
                return False

        except Exception as error:
            print("Üyelik kontrol hatası:", type(error).__name__)
            return False

    return True


async def missing_channels(bot: Bot, user_id: int) -> list:
    membership_bot = get_membership_bot(bot)
    missing = []

    for channel in REQUIRED_CHANNELS:
        try:
            member = await membership_bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status not in (
                "member",
                "administrator",
                "creator"
            ):
                missing.append(channel)

        except Exception:
            missing.append(channel)

    return missing
