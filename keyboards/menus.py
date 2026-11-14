
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard(is_admin_user=False):
    rows = [
        [
            InlineKeyboardButton(
                text="👤 Normal Kullanıcı İşlemleri",
                callback_data="menu:users"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 Klon Bot İşlemleri",
                callback_data="menu:clone"
            )
        ]
    ]

    if is_admin_user:
        rows.append([
            InlineKeyboardButton(
                text="🛠 Yönetici Paneli",
                callback_data="menu:admin"
            )
        ])

    rows.extend([
        [
            InlineKeyboardButton(
                text="➕ Beni Gruba Ekle",
                url="https://t.me/SancaklarTagBot?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Destek Grubu",
                url="https://t.me/ozturkordusu"
            ),
            InlineKeyboardButton(
                text="👨‍💻 Geliştirici",
                url="https://t.me/byatillaozturk"
            )
        ]
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def users_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 Komutlar ve Kullanım Rehberi",
                    callback_data="menu:help"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Beni Gruba Ekle",
                    url="https://t.me/SancaklarTagBot?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Ana Menü",
                    callback_data="menu:home"
                )
            ]
        ]
    )


def clone_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🤖 Yeni Klon Oluştur",
                    callback_data="menu:clone_start"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Ana Menü",
                    callback_data="menu:home"
                )
            ]
        ]
    )


def back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Ana Menü",
                    callback_data="menu:home"
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
