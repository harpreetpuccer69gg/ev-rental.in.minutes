"""
Persistent storage for vendor auth and pending changes using Google Sheets.
Sheet tabs:
  - "Vendor Auth"    → vendors_auth data
  - "Pending Changes" → pending_changes data
Each row stores one JSON-encoded record in column A.
"""
import json, os
from app.sheets import get_sheet
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _get_spreadsheet():
    """Get the full spreadsheet object (not just one worksheet)."""
    creds_json = os.getenv("GOOGLE_CREDS_JSON", "")
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "")
    if creds_json:
        import json as _json
        info = _json.loads(creds_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds_file = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
        creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)

def _get_tab(title: str):
    """Get or create a worksheet tab by title."""
    spreadsheet = _get_spreadsheet()
    try:
        return spreadsheet.worksheet(title)
    except Exception:
        ws = spreadsheet.add_worksheet(title=title, rows=1000, cols=2)
        return ws

def _read_all(title: str) -> list:
    ws = _get_tab(title)
    rows = ws.col_values(1)  # all values in column A
    result = []
    for r in rows:
        if r and r.strip():
            try:
                result.append(json.loads(r))
            except Exception:
                pass
    return result

def _write_all(title: str, data: list):
    ws = _get_tab(title)
    ws.clear()
    if data:
        ws.update('A1', [[json.dumps(row)] for row in data])

# ── Vendor Auth ──────────────────────────────────────────────────────────────

def load_auth() -> list:
    try:
        return _read_all("Vendor Auth")
    except Exception as e:
        print(f"[sheets_db] load_auth error: {e}")
        return _load_local_auth()

def save_auth(data: list):
    try:
        _write_all("Vendor Auth", data)
    except Exception as e:
        print(f"[sheets_db] save_auth error: {e}")
        _save_local_auth(data)

# ── Pending Changes ───────────────────────────────────────────────────────────

def load_pending() -> list:
    try:
        return _read_all("Pending Changes")
    except Exception as e:
        print(f"[sheets_db] load_pending error: {e}")
        return _load_local_pending()

def save_pending(data: list):
    try:
        _write_all("Pending Changes", data)
    except Exception as e:
        print(f"[sheets_db] save_pending error: {e}")
        _save_local_pending(data)

# ── Local JSON fallbacks (in case Sheets is down) ────────────────────────────

AUTH_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'vendors_auth.json'))
PENDING_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'pending_changes.json'))

def _load_local_auth():
    try:
        with open(AUTH_PATH, encoding='utf-8') as f: return json.load(f)
    except: return []

def _save_local_auth(data):
    with open(AUTH_PATH, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)

def _load_local_pending():
    try:
        with open(PENDING_PATH, encoding='utf-8') as f: return json.load(f)
    except: return []

def _save_local_pending(data):
    with open(PENDING_PATH, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
