
import asyncio
import html
import os
import random
import time

import aiosqlite
import asyncpg

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

CHANNEL = "@emeklisanalci"
CHANNEL_LINK = "https://t.me/emeklisanalci"
SUPPORT_LINK = "https://t.me/ozturkordusu"
OWNER_LINK = "https://t.me/ByAtillaozturk"

PAGE_SIZE = 25
COOLDOWN_SECONDS = 60

EMOJIS = [
    "❤️", "🔥", "😂", "👑", "💎",
    "🚀", "🎯", "🌟", "⚡", "🐺"
]

FUNNY_MESSAGES = [
    "📢 Dikkat! Herkes buraya çağrılıyor!",
    "😂 Toplanın, önemli bir olay var!",
    "🚨 Acil toplantı! Kaçış yok!",
    "👑 Kralın çağrısı var!",
    "🔥 Herkes buraya, ortalık karışıyor!",
    "🐺 Kurtlar sofrasına davetlisiniz!"
]

router = Router()
cooldowns = {}
db_pool = None


# ---------------- DATABASE ----------------

async def init_db():
    global db_pool

    if DATABASE_URL:
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        db_pool = await asyncpg.create_pool(url)

        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    chat_id BIGINT,
                    user_id BIGINT,
                    name TEXT,
                    username TEXT,
                    PRIMARY KEY (chat_id, user_id)
                )
            """)

    else:
        async with aiosqlite.connect("users.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    chat_id INTEGER,
                    user_id INTEGER,
                    name TEXT,
                    username TEXT,
                    PRIMARY KEY (chat_id, user_id)
                )
            """)
            await db.commit()


