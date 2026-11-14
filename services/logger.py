
from aiogram import Bot
from config import LOG_CHAT_ID


async def send_log(bot: Bot, message: str):
    try:
        await bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=message
        )
    except Exception as error:
        print(f"Log gönderilemedi: {type(error).__name__}")
      
