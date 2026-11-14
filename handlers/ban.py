
from html import escape

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.filters.command import CommandObject

from config import OWNER_ID
from database.db import is_admin
from services.ban_service import ban_user, unban_user


router = Router()


async def has_permission(message: Message) -> bool:
    if not message.from_user:
        return False

    return (
        message.from_user.id == OWNER_ID
        or await is_admin(message.from_user.id)
    )


@router.message(Command("ban"))
async def ban_command(
    message: Message,
    command: CommandObject
):
    if not await has_permission(message):
        return await message.answer("⛔ Bu komutu kullanma yetkin yok.")

    if not command.args:
        return await message.answer(
            "Kullanım:\n"
            "/ban KULLANICI_ID Sebep"
        )

    parts = command.args.split(maxsplit=1)

    try:
        user_id = int(parts[0])
    except ValueError:
        return await message.answer("Geçerli bir kullanıcı ID'si gir.")

    if user_id == OWNER_ID:
        return await message.answer("Kurucu hesabı banlanamaz.")

    reason = parts[1] if len(parts) > 1 else "Belirtilmedi"

    try:
        await ban_user(
            user_id=user_id,
            reason=reason,
            banned_by=message.from_user.id
        )

        await message.answer(
            "🚫 <b>Kullanıcı tüm botlardan banlandı.</b>\n\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"📝 Sebep: {escape(reason)}",
            parse_mode="HTML"
        )

    except Exception as error:
        print("Ban işlemi hatası:", type(error).__name__)
        await message.answer("Ban işlemi sırasında hata oluştu.")


@router.message(Command("unban"))
async def unban_command(
    message: Message,
    command: CommandObject
):
    if not await has_permission(message):
        return await message.answer("⛔ Bu komutu kullanma yetkin yok.")

    if not command.args:
        return await message.answer(
            "Kullanım:\n"
            "/unban KULLANICI_ID"
        )

    try:
        user_id = int(command.args.strip())
    except ValueError:
        return await message.answer("Geçerli bir kullanıcı ID'si gir.")

    try:
        removed = await unban_user(user_id)

        if removed:
            await message.answer(
                f"✅ <code>{user_id}</code> kullanıcısının "
                "bütün botlardaki banı kaldırıldı.",
                parse_mode="HTML"
            )
        else:
            await message.answer("Bu kullanıcı zaten banlı değil.")

    except Exception as error:
        print("Unban işlemi hatası:", type(error).__name__)
        await message.answer("Ban kaldırılırken hata oluştu.")
      
