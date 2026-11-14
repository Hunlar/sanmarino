
import html

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter

from database.db import get_members


async def get_group_members(group_id: int):
    return await get_members(group_id)


def create_mention(user_id: int, full_name: str) -> str:
    safe_name = html.escape(full_name or "İsimsiz Kullanıcı")

    return (
        f'<a href="tg://user?id={user_id}">'
        f'{safe_name}</a>'
    )


def create_username_mention(username: str) -> str:
    safe_username = html.escape(username.lstrip("@"))

    return f"@{safe_username}"


def create_emoji_mention(user_id: int) -> str:
    return f'<a href="tg://user?id={user_id}">🎯</a>'


def split_messages(items, max_length=3500):
    messages = []
    current = ""

    for item in items:
        addition = item + "\n"

        if len(current) + len(addition) > max_length:
            if current:
                messages.append(current)

            current = addition
        else:
            current += addition

    if current:
        messages.append(current)

    return messages


async def send_tag_messages(
    bot: Bot,
    chat_id: int,
    mentions: list
):
    messages = split_messages(mentions)
    sent_count = 0

    for message in messages:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

            sent_count += 1

        except TelegramRetryAfter as error:
            await bot.send_message(
                chat_id=chat_id,
                text="Etiketleme hız sınırına takıldı. Daha sonra tekrar deneyin."
            )
            break

        except Exception as error:
            print(
                f"Etiket mesajı gönderilemedi: "
                f"{type(error).__name__}"
            )
            break

    return sent_count
          
