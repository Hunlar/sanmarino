
import time
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import TAG_COOLDOWN
from database.db import get_members, save_tag_log
from services.tag_service import (
    create_mention,
    create_username_mention,
    create_emoji_mention,
    send_tag_messages,
)
from services.subscription import check_subscription
from services.clone_runtime import clone_runtime


router = Router()
last_tag_time = {}
logger = logging.getLogger(__name__)


async def is_group_admin(message: Message) -> bool:
    if message.chat.type not in ("group", "supergroup"):
        await message.reply("❌ Bu komut yalnızca gruplarda kullanılabilir.")
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
            "⚠️ Yönetici yetkin kontrol edilemedi. Botun yetkilerini kontrol et."
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
            "Önce bota özelden /start ver ve iki zorunlu "
            "kanalımıza katıl. Ardından komutu tekrar kullan.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return False

    now = time.time()
    last_time_value = last_tag_time.get(message.chat.id, 0)

    if now - last_time_value < TAG_COOLDOWN:
        remaining = int(TAG_COOLDOWN - (now - last_time_value))
        await message.reply(
            f"⏳ Tekrar etiketleme için {remaining} saniye beklemelisin."
        )
        return False

    return True


async def run_tag(message: Message, mode: str):
    print(
        "TAG COMMAND HANDLER CALISTI:",
        mode,
        repr(message.text),
        "BOT ID:",
        message.bot.id
    )

    if not message.from_user:
        return

    if not await can_tag(message):
        return

    last_tag_time[message.chat.id] = time.time()

    try:
        members = await get_members(message.chat.id)

        if not members:
            await message.reply(
                "❌ Henüz kayıtlı üye bulunamadı. "
                "Bot üyeleri mesajlardan tanıdıkça kaydedecek."
            )
            return

        mentions = []

        for user in members:
            user_id = user["user_id"]
            username = user["username"]
            full_name = user["full_name"]

            if mode == "tag":
                mentions.append(create_mention(user_id, full_name))

            elif mode == "utag" and username:
                mentions.append(create_username_mention(username))

            elif mode == "etag":
                mentions.append(create_emoji_mention(user_id))

        if not mentions:
            await message.reply(
                "❌ Etiketlenecek uygun üye bulunamadı."
            )
            return

        sent_count = await send_tag_messages(
            message.bot,
            message.chat.id,
            mentions
        )

        await save_tag_log(
            message.from_user.id,
            message.chat.id,
            mode,
            len(mentions)
        )

        await message.reply(
            f"✅ Etiketleme tamamlandı.\n"
            f"Etiketlenen kayıt: {len(mentions)}\n"
            f"Gönderilen mesaj: {sent_count}"
        )

    except Exception:
        logger.exception("Etiketleme işlemi başarısız.")
        await message.reply(
            "❌ Etiketleme sırasında hata oluştu. Heroku loglarını kontrol et."
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
