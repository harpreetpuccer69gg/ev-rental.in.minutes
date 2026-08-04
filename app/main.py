from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
import os
import json
import asyncio
import shutil
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
VENDORS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "vendors.json"))
SWAP_STATIONS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "swap_stations.json"))

app = FastAPI(title="EV Assist Landing Page")
app.add_middleware(GZipMiddleware, minimum_size=1000)
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
    creds_json = os.getenv("GOOGLE_CREDS_JSON", "")
    creds_file = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
    if not creds_json and not os.path.exists(os.path.join(os.path.dirname(__file__), "..", creds_file)):
        print("⚠️  WARNING: GOOGLE_CREDS_JSON env var not set and credentials.json not found. Leads will NOT be logged!")
    try:
        get_cached_sheet()
        print("✅ Google Sheet connection established at startup")
    except Exception as e:
        print(f"❌ Startup sheet connection failed: {e}")
    # Seed Vendors DB sheet if empty
    try:
        from app.sheets_db import load_vendors_db, save_vendors_db
        existing = load_vendors_db()
        if not existing:
            with open(VENDORS_PATH, encoding='utf-8') as f:
                import json as _json
                data = _json.load(f)
            save_vendors_db(data)
            print(f"Vendors DB seeded with {len(data)} entries from vendors.json")
        else:
            print(f"Vendors DB already has {len(existing)} entries")
    except Exception as e:
        print(f"Vendors DB seed error: {e}")


@app.get("/vendors")
@app.head("/vendors")
def get_vendors():
    try:
        from app.vendor_auth import load_vendors
        data = load_vendors()
        if not data:
            raise ValueError("empty")
        return JSONResponse(data)
    except Exception:
        try:
            with open(VENDORS_PATH, encoding="utf-8") as f:
                return JSONResponse(json.load(f))
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
        print(f"✅ Lead logged to sheet: {data.get('name')} - {data.get('vendor')} - {data.get('city')}")
        return JSONResponse({"status": "ok"})
    except Exception as e:
        import traceback
        print(f"❌ Sheet write FAILED for {data.get('name')} - {data.get('city')}: {e}")
        print(traceback.format_exc())
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.post("/vendor/register")
async def vendor_register(request: Request):
    try:
        from app.vendor_auth import register_vendor
        d = await request.json()
        return JSONResponse(register_vendor(d['email'], d['password'], d['vendor_name'], d.get('phone','')))
    except Exception as e:
        import traceback; traceback.print_exc()
        return JSONResponse({'ok': False, 'msg': str(e)}, status_code=500)

@app.post("/vendor/login")
async def vendor_login(request: Request):
    try:
        from app.vendor_auth import login_vendor
        d = await request.json()
        return JSONResponse(login_vendor(d['email'], d['password']))
    except Exception as e:
        import traceback; traceback.print_exc()
        return JSONResponse({'ok': False, 'msg': str(e)}, status_code=500)

@app.post("/admin/login")
async def admin_login(request: Request):
    try:
        from app.vendor_auth import login_admin
        d = await request.json()
        return JSONResponse(login_admin(d['email'], d['password']))
    except Exception as e:
        import traceback; traceback.print_exc()
        return JSONResponse({'ok': False, 'msg': str(e)}, status_code=500)

@app.post("/vendor/propose")
async def vendor_propose(request: Request):
    try:
        from app.vendor_auth import submit_change
        d = await request.json()
        return JSONResponse(submit_change(d['token'], d['type'], d['payload']))
    except Exception as e:
        import traceback; traceback.print_exc()
        return JSONResponse({'ok': False, 'msg': str(e)}, status_code=500)

