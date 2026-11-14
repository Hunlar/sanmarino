
import os

# Ana bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_NAME = "Sancak Tag Bot"

# Zorunlu katılım kanalları
REQUIRED_CHANNELS = [
    "@sancakmain",
    "@emeklisanalci",
]

# İsteğe bağlı destek grubu
SUPPORT_GROUP = "https://t.me/ozturkordusu"

# Geliştirici
OWNER_USERNAME = "https://t.me/byatillaozturk"

# Log grubu
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "-1004404608158"))

# Veritabanı
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Klon bot şifreleme anahtarı
CLONE_ENCRYPTION_KEY = os.getenv("CLONE_ENCRYPTION_KEY", "")

# Etiketleme ayarları
TAG_PAGE_SIZE = 25
TAG_COOLDOWN = 60


def validate_config():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN ayarlanmamış!")
      
