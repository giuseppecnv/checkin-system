import os
from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.db import (
    add_checkin,
    add_checkout, 
    get_all_vdash, 
    is_already_checked_in,
    is_already_checked_out,
    get_checkins_by_date,
    export_date_to_excel,
    get_user_by_token,
    get_checkin_time,
    get_checkout_time
)
from datetime import date

app = FastAPI()

# Percorsi da root progetto (static/ e templates/ alla root)
base_path = Path(__file__).resolve().parent
project_root = base_path.parent
static_path = project_root / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    vdash_list = get_all_vdash()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "users": vdash_list}
    )

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.post("/checkin")
def process_checkin(request: Request, vdash: str = Form(...)):
    vdash_clean = vdash.strip()
    today = date.today().isoformat()

    if not is_already_checked_in(vdash_clean):
        add_checkin(vdash_clean)
        export_date_to_excel(today)
    elif not is_already_checked_out(vdash_clean):
        add_checkout(vdash_clean)
        export_date_to_excel(today)

    return RedirectResponse("/", status_code=303)

@app.get("/dashboard")
def dashboard(request: Request, date_str: str = None):
    target_date = date_str if date_str else date.today().isoformat()
    checkins = get_checkins_by_date(target_date)
    all_users = get_all_vdash()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "checkins": checkins,
            "total_users": len(all_users),
            "present": len(checkins),
            "current_date": target_date
        }
    )

@app.get("/download/excel")
def download_excel(date_str: str = None):
    target_date = date_str if date_str else date.today().isoformat()
    export_date_to_excel(target_date)
    xlsx_path = "/tmp/checkins.xlsx"
    
    if os.path.exists(xlsx_path):
        return FileResponse(
            path=xlsx_path,
            filename=f"checkins_{target_date}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    return {"error": "File not found"}

@app.get("/api/check-status")
def check_status(vdash: str):
    checked_in = is_already_checked_in(vdash)
    checked_out = is_already_checked_out(vdash)
    return {
        "has_checked_in": checked_in,
        "has_checked_out": checked_out,
    }

@app.get("/api/token-status")
def token_status(token: str):
    user = get_user_by_token(token)
    if not user: return {"valid": False}

    vdash = user[0]
    first_name = user[1]
    middle_name = user[2]
    last_name = user[3]

    full_name = " ".join(filter(None, [
        first_name.strip() if first_name else "",
        middle_name.strip() if middle_name else "",
        last_name.strip() if last_name else ""
    ]))

    checked_in = is_already_checked_in(vdash)
    checked_out = is_already_checked_out(vdash)

    checkin_time = None
    checkout_time = None
    if checked_in: checkin_time = get_checkin_time(vdash)
    if checked_out: checkout_time = get_checkout_time(vdash)

    return {
        "valid": True,
        "vdash": vdash,
        "full_name": full_name,
        "has_checked_in": checked_in,
        "has_checked_out": checked_out,
        "checkin_time": checkin_time,
        "checkout_time": checkout_time
    }