@app.post("/vendor/upload-image")
async def upload_image(token: str = Form(...), file: UploadFile = File(...)):
    from app.vendor_auth import decode_token
    user = decode_token(token)
    if not user:
        return JSONResponse({'ok': False, 'msg': 'Session expired. Please login again.'}, status_code=401)
    if user.get('role') != 'vendor':
        return JSONResponse({'ok': False, 'msg': 'Unauthorized'}, status_code=401)
    allowed = ['image/jpeg','image/png','image/webp','video/mp4']
    if file.content_type not in allowed:
        return JSONResponse({'ok': False, 'msg': 'Invalid file type'})
    content = await file.read()
    # Try Cloudinary first (permanent CDN storage)
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME','')
    cloud_key  = os.getenv('CLOUDINARY_API_KEY','')
    cloud_sec  = os.getenv('CLOUDINARY_API_SECRET','')
    if cloud_name and cloud_key and cloud_sec:
        try:
            import cloudinary, cloudinary.uploader, io
            cloudinary.config(cloud_name=cloud_name, api_key=cloud_key, api_secret=cloud_sec)
            resource = 'video' if file.content_type == 'video/mp4' else 'image'
            folder   = 'ev_assist_vendors'
            result   = cloudinary.uploader.upload(
                io.BytesIO(content),
                resource_type=resource,
                folder=folder,
                public_id=f"{user['email'].split('@')[0]}_{os.path.splitext(file.filename)[0].replace(' ','_')}",
                overwrite=True
            )
            return JSONResponse({'ok': True, 'image_url': result['secure_url']})
        except Exception as e:
            print(f'[Cloudinary] upload failed: {e}')
    # Fallback: Google Drive
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        import io, json as _j
        scopes = ['https://www.googleapis.com/auth/drive.file']
        creds_json = os.getenv('GOOGLE_CREDS_JSON','')
        creds_file = os.getenv('GOOGLE_CREDS_FILE','credentials.json')
        creds = Credentials.from_service_account_info(_j.loads(creds_json), scopes=scopes) if creds_json \
                else Credentials.from_service_account_file(creds_file, scopes=scopes)
        drive  = build('drive','v3',credentials=creds)
        fname  = f"vendor_{user['email'].split('@')[0]}_{file.filename.replace(' ','_')}"
        media  = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
        uploaded = drive.files().create(body={'name':fname}, media_body=media, fields='id').execute()
        fid = uploaded.get('id')
        drive.permissions().create(fileId=fid, body={'type':'anyone','role':'reader'}).execute()
        url = f'https://drive.google.com/uc?export=download&id={fid}' if file.content_type=='video/mp4' \
              else f'https://drive.google.com/thumbnail?id={fid}&sz=w800'
        return JSONResponse({'ok': True, 'image_url': url})
    except Exception as e:
        print(f'[Drive] upload failed: {e}')
    # Last resort: local disk (will break on redeploy)
    fname = f"vendor_{user['email'].split('@')[0]}_{file.filename.replace(' ','_')}"
    fpath = os.path.join(STATIC_DIR, 'images', fname)
    with open(fpath, 'wb') as lf:
        lf.write(content)
    return JSONResponse({'ok': True, 'image_url': f'/static/images/{fname}', 'warning': 'Stored locally - will break on redeploy'})

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
    try:
        from app.vendor_auth import decode_token, ADMIN_EMAILS
        from app.sheets_db import load_pending, load_auth
        token = request.headers.get('Authorization','').replace('Bearer ','')
        user = decode_token(token)
        if not user or user.get('role') != 'admin':
            return JSONResponse({'ok': False}, status_code=401)
        return JSONResponse({'changes': load_pending(), 'vendors': load_auth()})
    except Exception as e:
        import traceback; traceback.print_exc()
        return JSONResponse({'ok': False, 'msg': str(e)}, status_code=500)

@app.get("/vendor/my-listings")
async def my_listings(request: Request):
    try:
        from app.vendor_auth import decode_token, load_vendors
        from app.sheets_db import load_auth
        token = request.headers.get('Authorization','').replace('Bearer ','')
        user = decode_token(token)
        if not user or user.get('role') != 'vendor':
            return JSONResponse({'ok': False}, status_code=401)
        auth = load_auth()
        vendor = next((v for v in auth if v['email'] == user['email']), None)
        if not vendor:
            return JSONResponse({'ok': False, 'msg': 'Vendor not found'}, status_code=404)
        vendors = load_vendors()
        my = [v for v in vendors if v.get('Vendor','').lower() == vendor['vendor_name'].lower()]
        return JSONResponse({'ok': True, 'listings': my, 'vendor_name': vendor['vendor_name']})
    except Exception as e:
        import traceback; traceback.print_exc()
        return JSONResponse({'ok': False, 'msg': str(e)}, status_code=500)


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


