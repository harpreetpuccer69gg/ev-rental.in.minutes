import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta
import os
import json
import math

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
DS_EXCEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Lead of ev_assit.xlsx"))
DS_MATCH_METERS = 400

HEADERS = [
    "Timestamp", "Rider Name", "Rider Phone", "City", "Language",
    "Budget Range", "Range Preference", "Vendor", "Make", "Type",
    "Rental/Week", "Security Deposit", "Refundable Deposit",
    "SPOC Name", "SPOC Phone", "Status",
    "Latitude", "Longitude", "DS City", "DS Store", "Distance (Meters)", "Lead Type"
]

BUDGET_LABELS = {
    "1": "Below Rs.1000",
    "2": "Rs.1000 - Rs.1500",
    "3": "Rs.1500 - Rs.2000",
    "4": "Above Rs.2000"
}

LANG_LABELS = {
    "en": "English", "hi": "Hindi", "bn": "Bengali", "kn": "Kannada"
}

KNOWN_CITIES = {
    "bangalore", "mumbai", "delhi ncr", "chennai", "kolkata", "hyderabad",
    "pune", "ahmedabad", "jaipur", "lucknow", "guwahati", "patna",
    "coimbatore", "surat", "vadodara", "bhopal", "indore", "kochi",
    "madurai", "zirakpur"
}

IST = timezone(timedelta(hours=5, minutes=30))


_sheet_cache = None
_bulk_sheet_cache = None

BULK_HEADERS = [
    "Timestamp", "FC Name", "Hub ID", "Phone", "City", "Vendor",
    "EV Type", "Make", "Quantity", "Required By", "Notes",
    "Latitude", "Longitude", "Maps Link", "Status"
]

DS_STORES = None

def _get_client():
    creds_json = os.getenv("GOOGLE_CREDS_JSON", "")
    if not creds_json and not os.path.exists(CREDS_FILE):
        raise RuntimeError("No Google credentials found. Set GOOGLE_CREDS_JSON env var on Render.")
    if creds_json:
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def _find_or_create_leads_sheet(wb):
    """Find the Leads sheet by trying multiple name variants, create if missing."""
    for name in ("Leads", "Leads ", "leads", "Sheet1"):
        try:
            return wb.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            continue
    # Create it fresh
    sheet = wb.add_worksheet(title="Leads", rows=5000, cols=20)
    sheet.insert_row(HEADERS, 1)
    print("Created new Leads worksheet")
    return sheet

def get_sheet():
    global _sheet_cache
    if _sheet_cache is not None:
        try:
            _sheet_cache.cell(1, 1)  # ping to check connection is alive
            return _sheet_cache
        except Exception:
            _sheet_cache = None  # reset and reconnect
    client = _get_client()
    wb = client.open_by_key(SHEET_ID)
    sheet = _find_or_create_leads_sheet(wb)
    existing_headers = sheet.row_values(1) if sheet.get_all_values() else []
    if not existing_headers:
        sheet.insert_row(HEADERS, 1)
    else:
        missing_headers = [header for header in HEADERS if header not in existing_headers]
        for header in missing_headers:
            column = len(existing_headers) + 1
            sheet.update_cell(1, column, header)
            existing_headers.append(header)
    _sheet_cache = sheet
    print(f"✅ Connected to sheet tab: '{sheet.title}'")
    return _sheet_cache

def get_bulk_sheet():
    global _bulk_sheet_cache
    if _bulk_sheet_cache is not None:
        try:
            _bulk_sheet_cache.cell(1, 1)
            return _bulk_sheet_cache
        except Exception:
            _bulk_sheet_cache = None
    client = _get_client()
    wb = client.open_by_key(SHEET_ID)
    try:
        sheet = wb.worksheet("Bulk Requests")
    except gspread.exceptions.WorksheetNotFound:
        sheet = wb.add_worksheet(title="Bulk Requests", rows=1000, cols=15)
    if not sheet.get_all_values() or sheet.cell(1, 1).value != "Timestamp":
        sheet.insert_row(BULK_HEADERS, 1)
    _bulk_sheet_cache = sheet
    return _bulk_sheet_cache


