import os
from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.db import (
    init_db, 
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
from datetime import date, timedelta

app = FastAPI()

base_path = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(base_path, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory="app/templates")

init_db()

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
    if not is_already_checked_in(vdash):
        add_checkin(vdash) 
        export_date_to_excel(date.today().isoformat())
        return RedirectResponse("/", status_code=303)
    elif not is_already_checked_out(vdash):
        add_checkout(vdash)
        export_date_to_excel(date.today().isoformat())
        return RedirectResponse("/", status_code=303)   
    
    return RedirectResponse("/", status_code=303)

@app.get("/dashboard")
def dashboard(request: Request, date_str: str = None):

    if date_str: target_date = date_str
    else: target_date = date.today().isoformat()
    
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

    if date_str: target_date = date_str
    else: target_date = date.today().isoformat()
    
    export_date_to_excel(target_date)
    
    xlsx_path = Path("data") / "checkins.xlsx"
    
    return FileResponse(
        str(xlsx_path),
        filename=f"checkins_{target_date}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


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
