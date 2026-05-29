import os, sys
from dotenv import load_dotenv
load_dotenv()

print("SHEET_ID:", os.getenv("GOOGLE_SHEET_ID", "NOT SET"))
print("CREDS_JSON set:", bool(os.getenv("GOOGLE_CREDS_JSON", "")))
print("credentials.json exists:", os.path.exists("credentials.json"))

try:
    import gspread
    from google.oauth2.service_account import Credentials
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    print("Sheet title:", sh.title)
    tabs = [ws.title for ws in sh.worksheets()]
    print("All tabs:", tabs)
    ws = sh.worksheet("Leads ")
    print("Tab [Leads ] found, headers:", ws.row_values(1))
    ws.append_row(["TEST_TS","TEST_NAME","7777777777","Bangalore","English","","","Yulu","Yulu Dex GR","Low speed","1364","499","NIL","Sandeep","8884468333","New Lead"])
    print("SUCCESS - test row written to sheet")
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()

sys.stdout.flush()
