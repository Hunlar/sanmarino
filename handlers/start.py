
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from keyboards.menus import start_keyboard, subscription_keyboard
from services.subscription import check_subscription


router = Router()


WELCOME_TEXT = """
🏴 <b>SANCAK TAG BOT</b>

Botumuza hoş geldin!

Etiketleme ve diğer özellikleri kullanabilmek için
öncelikle zorunlu kanallarımıza katılmalısın.

Destek grubumuz isteğe bağlıdır.

Komutları öğrenmek için /help yazabilirsin.
"""


SUBSCRIPTION_TEXT = """
⚠️ <b>ZORUNLU KANAL KATILIMI</b>

Botu kullanabilmek için aşağıdaki iki kanala da katılmalısın.

Katıldıktan sonra kontrol butonuna bas.
"""


HELP_TEXT = """
🏴 <b>SANCAK TAG BOT — YARDIM MENÜSÜ</b>

📌 <b>ETİKETLEME KOMUTLARI</b>

/tag
• Kayıtlı üyeleri isimleriyle etiketler.

/utag
• Kullanıcı adı olan üyeleri @kullanıcıadı şeklinde etiketler.

/etag
• Üyeleri tıklanabilir 🎯 emojileriyle etiketler.

/ktag
• Eğlenceli duyuruyla grup üyelerini etiketler.

/tagone
• Bir mesaja yanıt vererek yalnızca o kişiyi etiketler.

━━━━━━━━━━━━━━━━━━

🤖 <b>DİĞER KOMUTLAR</b>

/start
• Botu başlatır.

/help
• Yardım menüsünü gösterir.

/clone
• Kendi Telegram botunu oluşturmanı sağlar.

/iptal
• Klon oluşturma işlemini iptal eder.

━━━━━━━━━━━━━━━━━━

⚙️ <b>KULLANIM KURALLARI</b>

1. Etiketleme komutlarını yalnızca grup yöneticileri kullanabilir.
2. İki zorunlu kanala da abone olmalısın.
3. Abone değilsen bota özelden /start vermelisin.
4. Etiketleme işlemleri arasında bekleme süresi vardır.
5. Bot yalnızca karşılaştığı ve kaydettiği üyeleri etiketleyebilir.

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

    await message.answer(
        WELCOME_TEXT,
        reply_markup=start_keyboard(),
        parse_mode="HTML"
    )


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

    await callback.message.edit_text(
        WELCOME_TEXT,
        reply_markup=start_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer(
        "✅ Üyeliğin doğrulandı!"
    )
