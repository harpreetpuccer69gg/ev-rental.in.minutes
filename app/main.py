from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import asyncio
import shutil
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
VENDORS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "vendors.json"))

app = FastAPI(title="EV Assist Landing Page")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Pre-load sheet connection at startup so it's ready when leads come in
_sheet = None
def get_cached_sheet():
    global _sheet
    if _sheet is None:
        from app.sheets import get_sheet
        _sheet = get_sheet()
    return _sheet

@app.on_event("startup")
async def startup_event():
    try:
        get_cached_sheet()
        print("Google Sheet connection established at startup")
    except Exception as e:
        print(f"Startup sheet connection failed: {e}")


@app.get("/vendors")
@app.head("/vendors")
def get_vendors():
    try:
        with open(VENDORS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/submit-lead")
async def submit_lead(request: Request):
    data = await request.json()
    try:
        from app.sheets import log_lead
        session = {
            "name": data.get("name", ""),
            "city": data.get("city", ""),
            "lang": data.get("lang", "en"),
            "budget": data.get("budget", ""),
            "licence": data.get("licence", True),
            "chosen": {
                "Vendor": data.get("vendor", ""),
                "Make": data.get("make", ""),
                "Type": data.get("type", ""),
                "Approx Rental/Week": data.get("rental", ""),
                "Security Deposit": data.get("security_deposit", ""),
                "Refundable Deposit": data.get("refundable_deposit", ""),
                "Image": data.get("image", ""),
                "SPOC": data.get("spoc_name", ""),
                "Phone": data.get("spoc_phone", "")
            }
        }
        # Run sheet write in thread so it fully completes before response
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, log_lead, session, data.get("phone", ""))
        print(f"Lead logged: {data.get('name')} - {data.get('city')}")
        return JSONResponse({"status": "ok"})
    except Exception as e:
        import traceback
        print(f"Sheet error: {e}")
        print(traceback.format_exc())
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.get("/vendor")
def vendor_portal():
    return FileResponse(os.path.join(STATIC_DIR, "vendor_portal.html"))

@app.get("/admin")
def admin_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "admin_dashboard.html"))

@app.post("/vendor/register")
async def vendor_register(request: Request):
    from app.vendor_auth import register_vendor
    d = await request.json()
    return JSONResponse(register_vendor(d['email'], d['password'], d['vendor_name'], d.get('phone','')))

@app.post("/vendor/login")
async def vendor_login(request: Request):
    from app.vendor_auth import login_vendor
    d = await request.json()
    return JSONResponse(login_vendor(d['email'], d['password']))

@app.post("/admin/login")
async def admin_login(request: Request):
    from app.vendor_auth import login_admin
    d = await request.json()
    return JSONResponse(login_admin(d['email'], d['password']))

@app.post("/vendor/propose")
async def vendor_propose(request: Request):
    from app.vendor_auth import submit_change
    d = await request.json()
    return JSONResponse(submit_change(d['token'], d['type'], d['payload']))

@app.post("/vendor/upload-image")
async def upload_image(token: str = Form(...), file: UploadFile = File(...)):
    from app.vendor_auth import decode_token
    user = decode_token(token)
    if not user:
        return JSONResponse({'ok': False, 'msg': 'Unauthorized'}, status_code=401)
    allowed = ['image/jpeg','image/png','image/webp','video/mp4']
    if file.content_type not in allowed:
        return JSONResponse({'ok': False, 'msg': 'Invalid file type'})
    ext = os.path.splitext(file.filename)[1]
    fname = f"vendor_{user['email'].split('@')[0]}_{file.filename.replace(' ','_')}"
    fpath = os.path.join(STATIC_DIR, 'images', fname)
    with open(fpath, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    return JSONResponse({'ok': True, 'image_url': f'/static/images/{fname}'})

@app.post("/admin/review")
async def admin_review(request: Request):
    from app.vendor_auth import review_change
    d = await request.json()
    return JSONResponse(review_change(d['token'], d['change_id'], d['action'], d.get('note','')))

@app.post("/admin/approve-vendor")
async def admin_approve_vendor(request: Request):
    from app.vendor_auth import approve_vendor
    d = await request.json()
    return JSONResponse(approve_vendor(d['token'], d['vendor_id'], d['action']))

@app.get("/admin/pending")
async def get_pending(request: Request):
    from app.vendor_auth import decode_token, load_pending, load_auth, ADMIN_EMAILS
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user = decode_token(token)
    if not user or user.get('role') != 'admin':
        return JSONResponse({'ok': False}, status_code=401)
    return JSONResponse({'changes': load_pending(), 'vendors': [v for v in load_auth() if v['status']=='pending']})

@app.get("/vendor/my-listings")
async def my_listings(request: Request):
    from app.vendor_auth import decode_token, load_auth, load_vendors
    token = request.headers.get('Authorization','').replace('Bearer ','')
    user = decode_token(token)
    if not user or user.get('role') != 'vendor':
        return JSONResponse({'ok': False}, status_code=401)
    auth = load_auth()
    vendor = next((v for v in auth if v['email'] == user['email']), None)
    vendors = load_vendors()
    my = [v for v in vendors if v.get('Vendor','').lower() == vendor['vendor_name'].lower()]
    return JSONResponse({'ok': True, 'listings': my, 'vendor_name': vendor['vendor_name']})


@app.post("/admin/add-vendor")
async def add_vendor_entry(request: Request):
    from app.vendor_auth import decode_token, load_vendors, save_vendors
    d = await request.json()
    user = decode_token(d.get('token',''))
    if not user or user.get('role') != 'admin':
        return JSONResponse({'ok': False, 'msg': 'Unauthorized'}, status_code=401)
    payload = d.get('payload', {})
    if not payload.get('Vendor') or not payload.get('City') or not payload.get('Make'):
        return JSONResponse({'ok': False, 'msg': 'Vendor, City and Make are required'})
    vendors = load_vendors()
    vendors.append(payload)
    save_vendors(vendors)
    return JSONResponse({'ok': True, 'msg': f'Added {payload["Vendor"]} - {payload["Make"]} in {payload["City"]}'})


@app.post("/admin/remove-vendor")
async def remove_vendor(request: Request):
    from app.vendor_auth import decode_token, load_vendors, save_vendors
    d = await request.json()
    user = decode_token(d.get('token',''))
    if not user or user.get('role') != 'admin':
        return JSONResponse({'ok': False, 'msg': 'Unauthorized'}, status_code=401)
    vendors = load_vendors()
    filtered = [v for v in vendors if not (
        v.get('Vendor','').lower() == d.get('vendor','').lower() and
        v.get('City','').lower() == d.get('city','').lower() and
        v.get('Make','').lower() == d.get('make','').lower()
    )]
    if len(filtered) == len(vendors):
        return JSONResponse({'ok': False, 'msg': 'Vendor entry not found'})
    save_vendors(filtered)
    return JSONResponse({'ok': True, 'msg': f'Removed successfully'})


@app.head("/health")
def health():
    return {"status": "EV Assist is running 🚴"}


@app.get("/bounce")
@app.head("/bounce")
def bounce():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/")
@app.head("/")
def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
