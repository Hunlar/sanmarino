
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

BOT_NAME = "Sancak Tag Bot"

# Zorunlu kanallar
REQUIRED_CHANNELS = [
    "@sancakmain",
    "@emeklisanalci"
]

# Sabit bağlantılar
SUPPORT_GROUP = "https://t.me/ozturkordusu"
OWNER_USERNAME = "https://t.me/byatillaozturk"

# Ana yönetici
OWNER_ID = 8658946296

# Ortak yönetici listesi
ADMIN_IDS = {
    OWNER_ID
}

# Log grubu
LOG_CHAT_ID = int(
    os.getenv("LOG_CHAT_ID", "-1004404608158")
)

# Veritabanı
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Klon şifreleme anahtarı
CLONE_ENCRYPTION_KEY = os.getenv(
    "CLONE_ENCRYPTION_KEY",
    ""
)

# Etiketleme ayarları
TAG_PAGE_SIZE = 25
TAG_COOLDOWN = 60


def validate_config():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN ayarlanmamış!"
        )
