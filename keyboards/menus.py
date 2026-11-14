
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Beni Gruba Ekle",
                    url="https://t.me/SancakTagBot?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Sancak Main Kanalı",
                    url="https://t.me/sancakmain"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Emekli Sanalci Kanalı",
                    url="https://t.me/emeklisanalci"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Destek Grubu",
                    url="https://t.me/ozturkordusu"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨‍💻 Geliştirici",
                    url="https://t.me/byatillaozturk"
                )
            ]
        ]
    )


def subscription_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Sancak Main",
                    url="https://t.me/sancakmain"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Emekli Sanalci",
                    url="https://t.me/emeklisanalci"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Katıldım, Kontrol Et",
                    callback_data="check_subscription"
                )
            ]
        ]
    )
  
