
import asyncio
import html
import os
import random
import time

import aiosqlite
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = "users.db"

router = Router()
cooldowns = {}

EMOJIS = [
    "❤️", "🔥", "😂", "👑", "💎",
    "🚀", "🎯", "🌟", "⚡", "🐺"
]

FUNNY_MESSAGES = [
    "📢 Dikkat! Birileri buraya çağrılıyor!",
    "😂 Toplanın, önemli bir olay var!",
    "🚨 Acil toplantı! Kaçış yok!",
    "👑 Kralın çağrısı var!",
    "🔥 Herkes buraya, ortalık karışıyor!",
    "🐺 Kurtlar sofrasına davetlisiniz!"
]


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
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
    if user is None or user.is_bot:
        return

    name = user.full_name or "İsimsiz"

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO members (chat_id, user_id, name, username)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(chat_id, user_id)
            DO UPDATE SET
                name = excluded.name,
                username = excluded.username
        """, (
            chat_id,
            user.id,
            name,
            user.username
        ))
        await db.commit()


async def get_members(chat_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, name, username
            FROM members
            WHERE chat_id = ?
            ORDER BY name
        """, (chat_id,))

        return await cursor.fetchall()


@router.message()
async def track_members(message: Message):
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        await save_member(message.chat.id, message.from_user)


async def check_cooldown(message: Message):
    chat_id = message.chat.id
    now = time.time()

    last_used = cooldowns.get(chat_id, 0)

    if now - last_used < 20:
        remaining = int(20 - (now - last_used)) + 1
        await message.reply(
            f"⏳ Biraz bekle! {remaining} saniye sonra tekrar deneyebilirsin."
        )
        return False

    cooldowns[chat_id] = now
    return True


def make_mention(user_id, name):
    safe_name = html.escape(name)
    return f'<a href="tg://user?id={user_id}">{safe_name}</a>'


def make_emoji_mention(user_id, emoji):
    return f'<a href="tg://user?id={user_id}">{emoji}</a>'


async def send_chunks(message: Message, text: str):
    limit = 3500
    parts = []

    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)

        if split_at == -1:
            split_at = limit

        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    if text:
        parts.append(text)

    for part in parts:
        await message.answer(part)


async def get_group_members(message):
    members = await get_members(message.chat.id)

    if not members:
        await message.reply(
            "Henüz kayıtlı üye bulunamadı. "
            "Üyeler mesaj gönderdikçe kaydedilecek."
        )
        return None

    return members


@router.message(Command("tag"))
async def tag_command(
    message: Message,
    command: CommandObject
):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.reply("Bu komut gruplarda kullanılabilir.")
        return

    if not await check_cooldown(message):
        return

    members = await get_group_members(message)

    if members is None:
        return

    text = html.escape(command.args or "Herkes buraya!")

    mentions = [
        make_mention(user_id, name)
        for user_id, name, username in members
    ]

    result = f"📢 <b>{text}</b>\n\n"
    result += "\n".join(mentions)

    await send_chunks(message, result)


@router.message(Command("utag"))
async def utag_command(
    message: Message,
    command: CommandObject
):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.reply("Bu komut gruplarda kullanılabilir.")
        return

    if not await check_cooldown(message):
        return

    members = await get_group_members(message)

    if members is None:
        return

    usernames = [
        f"@{username}"
        for user_id, name, username in members
        if username
    ]

    if not usernames:
        await message.reply("Kayıtlı üyeler arasında kullanıcı adı bulunamadı.")
        return

    text = html.escape(command.args or "Herkes buraya!")

    result = f"📢 <b>{text}</b>\n\n"
    result += "\n".join(usernames)

    await send_chunks(message, result)


@router.message(Command("etag"))
async def etag_command(
    message: Message,
    command: CommandObject
):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.reply("Bu komut gruplarda kullanılabilir.")
        return

    if not await check_cooldown(message):
        return

    members = await get_group_members(message)

    if members is None:
        return

    result = f"✨ <b>{html.escape(command.args or 'Emojiler konuşsun!')}</b>\n\n"

    for index, (user_id, name, username) in enumerate(members):
        emoji = EMOJIS[index % len(EMOJIS)]
        result += make_emoji_mention(user_id, emoji) + " "

    await message.answer(result)


@router.message(Command("ktag"))
async def ktag_command(message: Message):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.reply("Bu komut gruplarda kullanılabilir.")
        return

    if not await check_cooldown(message):
        return

    members = await get_group_members(message)

    if members is None:
        return

    funny_text = random.choice(FUNNY_MESSAGES)

    result = f"<b>{html.escape(funny_text)}</b>\n\n"

    mentions = [
        make_mention(user_id, name)
        for user_id, name, username in members
    ]

    result += "\n".join(mentions)

    await send_chunks(message, result)


async def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN ayarlanmamış!")

    await init_db()

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()
    dp.include_router(router)

    print("User Tagger Bot çalışıyor!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
