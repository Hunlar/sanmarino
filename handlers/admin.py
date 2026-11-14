
import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import OWNER_ID
from database.db import (
    is_admin,
    add_admin,
    remove_admin,
    get_admin_ids,
    get_bot_stats,
    get_bot_groups
)
from services.clone_runtime import clone_runtime

router = Router()

pending_broadcasts = {}


def admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 İstatistikler",
                    callback_data="admin:stats"
                ),
                InlineKeyboardButton(
                    text="👮 Yöneticiler",
                    callback_data="admin:admins"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Duyuru gönder",
                    callback_data="admin:broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Paneli kapat",
                    callback_data="admin:close"
                )
            ]
        ]
    )


def broadcast_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Gönder",
                    callback_data="broadcast:confirm"
                ),
                InlineKeyboardButton(
                    text="❌ İptal",
                    callback_data="broadcast:cancel"
                )
            ]
        ]
    )


async def start_broadcast(user_id, message):
    pending_broadcasts[user_id] = message

    await message.answer(
        "📢 <b>DUYURU ÖNİZLEMESİ</b>\n\n"
        f"{message.text}\n\n"
        "Bu duyuruyu kayıtlı gruplara göndermek istiyor musun?",
        reply_markup=broadcast_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.chat.type != "private":
        await message.reply(
            "Yönetim paneli için bana özelden /admin yaz."
        )
        return

    if not await is_admin(message.from_user.id):
        await message.answer("❌ Yönetici yetkin bulunmuyor.")
        return

    await message.answer(
        "🏴 <b>SANCAK YÖNETİM PANELİ</b>\n\n"
        "Yönetmek istediğin işlemi seç:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin:"))
async def admin_callbacks(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "Yönetici yetkin bulunmuyor.",
            show_alert=True
        )
        return

    action = callback.data.split(":", 1)[1]

    if action == "close":
        await callback.message.delete()
        await callback.answer("Panel kapatıldı.")
        return

    if action == "stats":
        stats = await get_bot_stats()

        await callback.message.edit_text(
            "📊 <b>SİSTEM İSTATİSTİKLERİ</b>\n\n"
            f"👥 Kayıtlı kullanıcı: <b>{stats['users']}</b>\n"
            f"🏘 Kayıtlı grup: <b>{stats['groups']}</b>\n"
            f"🤖 Klon bot: <b>{stats['clones']}</b>",
            reply_markup=admin_keyboard(),
            parse_mode="HTML"
        )

    elif action == "admins":
        admin_ids = sorted(await get_admin_ids())
        admin_text = "\n".join(
            f"• <code>{user_id}</code>"
            for user_id in admin_ids
        )

        await callback.message.edit_text(
            "👮 <b>KALICI YÖNETİCİLER</b>\n\n"
            f"{admin_text}",
            reply_markup=admin_keyboard(),
            parse_mode="HTML"
        )

    elif action == "broadcast":
        await callback.message.answer(
            "📢 Göndermek istediğin duyuru metnini yaz.\n\n"
            "İptal etmek için /iptal yaz."
        )
        pending_broadcasts[callback.from_user.id] = None

    await callback.answer()


@router.message(Command("addadmin"))
async def add_admin_command(message: Message):
    if message.chat.type != "private":
        return

    if message.from_user.id != OWNER_ID:
        await message.answer(
            "❌ Yalnızca kurucu yönetici yetki verebilir."
        )
        return

    parts = (message.text or "").split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "Kullanım: /addadmin 123456789"
        )
        return

    user_id = int(parts[1])

    if await is_admin(user_id):
        await message.answer("Bu kullanıcı zaten yönetici.")
        return

    await add_admin(user_id)

    await message.answer(
        f"✅ {user_id} bütün botlarda yönetici oldu."
    )


@router.message(Command("deladmin"))
async def del_admin_command(message: Message):
    if message.chat.type != "private":
        return

    if message.from_user.id != OWNER_ID:
        await message.answer(
            "❌ Yalnızca kurucu yönetici yetki kaldırabilir."
        )
        return

    parts = (message.text or "").split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "Kullanım: /deladmin 123456789"
        )
        return

    user_id = int(parts[1])

    if user_id == OWNER_ID:
        await message.answer(
            "❌ Kurucunun yetkisi kaldırılamaz."
        )
        return

    removed = await remove_admin(user_id)

    if removed:
        await message.answer(
            f"✅ {user_id} bütün botlardan yönetici olarak kaldırıldı."
        )
    else:
        await message.answer("Bu kullanıcı yönetici değildi.")


