
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from config import LOG_CHAT_ID


def current_time():
    return datetime.now(
        ZoneInfo("Europe/Istanbul")
    ).strftime("%d.%m.%Y - %H:%M:%S")


async def send_log(bot: Bot, message: str):
    log_text = (
        "🏴 <b>SANCAK TAG BOT — LOG</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"{message}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🕒 <b>Tarih:</b> {current_time()}"
    )

    try:
        await bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=log_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    except Exception as error:
        print(
            "Log gönderilemedi:",
            type(error).__name__
        )
