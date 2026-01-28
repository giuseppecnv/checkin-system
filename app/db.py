import os
import psycopg2
import urllib.parse as up
from datetime import datetime, date
from openpyxl import Workbook, load_workbook

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    # Parsing robusto per gestire password con caratteri speciali e IPv6
    result = up.urlparse(DATABASE_URL)
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=up.unquote(result.password) if result.password else None,
        host=result.hostname,
        port=result.port or 5432,
        sslmode='require'
    )

def add_checkin(vdash: str):
    vdash_clean = vdash.lower().strip()
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now()
    try:
        cur.execute(
            "INSERT INTO checkins (vdash, checkin_time, checkin_date) VALUES (%s, %s, %s)",
            (vdash_clean, now.strftime("%H:%M:%S"), now.date().isoformat())
        )
        conn.commit()
    except Exception as e:
        print(f"Errore add_checkin: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def add_checkout(vdash: str):
    vdash_clean = vdash.lower().strip()
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now()
    try:
        cur.execute(
            "UPDATE checkins SET checkout_time = %s WHERE vdash = %s AND checkin_date = %s AND checkout_time IS NULL",
            (now.strftime("%H:%M:%S"), vdash_clean, now.date().isoformat())
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_all_vdash():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT vdash FROM users;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0].lower().strip() for row in rows]

def is_already_checked_in(vdash: str) -> bool:
    vdash_clean = vdash.lower().strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM checkins WHERE vdash = %s AND checkin_date = %s", (vdash_clean, date.today().isoformat()))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def is_already_checked_out(vdash: str) -> bool:
    vdash_clean = vdash.lower().strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM checkins WHERE vdash = %s AND checkin_date = %s AND checkout_time IS NOT NULL", (vdash_clean, date.today().isoformat()))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def get_checkins_by_date(target_date: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.vdash, c.checkin_time, c.checkout_time, u.first_name, u.last_name
        FROM checkins c
        JOIN users u ON c.vdash = u.vdash
        WHERE c.checkin_date = %s ORDER BY c.checkin_time;
    """, (target_date,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [(r[0].upper(), str(r[1])[:5], str(r[2])[:5] if r[2] else "", f"{r[3]} {r[4]}".upper()) for r in rows]

def get_user_by_token(token: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT vdash, first_name, middle_name, last_name FROM users WHERE token = %s", (token,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def get_checkin_time(vdash: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT checkin_time FROM checkins WHERE vdash = %s AND checkin_date = %s", (vdash.lower().strip(), date.today().isoformat()))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return str(row[0])[:5] if row else None

def get_checkout_time(vdash: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT checkout_time FROM checkins WHERE vdash = %s AND checkin_date = %s", (vdash.lower().strip(), date.today().isoformat()))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return str(row[0])[:5] if row and row[0] else None

def export_date_to_excel(target_date: str):
    rows = get_checkins_by_date(target_date)
    xlsx_path = "/tmp/checkins.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = target_date
    ws.append(["V-DASH", "CHECK-IN", "CHECK-OUT", "NAME"])
    for r in rows: ws.append(r)
    wb.save(xlsx_path)
