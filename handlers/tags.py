
import time
import logging
import random
import asyncio

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
    send_tag_messages,
)

from services.subscription import check_subscription
from services.clone_runtime import clone_runtime
from services.mtproto_service import mtproto_service


router = Router()
last_tag_time = {}
active_tag_stops = {}

logger = logging.getLogger(__name__)


ETAG_EMOJIS = [
    "🔥", "⚡", "🎯", "💥", "🚀",
    "👑", "🐺", "🦅", "💎", "🌟",
    "🎭", "🛡️", "⚔️", "🔱", "🌪️",
    "🍀", "🎲", "🦁", "🐉", "✨",
]


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
        logger.exception("Grup yöneticisi kontrolü başarısız.")

        await message.reply(
            "⚠️ Yönetici yetkin kontrol edilemedi. "
            "Botun yetkilerini kontrol et."
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
                        url=(
                            f"https://t.me/"
                            f"{bot_info.username}?start=subscribe"
                        )
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
            "Önce bota özelden /start ver ve iki zorunlu "
            "kanalımıza katıl. Ardından komutu tekrar kullan.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        return False

    now = time.time()

    last_time_value = last_tag_time.get(
        message.chat.id,
        0
    )

    if now - last_time_value < TAG_COOLDOWN:

        remaining = int(
            TAG_COOLDOWN - (now - last_time_value)
        )

        await message.reply(
            f"⏳ Tekrar etiketlemek için "
            f"{remaining} saniye beklemelisin."
        )

        return False

    return True


def get_custom_text(message: Message) -> str:

    if not message.text:
        return ""

    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        return ""

    command_text = parts[1].strip()

    if command_text.startswith("-"):
        command_text = command_text[1:].strip()

    return command_text


async def run_tag(message: Message, mode: str):

    if not message.from_user:
        return

    if not await can_tag(message):
        return

    chat_id = message.chat.id
    custom_text = get_custom_text(message)

    if chat_id in active_tag_stops:
        await message.reply(
            "⚠️ Bu grupta zaten bir etiketleme işlemi devam ediyor."
        )
        return

    stop_event = asyncio.Event()
    active_tag_stops[chat_id] = stop_event

    status = await message.reply(
        "🔎 <b>Grup üyeleri alınıyor...</b>",
        parse_mode="HTML"
    )

    try:

        members = await mtproto_service.get_group_members(
            message.chat.id,
            bot_token=message.bot.token
        )

        if stop_event.is_set():
            await status.edit_text(
                "⏹ Etiketleme durduruldu."
            )
            return

        if members is None:
            await status.edit_text(
                "❌ Grup üyeleri alınamadı.\n\n"
                "API_ID, API_HASH ve BOT_TOKEN ayarlarını "
                "kontrol et."
            )
            return

        if not members:
            await status.edit_text(
                "❌ Etiketlenecek üye bulunamadı."
            )
            return

        mentions = []
        seen_ids = set()

        emoji_pool = ETAG_EMOJIS.copy()
        random.shuffle(emoji_pool)

        for user in members:

            user_id = user.get("user_id")

            if not user_id or user_id in seen_ids:
                continue

            seen_ids.add(user_id)

            username = user.get("username")
            full_name = (
                user.get("full_name")
                or "İsimsiz Kullanıcı"
            )

            if mode == "tag":
                mentions.append(
                    create_mention(user_id, full_name)
                )

            elif mode == "utag":
                if username:
                    mentions.append(
                        create_username_mention(username)
                    )

            elif mode == "etag":

                if not emoji_pool:
                    emoji_pool = ETAG_EMOJIS.copy()
                    random.shuffle(emoji_pool)

                emoji = emoji_pool.pop()

                mentions.append(
                    f'<a href="tg://user?id={user_id}">'
                    f'{emoji}</a>'
                )

        if stop_event.is_set():
            await status.edit_text(
                "⏹ Etiketleme durduruldu."
            )
            return

        if not mentions:
            await status.edit_text(
                "❌ Bu etiketleme türü için uygun üye bulunamadı."
            )
            return

        sent_count = await send_tag_messages(
            message.bot,
            message.chat.id,
            mentions,
            prefix=custom_text,
            stop_event=stop_event
        )

        await save_tag_log(
            message.from_user.id,
            message.chat.id,
            mode,
            len(mentions)
        )

        last_tag_time[chat_id] = time.time()

        if stop_event.is_set():
            await status.edit_text(
                "⏹ <b>Etiketleme durduruldu!</b>\n\n"
                f"📨 Gönderilen mesaj: {sent_count}\n"
                f"👥 Planlanan etiket: {len(mentions)}",
                parse_mode="HTML"
            )
        else:
            await status.edit_text(
                "✅ <b>Etiketleme tamamlandı!</b>\n\n"
                f"👥 Etiketlenen üye: {len(mentions)}\n"
                f"📨 Gönderilen mesaj: {sent_count}\n"
                f"📝 Özel mesaj: "
                f"{'Var' if custom_text else 'Yok'}",
                parse_mode="HTML"
            )

    except Exception as error:

        logger.exception(
            "Etiketleme işlemi başarısız."
        )

        await status.edit_text(
            "❌ <b>Etiketleme başarısız oldu.</b>\n\n"
            f"Hata: <code>{str(error)[:700]}</code>",
            parse_mode="HTML"
        )

    finally:
        if active_tag_stops.get(chat_id) is stop_event:
            active_tag_stops.pop(chat_id, None)


@router.message(Command("tag"))
async def tag_command(message: Message):
    await run_tag(message, "tag")


@router.message(Command("utag"))
async def username_tag_command(message: Message):
    await run_tag(message, "utag")


@router.message(Command("etag"))
async def emoji_tag_command(message: Message):
    await run_tag(message, "etag")


@router.message(Command("stop"))
async def stop_tag_command(message: Message):

    if not await is_group_admin(message):
        return

    stop_event = active_tag_stops.get(message.chat.id)

    if not stop_event:
        await message.reply(
            "ℹ️ Bu grupta devam eden bir etiketleme yok."
        )
        return

    stop_event.set()

    await message.reply(
        "⏹ Etiketleme durdurma isteği alındı. "
        "Devam eden gönderim tamamlanınca işlem duracak."
        )
            
