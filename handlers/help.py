
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


HELP_TEXT = """
🏴 <b>SANCAK TAG BOT — YARDIM MENÜSÜ</b>

Botumuz grup içerisinde üyeleri etiketlemenizi sağlar.

━━━━━━━━━━━━━━━━━━

📌 <b>ETİKETLEME KOMUTLARI</b>

/tag
• Kayıtlı üyeleri isimleriyle etiketler.

/utag
• Kullanıcı adı bulunan üyeleri @kullanıcıadı şeklinde etiketler.

/etag
• Üyeleri tıklanabilir 🎯 emojileriyle etiketler.

/ktag
• Eğlenceli bir duyuruyla grup üyelerini etiketler.

/tagone
• Bir kişinin mesajına yanıt vererek yalnızca o kişiyi etiketler.

━━━━━━━━━━━━━━━━━━

🤖 <b>DİĞER KOMUTLAR</b>

/start
• Botu başlatır ve gerekli kanal aboneliklerini kontrol eder.

/help
• Bu yardım menüsünü gösterir.

/clone
• Kendi Telegram botunu oluşturup Sancak Tag Bot özelliklerini kullanmanı sağlar.

/iptal
• Devam eden klon oluşturma işlemini iptal eder.

━━━━━━━━━━━━━━━━━━

⚙️ <b>KULLANIM KURALLARI</b>

1. Etiketleme komutlarını yalnızca grup yöneticileri kullanabilir.
2. Botu kullanmak için iki zorunlu kanala da abone olmalısınız.
3. Abone değilseniz önce bota özelden /start vermelisiniz.
4. Etiketleme işlemleri arasında bekleme süresi vardır.
5. Bot, grupta karşılaştığı üyeleri kaydeder. Daha önce hiç karşılaşmadığı üyeleri otomatik olarak bulamaz.

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


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        HELP_TEXT,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
  
