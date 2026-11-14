
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from keyboards.menus import (
    start_keyboard,
    subscription_keyboard,
    users_keyboard,
    clone_keyboard,
    back_keyboard
)

from services.subscription import check_subscription
from database.db import is_admin


router = Router()


WELCOME_TEXT = """
🏴 <b>SANCAK TAG BOT</b>

Botumuza hoş geldin!

İşlem yapmak istediğin bölümü aşağıdan seç.
"""


SUBSCRIPTION_TEXT = """
⚠️ <b>ZORUNLU KANAL KATILIMI</b>

Botu kullanabilmek için aşağıdaki iki kanala da katılmalısın.

Katıldıktan sonra kontrol butonuna bas.
"""


USERS_MENU_TEXT = """
👤 <b>NORMAL KULLANICI İŞLEMLERİ</b>

Bu bölümden botun normal kullanım özelliklerine ulaşabilirsin.

📖 Komutları ve kullanım kurallarını öğrenebilir,
botu grubuna ekleyebilirsin.

<b>Yardım:</b> /help
"""


CLONE_MENU_TEXT = """
🤖 <b>KLON BOT İŞLEMLERİ</b>

Kendi Telegram botunu Sancak sistemine ekleyebilirsin.

<b>Klon oluşturma adımları:</b>

1. BotFather üzerinden yeni bir bot oluştur.
2. BotFather'ın verdiği tokeni hazırla.
3. Aşağıdaki klon oluşturma butonuna bas.
4. Tokenini bota gönder.

<b>Komutlar:</b>

/clone — Klon oluşturma işlemini başlatır.
/iptal — Devam eden klon işlemini iptal eder.
"""


HELP_TEXT = """
🏴 <b>SANCAK TAG BOT — YARDIM MENÜSÜ</b>

📌 <b>ETİKETLEME KOMUTLARI</b>

/tag
• Kayıtlı üyeleri isimleriyle etiketler.

/utag
• Kullanıcı adı olan üyeleri etiketler.

/etag
• Üyeleri tıklanabilir 🎯 emojileriyle etiketler.

/ktag
• Eğlenceli duyuruyla grup üyelerini etiketler.

/tagone
• Bir mesaja yanıt vererek yalnızca o kişiyi etiketler.

━━━━━━━━━━━━━━━━━━

🤖 <b>KLON KOMUTLARI</b>

/clone
• Kendi Telegram botunu oluşturmanı sağlar.

/iptal
• Klon oluşturma işlemini iptal eder.

━━━━━━━━━━━━━━━━━━

⚙️ <b>KULLANIM KURALLARI</b>

1. Etiketleme komutlarını yalnızca grup yöneticileri kullanabilir.
2. İki zorunlu kanala da abone olmalısın.
3. Etiketleme işlemleri arasında bekleme süresi vardır.
4. Bot yalnızca karşılaştığı ve kaydettiği üyeleri etiketleyebilir.

━━━━━━━━━━━━━━━━━━

📢 <b>ZORUNLU KANALLAR</b>

• @sancakmain
• @emeklisanalci

💬 <b>DESTEK GRUBU</b>
@ozturkordusu

👨‍💻 <b>GELİŞTİRİCİ</b>
@byatillaozturk

🏴 Sancak Tag Bot — Gücümüz birliğimizden!
"""


async def show_main_menu(message_or_callback):
    user_id = message_or_callback.from_user.id
    admin_status = await is_admin(user_id)

    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(
            WELCOME_TEXT,
            reply_markup=start_keyboard(admin_status),
            parse_mode="HTML"
        )
    else:
        await message_or_callback.answer(
            WELCOME_TEXT,
            reply_markup=start_keyboard(admin_status),
            parse_mode="HTML"
        )


@router.message(CommandStart())
async def start_command(message: Message):
    if not await check_subscription(
        message.bot,
        message.from_user.id
    ):
        await message.answer(
            SUBSCRIPTION_TEXT,
            reply_markup=subscription_keyboard(),
            parse_mode="HTML"
        )
        return

    await show_main_menu(message)


@router.message(Command("help"))
async def help_command(message: Message):
    if not await check_subscription(
        message.bot,
        message.from_user.id
    ):
        await message.answer(
            SUBSCRIPTION_TEXT,
            reply_markup=subscription_keyboard(),
            parse_mode="HTML"
        )
        return

    await message.answer(
        HELP_TEXT,
        reply_markup=back_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
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

    admin_status = await is_admin(callback.from_user.id)

    await callback.message.edit_text(
        WELCOME_TEXT,
        reply_markup=start_keyboard(admin_status),
        parse_mode="HTML"
    )

    await callback.answer("✅ Üyeliğin doğrulandı!")


@router.callback_query(F.data == "menu:home")
async def home_menu_callback(callback: CallbackQuery):
    if not await check_subscription(
        callback.bot,
        callback.from_user.id
    ):
        await callback.answer(
            "Önce zorunlu kanallara katılmalısın.",
            show_alert=True
        )
        return

    await show_main_menu(callback)
    await callback.answer()


@router.callback_query(F.data == "menu:users")
async def users_menu_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        USERS_MENU_TEXT,
        reply_markup=users_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:clone")
async def clone_menu_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        CLONE_MENU_TEXT,
        reply_markup=clone_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu:clone_start")
async def clone_start_callback(callback: CallbackQuery):
    if not await check_subscription(
        callback.bot,
        callback.from_user.id
    ):
        await callback.answer(
            "Önce zorunlu kanallara katılmalısın.",
            show_alert=True
        )
        return

    from handlers.clone import pending_clones

    pending_clones.add(callback.from_user.id)

    await callback.message.answer(
        "🤖 <b>SANCAK KLON SİSTEMİ</b>\n\n"
        "1. BotFather üzerinden yeni bir bot oluştur.\n"
        "2. BotFather'ın verdiği tokeni buraya gönder.\n\n"
        "İptal etmek için /iptal yaz.",
        parse_mode="HTML"
    )

    await callback.answer("Klon oluşturma başlatıldı.")


@router.callback_query(F.data == "menu:help")
async def help_menu_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        HELP_TEXT,
        reply_markup=back_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == "menu:admin")
async def admin_menu_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Yönetici yetkin bulunmuyor.",
            show_alert=True
        )
        return

    from handlers.admin import admin_keyboard

    await callback.message.edit_text(
        "🏴 <b>SANCAK YÖNETİM PANELİ</b>\n\n"
        "Yönetmek istediğin işlemi seç:",
        reply_markup=admin_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()
