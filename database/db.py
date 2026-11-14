
import asyncpg
import os


pool = None


async def init_db():
    global pool

    database_url = os.getenv("DATABASE_URL", "")

    if not database_url:
        raise RuntimeError("DATABASE_URL ayarlanmamış!")

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    pool = await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=5,
        ssl="require"
    )

    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                group_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                username TEXT,
                full_name TEXT,
                is_bot BOOLEAN DEFAULT FALSE,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, user_id)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS clones (
                bot_id BIGINT PRIMARY KEY,
                owner_id BIGINT NOT NULL,
                username TEXT,
                encrypted_token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tag_logs (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT,
                group_id BIGINT,
                command TEXT,
                tagged_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


async def save_member(group_id, user):
    if pool is None or user.is_bot:
        return

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO members (
                group_id,
                user_id,
                username,
                full_name,
                is_bot,
                last_seen
            )
            VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
            ON CONFLICT (group_id, user_id)
            DO UPDATE SET
                username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                last_seen = CURRENT_TIMESTAMP
        """,
            group_id,
            user.id,
            user.username,
            user.full_name,
            user.is_bot
        )


async def get_members(group_id):
    if pool is None:
        return []

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, username, full_name
            FROM members
            WHERE group_id = $1
            ORDER BY last_seen DESC
        """, group_id)

    return rows


async def get_bot_stats():
    if pool is None:
        return {
            "users": 0,
            "groups": 0,
            "clones": 0
        }

    async with pool.acquire() as conn:
        users = await conn.fetchval("""
            SELECT COUNT(DISTINCT user_id)
            FROM members
        """)

        groups = await conn.fetchval("""
            SELECT COUNT(DISTINCT group_id)
            FROM members
        """)

        clones = await conn.fetchval("""
            SELECT COUNT(*)
            FROM clones
        """)

    return {
        "users": users or 0,
        "groups": groups or 0,
        "clones": clones or 0
    }


async def save_tag_log(user_id, group_id, command, tagged_count):
    if pool is None:
        return

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO tag_logs (
                user_id,
                group_id,
                command,
                tagged_count
            )
            VALUES ($1, $2, $3, $4)
        """,
            user_id,
            group_id,
            command,
            tagged_count
        )


async def close_db():
    global pool

    if pool is not None:
        await pool.close()
        pool = None
