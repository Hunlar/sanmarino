
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.clone_service import create_clone
from services.subscription import check_subscription

router = Router()

pending_clones = set()


@router.message(Command("clone"))
async def clone_command(message: Message):
    if message.chat.type != "private":
        await message.reply(
            "⚠️ Klon oluşturmak için botuma özel mesajdan /clone yaz."
        )
        return

    if not message.from_user:
        return

    if not await check_subscription(
        message.bot,
        message.from_user.id
    ):
        from keyboards.menus import subscription_keyboard

        await message.answer(
            "❌ Önce iki zorunlu kanalımıza katılmalısın.",
            reply_markup=subscription_keyboard()
        )
        return

    pending_clones.add(message.from_user.id)

    await message.answer(
        "🤖 <b>SANCAK KLON SİSTEMİ</b>\n\n"
        "1. BotFather üzerinden yeni bir bot oluştur.\n"
        "2. BotFather'ın verdiği tokeni buraya gönder.\n\n"
        "Kızıl Sancak Dev saygı ile sunar.",
        parse_mode="HTML"
    )


@router.message(Command("iptal"))
async def cancel_clone(message: Message):
    if message.from_user:
        pending_clones.discard(message.from_user.id)

    await message.answer(
        "❌ Klon oluşturma işlemi iptal edildi."
    )


@router.message(
    lambda message: (
        message.chat.type == "private"
        and message.from_user is not None
        and message.from_user.id in pending_clones
    )
)
async def receive_clone_token(message: Message):
    user_id = message.from_user.id
    token = (message.text or "").strip()

    if not token or ":" not in token:
        await message.answer(
            "❌ Geçerli bir bot tokeni gönder."
        )
        return

    try:
        await message.delete()
    except Exception:
        pass

    pending_clones.discard(user_id)

    status_message = await message.answer(
        "⏳ Token kontrol ediliyor, lütfen bekle..."
    )

    success, result = await create_clone(
        main_bot=message.bot,
        owner_id=user_id,
        token=token
    )

    if success:
        await status_message.edit_text(
            f"✅ <b>Klon başarıyla kaydedildi!</b>\n\n"
            f"🤖 Bot: @{result}\n\n"
            "Klon bilgileri sisteme kaydedildi. "
            "Çalıştırma işlemi ayrıca yapılacaktır.",
            parse_mode="HTML"
        )
    else:
        await status_message.edit_text(
            f"❌ Klon oluşturulamadı.\n\n{result}"
        )
        
