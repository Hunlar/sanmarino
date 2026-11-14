
import html

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
    get_bot_stats
)

router = Router()


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
                    text="📢 Duyuru sistemi",
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


async def check_admin(user_id: int) -> bool:
    return await is_admin(user_id)


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.chat.type != "private":
        await message.reply(
            "⚠️ Yönetim panelini kullanmak için bana özelden yaz."
        )
        return

    if not await check_admin(message.from_user.id):
        await message.answer("❌ Bu paneli kullanma yetkin yok.")
        return

    await message.answer(
        "🏴 <b>SANCAK YÖNETİM PANELİ</b>\n\n"
        "Hoş geldin yönetici!\n\n"
        "Aşağıdaki butonlardan yönetim işlemlerini seçebilirsin.",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin:"))
async def admin_callbacks(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        await callback.answer(
            "❌ Yönetici yetkin bulunmuyor.",
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

        text = (
            "📊 <b>SİSTEM İSTATİSTİKLERİ</b>\n\n"
            f"👥 Kayıtlı üye: <b>{stats['users']}</b>\n"
            f"🏘 Kullanılan grup: <b>{stats['groups']}</b>\n"
            f"🤖 Klon bot: <b>{stats['clones']}</b>"
        )

        await callback.message.edit_text(
            text,
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
        await callback.answer(
            "Duyuru sistemi bir sonraki adımda eklenecek.",
            show_alert=True
        )
        return

    await callback.answer()


@router.message(Command("addadmin"))
async def add_admin_command(message: Message):
    if message.chat.type != "private":
        return

    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Yalnızca kurucu yönetici ekleyebilir.")
        return

    parts = (message.text or "").split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "Kullanım: <code>/addadmin 123456789</code>",
            parse_mode="HTML"
        )
        return

    user_id = int(parts[1])

    if await is_admin(user_id):
        await message.answer("ℹ️ Bu kullanıcı zaten yönetici.")
        return

    await add_admin(user_id)

    await message.answer(
        f"✅ <code>{user_id}</code> artık bütün botlarda yöneticidir.",
        parse_mode="HTML"
    )


@router.message(Command("deladmin"))
async def del_admin_command(message: Message):
    if message.chat.type != "private":
        return

    if message.from_user.id != OWNER_ID:
        await message.answer("❌ Yalnızca kurucu yönetici yetki kaldırabilir.")
        return

    parts = (message.text or "").split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer(
            "Kullanım: <code>/deladmin 123456789</code>",
            parse_mode="HTML"
        )
        return

    user_id = int(parts[1])

    if user_id == OWNER_ID:
        await message.answer("❌ Kurucu yöneticinin yetkisi kaldırılamaz.")
        return

    removed = await remove_admin(user_id)

    if removed:
        await message.answer(
            f"✅ <code>{user_id}</code> bütün botlardan yönetici olarak kaldırıldı.",
            parse_mode="HTML"
        )
    else:
        await message.answer("ℹ️ Bu kullanıcı yönetici değildi.")


@router.message(Command("admins"))
async def admins_command(message: Message):
    if message.chat.type != "private":
        return

    if not await check_admin(message.from_user.id):
        await message.answer("❌ Yetkin yok.")
        return

    admin_ids = sorted(await get_admin_ids())

    admin_text = "\n".join(
        f"• <code>{user_id}</code>"
        for user_id in admin_ids
    )

    await message.answer(
        "👮 <b>KALICI YÖNETİCİLER</b>\n\n" + admin_text,
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def stats_command(message: Message):
    if message.chat.type != "private":
        return

    if not await check_admin(message.from_user.id):
        await message.answer("❌ Yetkin yok.")
        return

    stats = await get_bot_stats()

    await message.answer(
        "📊 <b>SİSTEM İSTATİSTİKLERİ</b>\n\n"
        f"👥 Kayıtlı üye: <b>{stats['users']}</b>\n"
        f"🏘 Kullanılan grup: <b>{stats['groups']}</b>\n"
        f"🤖 Klon bot: <b>{stats['clones']}</b>",
        parse_mode="HTML"
  )
  
