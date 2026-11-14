
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keyboards.menus import start_keyboard, subscription_keyboard
from services.subscription import check_subscription


router = Router()


WELCOME_TEXT = """
🏴 **SANCAK TAG BOT**

Botumuza hoş geldin!

Etiketleme ve diğer özellikleri kullanabilmek için
öncelikle zorunlu kanallarımıza katılmalısın.

Destek grubumuz isteğe bağlıdır.
"""


SUBSCRIPTION_TEXT = """
⚠️ **ZORUNLU KANAL KATILIMI**

Botu kullanabilmek için aşağıdaki iki kanala da katılmalısın.

Katıldıktan sonra kontrol butonuna bas.
"""


@router.message(CommandStart())
async def start_command(message: Message):
    if not await check_subscription(
        message.bot,
        message.from_user.id
    ):
        await message.answer(
            SUBSCRIPTION_TEXT,
            reply_markup=subscription_keyboard(),
            parse_mode="Markdown"
        )
        return

    await message.answer(
        WELCOME_TEXT,
        reply_markup=start_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "check_subscription")
async def subscription_callback(callback: CallbackQuery):
    is_member = await check_subscription(
        callback.bot,
        callback.from_user.id
    )

    if not is_member:
        await callback.answer(
            "❌ İki kanala da katılmalısın!",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        WELCOME_TEXT,
        reply_markup=start_keyboard(),
        parse_mode="Markdown"
    )

    await callback.answer(
        "✅ Üyeliğin doğrulandı!"
  )
  