@app.post("/admin/sync-vendors")
async def sync_vendors(request: Request):
    from app.vendor_auth import decode_token, save_vendors
    d = await request.json()
    user = decode_token(d.get('token',''))
    if not user or user.get('role') != 'admin':
        return JSONResponse({'ok': False, 'msg': 'Unauthorized'}, status_code=401)
    with open(VENDORS_PATH, encoding='utf-8') as f:
        import json as _j
        data = _j.load(f)
    save_vendors(data)
    return JSONResponse({'ok': True, 'msg': f'Synced {len(data)} vendors to Google Sheet'})


@app.get("/swap-stations")
def get_swap_stations():
    try:
        with open(SWAP_STATIONS_PATH, encoding="utf-8") as f:
            return JSONResponse(json.load(f))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/swap-map")
def swap_map():
    return FileResponse(os.path.join(STATIC_DIR, "swap_map.html"))


@app.get("/vendor")
def vendor_portal():
    return FileResponse(os.path.join(STATIC_DIR, "vendor_portal.html"))

@app.get("/admin")
def admin_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "admin_dashboard.html"))

@app.post("/admin/remove-history")
async def remove_history(request: Request):
    from app.vendor_auth import decode_token, load_vendors, save_vendors, git_push_vendors
    from app.sheets_db import load_pending, save_pending, _save_local_pending
    import threading
    d = await request.json()
    user = decode_token(d.get('token',''))
    if not user or user.get('role') != 'admin':
        return JSONResponse({'ok': False, 'msg': 'Unauthorized'}, status_code=401)
    change_id = d.get('change_id')
    pending = load_pending()
    chg = next((c for c in pending if c['id'] == change_id), None)
    if not chg:
        return JSONResponse({'ok': False, 'msg': 'History entry not found'})
    # Remove from marketplace if it was an approved 'new' entry
    removed_from_market = False
    if chg.get('status') == 'approved' and chg.get('type') in ('new', 'edit'):
        p = chg.get('payload', {})
        vendors = load_vendors()
        filtered = [v for v in vendors if not (
            v.get('Vendor','').lower() == p.get('Vendor','').lower() and
            v.get('City','').lower() == p.get('City','').lower() and
            v.get('Make','').lower() == p.get('Make','').lower()
        )]
        if len(filtered) < len(vendors):
            save_vendors(filtered)
            threading.Thread(target=git_push_vendors, args=(f'Auto: removed {p.get("Vendor")} from marketplace',), daemon=True).start()
            removed_from_market = True
    # Remove from history
    updated = [c for c in pending if c['id'] != change_id]
    _save_local_pending(updated)
    threading.Thread(target=save_pending, args=(updated,), daemon=True).start()
    msg = 'Removed from history' + (' and marketplace' if removed_from_market else '')
    return JSONResponse({'ok': True, 'msg': msg, 'removed_from_market': removed_from_market})


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "images", "logo.png"), media_type="image/png")


@app.get("/health")
def health():
    return {"status": "EV Assist is running 🚴"}


@app.get("/bulk-request")
def bulk_request_page():
    return FileResponse(os.path.join(STATIC_DIR, "bulk_request.html"))


@app.post("/submit-bulk-request")
async def submit_bulk_request(request: Request):
    data = await request.json()
    try:
        from app.sheets import log_bulk_request
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, log_bulk_request, data)
        return JSONResponse({"status": "ok"})
    except Exception as e:
        import traceback; traceback.print_exc()
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.get("/bounce")
@app.head("/bounce")
def bounce():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/")
@app.head("/")
def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
