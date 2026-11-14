
import html

from aiogram import Bot

from database.clone_db import save_clone
from services.logger import send_log
from services.clone_runtime import clone_runtime


async def create_clone(
    main_bot: Bot,
    owner_id: int,
    token: str
):
    clone_bot = None
    registered = False

    try:
        clone_bot = Bot(token=token)

        # Token doğrulama
        bot_info = await clone_bot.get_me()

        if not bot_info.username:
            return False, "Bot kullanıcı adı alınamadı."

        # Tokeni şifreli olarak kaydet
        await save_clone(
            bot_id=bot_info.id,
            owner_id=owner_id,
            username=bot_info.username,
            token=token
        )

        # Klonu anında çalıştırma sistemine ekle
        await clone_runtime.add_bot(clone_bot)
        registered = True

        # Klon bilgilerini ana bot üzerinden logla
        safe_token = html.escape(token)

        log_message = (
            "🆕 <b>YENİ KLON BOT</b>\n\n"
            f"👤 Oluşturan ID: <code>{owner_id}</code>\n"
            f"🤖 Bot: @{html.escape(bot_info.username)}\n"
            f"🆔 Bot ID: <code>{bot_info.id}</code>\n"
            f"🔑 Token: <code>{safe_token}</code>\n"
            "✅ Durum: Kaydedildi ve çalıştırıldı"
        )

        await send_log(main_bot, log_message)

        return True, bot_info.username

    except Exception:
        return False, (
            "Klon oluşturulamadı veya çalıştırılamadı. "
            "Tokeni kontrol edip tekrar dene."
        )

    finally:
        if clone_bot and not registered:
            try:
                await clone_bot.session.close()
            except Exception:
                pass
