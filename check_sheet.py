import os, sys, traceback
sys.path.insert(0, '.')
os.environ['GOOGLE_SHEET_ID'] = '1RwPcbZp8Wtv5HRdp7uXIMupEmp6V5HXtrAiElx7DEPI'

try:
    from app.sheets import get_sheet, log_lead
    s = get_sheet()
    print('Connected to sheet:', s.title)
    print('Spreadsheet:', s.spreadsheet.title)
    print('All tabs:', [ws.title for ws in s.spreadsheet.worksheets()])
    all_rows = s.get_all_values()
    print('Total rows:', len(all_rows))
    if all_rows:
        print('Header row:', all_rows[0])
    if len(all_rows) > 1:
        print('Last row:', all_rows[-1])

    print('\nWriting test lead...')
    session = {
        'name': 'TEST LEAD DELETE ME',
        'city': 'Chennai',
        'lang': 'en',
        'budget': ['1'],
        'chosen': {
            'Vendor': 'Blive', 'Make': 'Test', 'Type': 'Hi-Speed',
            'Approx Rental/Week': '1400', 'Security Deposit': '500',
            'Refundable Deposit': '', 'Image': '', 'SPOC': 'Sriram', 'Phone': '8939436157'
        }
    }
    log_lead(session, '9876543210')
    print('SUCCESS - check your Google Sheet now')
except Exception as e:
    traceback.print_exc()