async def save_member(chat_id, user):
    if not user or user.is_bot:
        return

    name = user.full_name or "İsimsiz"

    if db_pool:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO members (chat_id, user_id, name, username)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (chat_id, user_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    username = EXCLUDED.username
            """, chat_id, user.id, name, user.username)

    else:
        async with aiosqlite.connect("users.db") as db:
            await db.execute("""
                INSERT INTO members (chat_id, user_id, name, username)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(chat_id, user_id)
                DO UPDATE SET
                    name = excluded.name,
                    username = excluded.username
            """, (chat_id, user.id, name, user.username))
            await db.commit()


async def get_members(chat_id, page, username_only=False):
    offset = (page - 1) * PAGE_SIZE

    if db_pool:
        async with db_pool.acquire() as conn:
            if username_only:
                query = """
                    SELECT user_id, name, username
                    FROM members
                    WHERE chat_id = $1 AND username IS NOT NULL
                    ORDER BY user_id
                    LIMIT $2 OFFSET $3
                """
                count_query = """
                    SELECT COUNT(*) FROM members
                    WHERE chat_id = $1 AND username IS NOT NULL
                """
            else:
                query = """
                    SELECT user_id, name, username
                    FROM members
                    WHERE chat_id = $1
                    ORDER BY user_id
                    LIMIT $2 OFFSET $3
                """
                count_query = """
                    SELECT COUNT(*) FROM members WHERE chat_id = $1
                """

            rows = await conn.fetch(query, chat_id, PAGE_SIZE, offset)
            total = await conn.fetchval(count_query, chat_id)
            return rows, total

    async with aiosqlite.connect("users.db") as db:
        if username_only:
            cursor = await db.execute("""
                SELECT user_id, name, username
                FROM members
                WHERE chat_id = ? AND username IS NOT NULL
                ORDER BY user_id
                LIMIT ? OFFSET ?
            """, (chat_id, PAGE_SIZE, offset))

            count_cursor = await db.execute("""
                SELECT COUNT(*) FROM members
                WHERE chat_id = ? AND username IS NOT NULL
            """, (chat_id,))
        else:
            cursor = await db.execute("""
                SELECT user_id, name, username
                FROM members
                WHERE chat_id = ?
                ORDER BY user_id
                LIMIT ? OFFSET ?
            """, (chat_id, PAGE_SIZE, offset))

            count_cursor = await db.execute("""
                SELECT COUNT(*) FROM members WHERE chat_id = ?
            """, (chat_id,))

        rows = await cursor.fetchall()
        total = (await count_cursor.fetchone())[0]
        return rows, total


# ---------------- START MENU ----------------

async def start_keyboard(bot_username, subscribed=False):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Beni Gruba Ekle",
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Destek Grubu",
                url=SUPPORT_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 Kanal",
                url=CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="👑 Bot Sahibi",
                url=OWNER_LINK
            )
        ]
    ]

    if not subscribed:
        buttons.insert(0, [
            InlineKeyboardButton(
                text="✅ Abone Oldum - Kontrol Et",
                callback_data="check_subscription"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as error:
        print("Kanal kontrol hatası:", error)
        return False


async def send_start(message, bot):
    subscribed = await is_subscribed(bot, message.from_user.id)
    me = await bot.get_me()

    if subscribed:
        text = (
            "🤖 <b>User Tagger Bot'a Hoş Geldin!</b>\n\n"
            "Etiketleme komutlarını kullanabilirsin.\n\n"
            "📌 <b>Komutlar:</b>\n"
            "/tag - İsimle etiketle\n"
            "/utag - Kullanıcı adıyla etiketle\n"
            "/etag - Emojilerle etiketle\n"
            "/ktag - Komik etiketleme\n\n"
            "ℹ️ Destek grubuna katılmak isteğe bağlıdır."
        )
    else:
        text = (
            "🤖 <b>User Tagger Bot'a Hoş Geldin!</b>\n\n"
            "Botu kullanabilmek için önce zorunlu kanalımıza "
            "abone olmalısın.\n\n"
            "📢 Kanal: @emeklisanalci\n\n"
            "Abone olduktan sonra aşağıdaki kontrol butonuna bas."
        )

    await message.answer(
        text,
        reply_markup=await start_keyboard(me.username, subscribed)
    )


@router.message(Command("start"))
async def start_command(message: Message, bot: Bot):
    await send_start(message, bot)


@router.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        me = await bot.get_me()

        await callback.message.edit_text(
            "✅ <b>Kanal aboneliğin doğrulandı!</b>\n\n"
            "Artık botu kullanabilirsin.",
            reply_markup=await start_keyboard(me.username, True)
        )
        await callback.answer("Abonelik onaylandı!")
    else:
        await callback.answer(
            "Önce @emeklisanalci kanalına abone olmalısın.",
            show_alert=True
        )


# ---------------- HELPERS ----------------

def parse_page_args(args):
    if not args:
        return 1, ""

    parts = args.split(maxsplit=1)

    if parts[0].isdigit():
        page = max(1, int(parts[0]))
        text = parts[1] if len(parts) > 1 else ""
        return page, text

    return 1, args


def mention(user_id, name):
    return (
        f'<a href="tg://user?id={user_id}">'
        f'{html.escape(name)}</a>'
    )


def emoji_mention(user_id, emoji):
    return f'<a href="tg://user?id={user_id}">{emoji}</a>'


async def send_chunks(message, text):
    while len(text) > 3500:
        split_at = text.rfind("\n", 0, 3500)

        if split_at == -1:
            split_at = 3500

        await message.answer(text[:split_at])
        text = text[split_at:].lstrip()

    if text:
        await message.answer(text)


async def check_access(message, bot):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.reply("Bu komut sadece gruplarda kullanılabilir.")
        return False

    if not await is_subscribed(bot, message.from_user.id):
        await message.reply(
            "⛔ Bu komutu kullanmak için "
            "@emeklisanalci kanalına abone olmalısın."
        )
        return False

    await save_member(message.chat.id, message.from_user)
    return True


async def check_cooldown(message):
    chat_id = message.chat.id
    now = time.time()
    last = cooldowns.get(chat_id, 0)

    if now - last < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last)) + 1
        await message.reply(
            f"⏳ Etiketleme için {remaining} saniye beklemelisin."
        )
        return False

    cooldowns[chat_id] = now
    return True


async def run_tag(message, bot, mode):
    if not await check_access(message, bot):
        return

    page, custom_text = parse_page_args(
        message.text.split(maxsplit=1)[1]
        if len(message.text.split(maxsplit=1)) > 1
        else ""
    )

    username_only = mode == "username"

    rows, total = await get_members(
        message.chat.id,
        page,
        username_only
    )

    if total == 0:
        await message.reply(
            "Henüz kayıtlı üye bulunamadı. "
            "Üyeler mesaj gönderdikçe kaydedilir."
        )
        return

    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

    if page > total_pages:
        await message.reply(
            f"Bu sayfa bulunamadı. Toplam {total_pages} sayfa var."
        )
        return

    if not await check_cooldown(message):
        return

    intro = html.escape(custom_text or "Herkes buraya!")

    result = f"📢 <b>{intro}</b>\n\n"

    for index, row in enumerate(rows):
        user_id = row["user_id"] if db_pool else row[0]
        name = row["name"] if db_pool else row[1]
        username = row["username"] if db_pool else row[2]

        if mode == "username":
            result += f"@{username}\n"
        elif mode == "emoji":
            result += emoji_mention(
                user_id,
                EMOJIS[index % len(EMOJIS)]
            ) + " "
        else:
            result += mention(user_id, name) + "\n"

    result += (
        f"\n\n📄 Sayfa: {page}/{total_pages}"
        f"\n👥 Kayıtlı üye: {total}"
        f"\n➡️ Sonraki sayfa için: /{mode_command(mode)} {page + 1}"
    )

    await send_chunks(message, result)


def mode_command(mode):
    return {
        "name": "tag",
        "username": "utag",
        "emoji": "etag"
    }.get(mode, "tag")


# ---------------- TAG COMMANDS ----------------

@router.message(Command("tag"))
async def tag_command(message: Message, bot: Bot):
    await run_tag(message, bot, "name")


@router.message(Command("utag"))
async def utag_command(message: Message, bot: Bot):
    await run_tag(message, bot, "username")


@router.message(Command("etag"))
async def etag_command(message: Message, bot: Bot):
    await run_tag(message, bot, "emoji")


@router.message(Command("ktag"))
async def ktag_command(message: Message, bot: Bot):
    if not await check_access(message, bot):
        return

    if not await check_cooldown(message):
        return

    funny = random.choice(FUNNY_MESSAGES)
    await message.answer(
        f"<b>{html.escape(funny)}</b>\n\n"
        "Etiketleme için /tag komutunu kullanabilirsin."
    )


# ---------------- MEMBER TRACKING ----------------

@router.message()
async def track_members(message: Message):
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        await save_member(message.chat.id, message.from_user)


# ---------------- MAIN ----------------

async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN ayarlanmamış!")

    await init_db()

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(router)

    print("User Tagger Bot başlatıldı!")

    try:
        await dp.start_polling(bot)
    finally:
        if db_pool:
            await db_pool.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
