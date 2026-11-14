
from cryptography.fernet import Fernet

import database.db as db
from config import CLONE_ENCRYPTION_KEY


def get_cipher():
    if not CLONE_ENCRYPTION_KEY:
        raise RuntimeError(
            "CLONE_ENCRYPTION_KEY ayarlanmamış!"
        )

    return Fernet(CLONE_ENCRYPTION_KEY.encode())


async def save_clone(
    bot_id: int,
    owner_id: int,
    username: str,
    token: str
):
    if db.pool is None:
        raise RuntimeError("Veritabanı başlatılmamış!")

    encrypted_token = get_cipher().encrypt(
        token.encode()
    ).decode()

    async with db.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO clones (
                bot_id,
                owner_id,
                username,
                encrypted_token
            )
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (bot_id)
            DO UPDATE SET
                owner_id = EXCLUDED.owner_id,
                username = EXCLUDED.username,
                encrypted_token = EXCLUDED.encrypted_token
        """,
            bot_id,
            owner_id,
            username,
            encrypted_token
        )


async def get_clones():
    if db.pool is None:
        return []

    async with db.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT bot_id, owner_id, username, encrypted_token
            FROM clones
        """)

    cipher = get_cipher()
    clones = []

    for row in rows:
        token = cipher.decrypt(
            row["encrypted_token"].encode()
        ).decode()

        clones.append({
            "bot_id": row["bot_id"],
            "owner_id": row["owner_id"],
            "username": row["username"],
            "token": token,
        })

    return clones
  
