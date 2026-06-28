import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta
import os
import json

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")

HEADERS = [
    "Timestamp", "Rider Name", "Rider Phone", "City", "Language",
    "Budget Range", "Range Preference", "Vendor", "Make", "Type",
    "Rental/Week", "Security Deposit", "Refundable Deposit",
    "SPOC Name", "SPOC Phone", "Status"
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

def _get_client():
    creds_json = os.getenv("GOOGLE_CREDS_JSON", "")
    if creds_json:
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def get_sheet():
    global _sheet_cache
    if _sheet_cache is not None:
        try:
            _sheet_cache.cell(1, 1)
            return _sheet_cache
        except Exception:
            _sheet_cache = None
    client = _get_client()
    sheet = client.open_by_key(SHEET_ID).worksheet("Leads ")
    if not sheet.get_all_values() or sheet.cell(1, 1).value != "Timestamp":
        sheet.insert_row(HEADERS, 1)
    _sheet_cache = sheet
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
    chosen = session.get("chosen", {})
    row = [
        datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
        session.get("name", ""),
        phone,
        session.get("city", "") if session.get("city", "").strip().lower() in KNOWN_CITIES else f"Others: {session.get('city', '')}",
        LANG_LABELS.get(session.get("lang", "en"), "English"),
        ", ".join([BUDGET_LABELS.get(str(b), "") for b in (session.get("budget") or [])]) if isinstance(session.get("budget"), list) else BUDGET_LABELS.get(str(session.get("budget", "")), ""),
        "",  # Range Preference - kept for column alignment
        chosen.get("Vendor", ""),
        chosen.get("Make", ""),
        chosen.get("Type", ""),
        chosen.get("Approx Rental/Week", ""),
        chosen.get("Security Deposit", ""),
        chosen.get("Refundable Deposit", ""),
        chosen.get("SPOC", ""),
        chosen.get("Phone", ""),
        "Pending"
    ]
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
