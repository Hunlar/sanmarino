
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from typing import Any, Callable, Dict, Awaitable

import database.db as db


async def init_ban_db():
    if db.pool is None:
        raise RuntimeError("Veritabanı başlatılmamış!")

    async with db.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS banned_users (
                user_id BIGINT PRIMARY KEY,
                reason TEXT DEFAULT 'Belirtilmedi',
                banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                banned_by BIGINT
            )
        """)


async def ban_user(user_id: int, reason: str, banned_by: int):
    if db.pool is None:
        raise RuntimeError("Veritabanı başlatılmamış!")

    async with db.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO banned_users (user_id, reason, banned_by)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id)
            DO UPDATE SET
                reason = EXCLUDED.reason,
                banned_by = EXCLUDED.banned_by,
                banned_at = CURRENT_TIMESTAMP
        """, user_id, reason, banned_by)


async def unban_user(user_id: int):
    if db.pool is None:
        raise RuntimeError("Veritabanı başlatılmamış!")

    async with db.pool.acquire() as conn:
        result = await conn.execute("""
            DELETE FROM banned_users
            WHERE user_id = $1
        """, user_id)

    return result.endswith("1")


async def is_banned(user_id: int):
    if db.pool is None:
        return None

    async with db.pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT user_id, reason
            FROM banned_users
            WHERE user_id = $1
        """, user_id)


class GlobalBanMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[
            [TelegramObject, Dict[str, Any]],
            Awaitable[Any]
        ],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, Update):
            user = None

            if event.message:
                user = event.message.from_user

            elif event.callback_query:
                user = event.callback_query.from_user

            elif event.edited_message:
                user = event.edited_message.from_user

            if user and not user.is_bot:
                banned = await is_banned(user.id)

                if banned:
                    reason = str(banned["reason"] or "Belirtilmedi")

                    if event.message:
                        await event.message.answer(
                            "⛔ <b>BOT ERİŞİMİN ENGELLENDİ</b>\n\n"
                            f"Sebep: {reason}",
                            parse_mode="HTML"
                        )

                    elif event.callback_query:
                        await event.callback_query.answer(
                            "⛔ Bot erişimin engellendi.",
                            show_alert=True
                        )

                    return None

        return await handler(event, data)
