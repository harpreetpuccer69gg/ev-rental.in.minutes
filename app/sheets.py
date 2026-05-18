import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
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


def get_sheet():
    creds_json = os.getenv("GOOGLE_CREDS_JSON", "")
    if creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    if not sheet.get_all_values() or sheet.cell(1, 1).value != "Timestamp":
        sheet.insert_row(HEADERS, 1)
    return sheet


def log_lead(session: dict, phone: str):
    chosen = session.get("chosen", {})
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        session.get("name", ""),
        phone,
        session.get("city", ""),
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
        "New Lead"
    ]
    get_sheet().append_row(row)