def log_lead(session: dict, phone: str):
    global _sheet_cache
    chosen = session.get("chosen", {})
    latitude = session.get("latitude", "")
    longitude = session.get("longitude", "")
    ds_city, ds_store, distance, lead_type = match_ds_store(latitude, longitude)
    row = [
        datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
        session.get("name", ""),
        phone,
        session.get("city", "") if session.get("city", "").strip().lower() in KNOWN_CITIES else f"Others: {session.get('city', '')}",
        LANG_LABELS.get(session.get("lang", "en"), "English"),
        ", ".join([BUDGET_LABELS.get(str(b), "") for b in (session.get("budget") or [])]) if isinstance(session.get("budget", []), list) else BUDGET_LABELS.get(str(session.get("budget", "")), ""),
        "",
        chosen.get("Vendor", ""),
        chosen.get("Make", ""),
        chosen.get("Type", ""),
        chosen.get("Approx Rental/Week", ""),
        chosen.get("Security Deposit", ""),
        chosen.get("Refundable Deposit", ""),
        chosen.get("SPOC", ""),
        chosen.get("Phone", ""),
        "New Lead",
        latitude,
        longitude,
        ds_city,
        ds_store,
        distance,
        lead_type
    ]
    try:
        get_sheet().append_row(row)
    except Exception:
        _sheet_cache = None
        get_sheet().append_row(row)


def log_bulk_request(data: dict):
    row = [
        datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
        data.get("fc_name", ""),
        data.get("hub_id", ""),
        data.get("phone", ""),
        data.get("city", ""),
        data.get("vendor", ""),
        data.get("ev_type", ""),
        data.get("make", ""),
        data.get("quantity", ""),
        data.get("required_by", ""),
        data.get("notes", ""),
        data.get("latitude", ""),
        data.get("longitude", ""),
        f"https://www.google.com/maps?q={data.get('latitude','')},{data.get('longitude','')}" if data.get("latitude") else "",
        "New Request"
    ]
    get_bulk_sheet().append_row(row)

def load_ds_stores():
    global DS_STORES
    if DS_STORES is not None:
        return DS_STORES
    DS_STORES = []
    if not os.path.exists(DS_EXCEL_PATH):
        print(f"DS workbook not found: {DS_EXCEL_PATH}")
        return DS_STORES
    try:
        import openpyxl
        workbook = openpyxl.load_workbook(DS_EXCEL_PATH, read_only=True, data_only=True)
        sheet = workbook["ds"]
        headers = [str(cell.value).strip().lower() if cell.value is not None else "" for cell in next(sheet.iter_rows(min_row=1, max_row=1))]
        city_i = headers.index("city")
        store_i = headers.index("store name")
        lat_i = headers.index("lat")
        long_i = headers.index("long")
        for row in sheet.iter_rows(min_row=2, values_only=True):
            try:
                lat = float(row[lat_i])
                long = float(row[long_i])
            except (TypeError, ValueError, IndexError):
                continue
            DS_STORES.append({
                "city": str(row[city_i]).strip() if row[city_i] is not None else "",
                "store": str(row[store_i]).strip() if row[store_i] is not None else "",
                "lat": lat,
                "long": long,
            })
        workbook.close()
        print(f"Loaded {len(DS_STORES)} DS store locations")
    except Exception as e:
        print(f"Failed to load DS workbook: {type(e).__name__}: {e}")
    return DS_STORES


def distance_meters(lat1, lon1, lat2, lon2):
    radius = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def match_ds_store(latitude, longitude):
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (TypeError, ValueError):
        return "", "", "", "Normal Lead"

    nearest = None
    nearest_distance = None
    for store in load_ds_stores():
        distance = distance_meters(lat, lon, store["lat"], store["long"])
        if nearest_distance is None or distance < nearest_distance:
            nearest = store
            nearest_distance = distance

    if nearest is not None and nearest_distance <= DS_MATCH_METERS:
        return nearest["city"], nearest["store"], round(nearest_distance, 1), "DS Lead"
    distance_text = round(nearest_distance, 1) if nearest_distance is not None else ""
    return "", "", distance_text, "Normal Lead"