@router.message(Command("admins"))
async def admins_command(message: Message):
    if message.chat.type != "private":
        return

    if not await is_admin(message.from_user.id):
        await message.answer("❌ Yetkin bulunmuyor.")
        return

    admin_ids = sorted(await get_admin_ids())

    admin_text = "\n".join(
        f"• <code>{user_id}</code>"
        for user_id in admin_ids
    )

    await message.answer(
        "👮 <b>YÖNETİCİLER</b>\n\n" + admin_text,
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def stats_command(message: Message):
    if message.chat.type != "private":
        return

    if not await is_admin(message.from_user.id):
        await message.answer("❌ Yetkin bulunmuyor.")
        return

    stats = await get_bot_stats()

    await message.answer(
        "📊 <b>SİSTEM İSTATİSTİKLERİ</b>\n\n"
        f"👥 Kayıtlı kullanıcı: <b>{stats['users']}</b>\n"
        f"🏘 Kayıtlı grup: <b>{stats['groups']}</b>\n"
        f"🤖 Klon bot: <b>{stats['clones']}</b>",
        parse_mode="HTML"
    )


@router.message(Command("broadcast"))
async def broadcast_command(message: Message):
    if message.chat.type != "private":
        return

    if not await is_admin(message.from_user.id):
        await message.answer("❌ Yetkin bulunmuyor.")
        return

    await message.answer(
        "📢 Göndermek istediğin duyuru metnini yaz.\n\n"
        "İptal etmek için /iptal yaz."
    )

    pending_broadcasts[message.from_user.id] = None


@router.message(Command("iptal"))
async def cancel_broadcast(message: Message):
    user_id = message.from_user.id

    if user_id in pending_broadcasts:
        pending_broadcasts.pop(user_id, None)
        await message.answer("❌ Duyuru işlemi iptal edildi.")


@router.message(
    F.chat.type == "private",
    F.text,
    ~F.text.startswith("/")
)
async def receive_broadcast_text(message: Message):
    user_id = message.from_user.id

    if user_id not in pending_broadcasts:
        return

    if not await is_admin(user_id):
        pending_broadcasts.pop(user_id, None)
        return

    text = message.text.strip()

    if not text:
        await message.answer("Duyuru metni boş olamaz.")
        return

    pending_broadcasts[user_id] = text

    preview = text[:3500]

    await message.answer(
        "📢 <b>DUYURU ÖNİZLEMESİ</b>\n\n"
        f"{preview}\n\n"
        "Göndermek istediğinden emin misin?",
        reply_markup=broadcast_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("broadcast:"))
async def broadcast_callbacks(callback: CallbackQuery):
    user_id = callback.from_user.id

    if not await is_admin(user_id):
        await callback.answer(
            "Yetkin bulunmuyor.",
            show_alert=True
        )
        return

    action = callback.data.split(":", 1)[1]

    if action == "cancel":
        pending_broadcasts.pop(user_id, None)
        await callback.message.edit_text(
            "❌ Duyuru iptal edildi."
        )
        await callback.answer()
        return

    text = pending_broadcasts.get(user_id)

    if not isinstance(text, str) or not text.strip():
        await callback.answer(
            "Önce duyuru metni yazmalısın.",
            show_alert=True
        )
        return

    pending_broadcasts.pop(user_id, None)

    await callback.message.edit_text(
        "⏳ Duyuru gönderiliyor..."
    )
    await callback.answer()

    sent = 0
    failed = 0
    processed_groups = set()

    # Her botun kayıtlı gruplarına kendi botuyla gönder
    for bot_id, bot in list(clone_runtime.bots.items()):
        try:
            group_ids = await get_bot_groups(bot_id)
        except Exception:
            continue

        for group_id in group_ids:
            if group_id in processed_groups:
                continue

            processed_groups.add(group_id)

            try:
                await bot.send_message(
                    chat_id=group_id,
                    text=text
                )
                sent += 1

            except Exception:
                failed += 1

            await asyncio.sleep(0.05)

    await callback.message.answer(
        "📢 <b>DUYURU TAMAMLANDI</b>\n\n"
        f"✅ Başarılı: <b>{sent}</b>\n"
        f"❌ Başarısız: <b>{failed}</b>\n"
        f"📦 Denenen grup: <b>{len(processed_groups)}</b>",
        parse_mode="HTML"
    )
