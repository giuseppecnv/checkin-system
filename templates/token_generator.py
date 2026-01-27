import sqlite3
from pathlib import Path
import uuid

DB_PATH = Path("data") / "checkins_hcl.db"

def get_all_vdash():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT vdash FROM users;
        """
    )

    rows = cur.fetchall()
    conn.close()
    vdash_list = [row[0] for row in rows]
    return vdash_list


def update_user_token(vdash: str, token: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET token = ?
        WHERE vdash = ?
        """,
        (token, vdash)
    )

    conn.commit()
    conn.close()


def generate_all_tokens():
    vdash_list = get_all_vdash()

    for vdash in vdash_list:
        token = str(uuid.uuid4()).replace("-", "")[:10]
        update_user_token(vdash, token)
        print(f"Generated token for {vdash}: {token}")

if __name__ == "__main__":
    generate_all_tokens()
    print("🎉 Tutti i token generati!")