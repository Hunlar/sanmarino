
import random
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import get_members, save_tag_log
from services.tag_service import (
    create_mention,
    send_tag_messages,
)
from handlers.tags import can_tag


router = Router()
logger = logging.getLogger(__name__)


FUNNY_MESSAGES = [
    "🚨 SANCAK ALARMI! Herkes buraya toplansın!",
    "😂 Yoklama var! Kaçan olursa tek tek bulacağız!",
    "🔥 Sancak meydanında toplanıyoruz!",
    "📢 Duyduk duymadık demeyin! Herkes buraya!",
    "😎 Reis çağırıyor, kimse kaybolmasın!",
    "🐺 Kurtlar sofrasına herkes davetli!",
    "🚔 Telegram polisi geldi! Herkes meydana!",
    "🫡 Komutan çağırıyor! Görmezden gelenin vay hâline!",
    "🍿 Dedikodu toplantısı başladı, geç kalan patlamış mısır getirsin!",
    "🐢 Kaplumbağa hızında gelenler de buyursun!",
    "📣 Hoparlörleri açın! Mahalle toplantısı var!",
    "😂 Sessizler de konuşsun, bugün kaçış yok!",
    "🧹 Grup temizliği değil, toplu yoklama yapıyoruz!",
    "🥷 Görünmezlik pelerinini çıkarıp meydana gelin!",
    "🛎️ Kapı kapı dolaşmadan herkesi buraya çağırıyoruz!",
    "🐸 Kurbağa bile zıplayıp geldi, siz hâlâ yoksunuz!",
    "🧠 Beyin fırtınası değil, kafa karışıklığı toplantısı!",
    "🍕 Pizza dağıtılmıyor ama yine de gelin!",
    "🚀 Herkes çevrimiçi olsun, uzaya çıkıyoruz!",
    "🦁 Aslanlar meydana, kediler de peşlerinden!",
    "🎤 Mikrofon açık! Şarkı söylemek zorunlu değil!",
    "🧨 Patırtı başladı, herkes yerini alsın!",
    "🕵️ Kaybolan üyeler aranıyor! Son görüldükleri yer burası!",
    "🛒 Alışveriş listesi değil, insan listesi açıldı!",
    "🐔 Tavuklar bile kümeste toplandı, siz nerdesiniz?",
    "🧊 Soğuk yapanlar çözülsün, toplantı başladı!",
    "🎪 Sirk açıldı! Palyaçolar ve seyirciler meydana!",
    "📡 Sinyal alınamayan üyeler, lütfen antenlerini düzeltsin!",
    "🦖 Dinozorlar bile uyandı, grup hâlâ sessiz!",
    "🥳 Bugün bahane kabul edilmiyor, herkes meydana!",
    "🧙 Büyü yapıldı! Herkes buraya ışınlanıyor!",
    "🛸 Uzaylılar geldi, grupta kimseyi bulamadılar!",
    "🐧 Penguen yürüyüşü başladı, sıraya geçin!",
    "🧦 Çoraplarını bulanlar meydana gelsin!",
    "🎯 Hedef belli: Herkesi buraya toplamak!",
    "🪑 Sandalyeleri çekin, toplantı başlıyor!",
    "🥸 Sahte kimlik kullananlar da yoklamaya katılsın!",
    "🐒 Maymunlar bile sakin, biraz hareketlenelim!",
    "📚 Bugünkü ders: Kaybolmadan grupta durabilmek!",
    "🍉 Karpuz kesildi, gelmeyene kabuk kalacak!",
    "🧯 Yangın yok ama grup fena sessiz!",
    "🦆 Ördekler sıraya girdi, insanlar nerede?",
    "🎮 Oyun durduruldu! Herkes meydana!",
    "🧹 Toz tutmuş grup, biraz hareket lazım!",
    "🧛 Gece vardiyası uyansın! Yoklama vakti!",
    "🧟 Zombiler bile mesaj attı, siz hâlâ susuyorsunuz!",
    "🐻 Ayılar kış uykusundan kalktı, siz de kalkın!",
    "🚜 Sessizlik tarlasını sürmeye geldik!",
    "🪄 Abrakadabra! Herkes burada belirsin!",
    "🥁 Davullar çalsın! Sancak toplantısı başlıyor!",
    "🧃 Meyve suyu hazır, üyeler eksik!",
    "🦀 Yengeç yürüyüşüyle de olsa meydana gelin!",
    "📢 Anons anons! Kayıp üyeler, evinize dönün!",
    "🕺 Dans etmeyen kalmasın, müzik kafamızda!",
    "🧸 Oyuncaklar bile toplandı, siz nerdesiniz?",
    "🧻 Tuvalet molası verenler hariç herkes gelsin!",
    "🐝 Arılar çalışıyor, grup üyeleri kayıp!",
    "🧀 Peynir kokusuna gelen fareler bile burada!",
    "🚀 Kalkışa 10 saniye! Grubun mürettebatı nerede?",
    "👀 Okuyup kaçanlar, sizi de gördük!",
]


@router.message(Command("ktag"))
async def funny_tag_command(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        await message.reply(
            "❌ Bu komut yalnızca gruplarda kullanılabilir."
        )
        return

    if not message.from_user:
        return

    if not await can_tag(message):
        return

    try:
        members = await get_members(message.chat.id)

        if not members:
            await message.reply(
                "❌ Henüz kayıtlı üye bulunamadı."
            )
            return

        mentions = []

        for user in members:
            if user["user_id"] == message.from_user.id:
                continue

            mentions.append(
                create_mention(
                    user["user_id"],
                    user["full_name"]
                )
            )

        if not mentions:
            await message.reply(
                "❌ Etiketlenecek başka üye bulunamadı."
            )
            return

        await message.answer(
            random.choice(FUNNY_MESSAGES)
        )

        sent_count = await send_tag_messages(
            message.bot,
            message.chat.id,
            mentions
        )

        await save_tag_log(
            message.from_user.id,
            message.chat.id,
            "ktag",
            len(mentions)
        )

        await message.reply(
            f"😂 Ktag tamamlandı!\n"
            f"Etiketlenen kayıt: {len(mentions)}\n"
            f"Gönderilen etiket mesajı: {sent_count}"
        )

    except Exception:
        logger.exception("Ktag işlemi başarısız.")
        await message.reply(
            "❌ Ktag sırasında bir hata oluştu. "
            "Heroku loglarını kontrol et."
        )
