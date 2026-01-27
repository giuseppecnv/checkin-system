import sqlite3
from pathlib import Path
from datetime import datetime, date
from openpyxl import Workbook, load_workbook


DB_PATH = Path("data") / "checkins_hcl.db"
XLSX_PATH = Path("data") / "checkins.xlsx"

def init_db():
    pass

def add_checkin(vdash: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    now = datetime.now()
    checkin_time = now.time().isoformat(timespec='seconds')
    checkin_date = now.date().isoformat()

    cur.execute(
        """
        INSERT INTO checkins (vdash, checkin_time, checkin_date)
        VALUES (?, ?, ?)         
        """,
        (vdash, checkin_time, checkin_date) 
    )

    conn.commit()
    conn.close()

def add_checkout(vdash: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.now()
    checkout_time = now.time().isoformat(timespec='seconds')
    today = now.date().isoformat()

    cur.execute(
        """
        UPDATE checkins
        SET checkout_time = ?
        WHERE vdash = ?
        AND checkin_date = ?
        AND checkout_time IS NULL
        """,
        (checkout_time, vdash, today)
    )

    conn.commit()
    conn.close()


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
    vdash_list = [row[0].upper() for row in rows]
    return vdash_list


def is_already_checked_in(vdash: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        SELECT * FROM checkins WHERE vdash = ? 
        AND checkin_date = ?;
        """,
        (vdash, today)
    )

    rows = cur.fetchall()
    conn.close()

    return len(rows) > 0

def is_already_checked_out(vdash: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        SELECT * FROM checkins WHERE vdash = ?
        AND checkin_date = ?
        AND checkout_time IS NOT NULL;
        """,
        (vdash, today)
    )

    rows = cur.fetchall()
    conn.close()

    return len(rows) > 0

def get_checkins_by_date(target_date: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.vdash,
            c.checkin_time,
            c.checkout_time,
            u.first_name,
            u.middle_name,
            u.last_name
        FROM checkins c
        JOIN users u ON UPPER(c.vdash) = UPPER(u.vdash)
        WHERE c.checkin_date = ?
        ORDER BY c.checkin_time;
    """, (target_date,))

    rows = cur.fetchall()
    conn.close()

    formatted_rows = []

    for row in rows:
        vdash = row[0].upper()

        checkin_time = (row[1] or "")[:5]
        checkout_time = (row[2] or "")[:5]

        first = row[3].upper() if row[3] else ""
        middle = row[4].upper() if row[4] else ""
        last = row[5].upper() if row[5] else ""

        full_name = f"{first} {middle} {last}".strip()

        formatted_rows.append(
            (vdash, checkin_time, checkout_time, full_name)
        )

    return formatted_rows


def get_checkout_time(vdash: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        SELECT checkout_time FROM checkins
        WHERE vdash = ? AND checkin_date = ?
        """,
        (vdash, today)
    )

    row = cur.fetchone()
    conn.close()

    if row and row[0]:
        return row[0][:5]
    return None

def export_date_to_excel(target_date: str):
    rows = get_checkins_by_date(target_date)

    if not rows:
        return

    if XLSX_PATH.exists():
        wb = load_workbook(XLSX_PATH)
    else:
        wb = Workbook()
        wb.remove(wb.active)

    if target_date in wb.sheetnames:
        del wb[target_date]

    ws = wb.create_sheet(title=target_date)
    ws.append(["V-DASH", "FULL NAME", "CHECK-IN TIME", "CHECK-OUT TIME"])

    for row in rows:
        ws.append([row[0], row[3], row[1], row[2]])

    wb.save(XLSX_PATH)


def get_user_by_token(token: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
            SELECT vdash, first_name, middle_name, last_name
            FROM users
            WHERE token = ?
        """, 
        (token,)
    )
    
    row = cur.fetchone()
    conn.close()
    
    return row


def get_checkin_time(vdash: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    today = date.today().isoformat()

    cur.execute(
        """
        SELECT checkin_time FROM checkins 
        WHERE vdash = ? AND checkin_date = ?
        """,
        (vdash, today)
    )

    row = cur.fetchone()
    conn.close()

    if row:
        return row[0][:5]
    return None