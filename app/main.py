from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
VENDORS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "vendors.json"))

app = FastAPI(title="EV Assist Landing Page")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


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
        log_lead(session, data.get("phone", ""))
        return JSONResponse({"status": "ok"})
    except Exception as e:
        import traceback
        print(f"Sheet error: {e}")
        print(traceback.format_exc())
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)


@app.get("/health")
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
