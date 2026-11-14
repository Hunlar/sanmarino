
import time
import html
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import TAG_COOLDOWN
from database.db import save_tag_log

from services.tag_service import (
    create_mention,
    create_username_mention,
    create_emoji_mention,
    send_tag_messages,
)

from services.subscription import check_subscription
from services.clone_runtime import clone_runtime
from services.mtproto_service import mtproto_service


router = Router()
last_tag_time = {}

logger = logging.getLogger(__name__)


async def is_group_admin(message: Message) -> bool:

    if message.chat.type not in ("group", "supergroup"):
        await message.reply(
            "❌ Bu komut yalnızca gruplarda kullanılabilir."
        )
        return False

    if not message.from_user:
        return False

    try:
        member = await message.bot.get_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id
        )

        if member.status not in ("administrator", "creator"):
            await message.reply(
                "❌ Bu komutu yalnızca grup yöneticileri kullanabilir."
            )
            return False

        return True

    except Exception:
        logger.exception("Yönetici kontrolü başarısız.")

        await message.reply(
            "⚠️ Yönetici yetkin kontrol edilemedi."
        )

        return False


async def can_tag(message: Message) -> bool:

    if not await is_group_admin(message):
        return False

    check_bot = clone_runtime.main_bot or message.bot

    try:
        subscribed = await check_subscription(
            check_bot,
            message.from_user.id
        )

    except Exception:
        logger.exception("Abonelik kontrolü başarısız.")

        await message.reply(
            "⚠️ Kanal üyeliği kontrol edilirken hata oluştu."
        )

        return False

    if not subscribed:

        bot_info = await message.bot.get_me()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤖 Bota Özelden Start Ver",
                        url=f"https://t.me/{bot_info.username}?start=subscribe"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📢 Birinci Kanal",
                        url="https://t.me/sancakmain"
                    ),
                    InlineKeyboardButton(
                        text="📢 İkinci Kanal",
                        url="https://t.me/emeklisanalci"
                    )
                ]
            ]
        )

        await message.reply(
            "⚠️ <b>ABONELİK GEREKLİ!</b>\n\n"
            "Önce bota özelden /start ver ve zorunlu "
            "kanallarımıza katıl.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        return False

    now = time.time()

    last_time = last_tag_time.get(message.chat.id, 0)

    if now - last_time < TAG_COOLDOWN:

        remaining = int(
            TAG_COOLDOWN - (now - last_time)
        )

        await message.reply(
            f"⏳ Tekrar etiketlemek için {remaining} saniye bekle."
        )

        return False

    return True


def get_custom_text(message: Message) -> str:

    if not message.text:
        return ""

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        return ""

    text = parts[1].strip()

    if text.startswith("-"):
        text = text[1:].strip()

    return text


async def run_tag(message: Message, mode: str):

    if not message.from_user:
        return

    if not await can_tag(message):
        return

    last_tag_time[message.chat.id] = time.time()

    status = await message.reply(
        "🔎 Grup üyeleri kontrol ediliyor..."
    )

    try:

        # Her klon kendi bot tokeniyle üye listesini sorgular.
        members = await mtproto_service.get_group_members(
            message.chat.id,
            bot_token=message.bot.token
        )

        if members is None or not members:

            await status.edit_text(
                "❌ Grup üyeleri alınamadı.\n\n"
                "Bot tokeni, API_ID, API_HASH ve "
                "Telegram erişim izinlerini kontrol et."
            )

            return

        mentions = []

        for user in members:

            user_id = user["user_id"]
            username = user.get("username")
            full_name = user.get("full_name") or "İsimsiz Kullanıcı"

            if mode == "tag":

                mentions.append(
                    create_mention(
                        user_id,
                        full_name
                    )
                )

            elif mode == "utag":

                if username:
                    mentions.append(
                        create_username_mention(username)
                    )

            elif mode == "etag":

                mentions.append(
                    create_emoji_mention(user_id)
                )

        if not mentions:

            await status.edit_text(
                "❌ Etiketlenecek uygun üye bulunamadı."
            )

            return

        # Bütün komutlarda özel mesaj desteği.
        custom_text = get_custom_text(message)

        outgoing_items = list(mentions)

        if custom_text:
            outgoing_items.insert(
                0,
                html.escape(custom_text)
            )

        sent_count = await send_tag_messages(
            message.bot,
            message.chat.id,
            outgoing_items
        )

        await save_tag_log(
            message.from_user.id,
            message.chat.id,
            mode,
            len(mentions)
        )

        await status.edit_text(
            "✅ <b>Etiketleme tamamlandı!</b>\n\n"
            f"👥 Etiketlenen üye: {len(mentions)}\n"
            f"📨 Gönderilen mesaj: {sent_count}\n"
            f"📝 Özel mesaj: {'Var' if custom_text else 'Yok'}",
            parse_mode="HTML"
        )

    except Exception as error:

        logger.exception("Etiketleme başarısız.")

        await status.edit_text(
            "❌ Etiketleme başarısız oldu.\n\n"
            f"Hata: <code>{html.escape(str(error)[:700])}</code>",
            parse_mode="HTML"
        )


@router.message(Command("tag"))
async def tag_command(message: Message):
    await run_tag(message, "tag")


@router.message(Command("utag"))
async def username_tag_command(message: Message):
    await run_tag(message, "utag")


@router.message(Command("etag"))
async def emoji_tag_command(message: Message):
    await run_tag(message, "etag")
            
