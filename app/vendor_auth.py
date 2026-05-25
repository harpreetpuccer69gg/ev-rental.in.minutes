import json, os, bcrypt, jwt, smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

AUTH_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'vendors_auth.json'))
PENDING_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'pending_changes.json'))
VENDORS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'vendors.json'))

SECRET = os.getenv('JWT_SECRET', 'ev-assist-secret-2025')
ADMIN_EMAILS = [
    'navin.chandra@flipkart.com',
    'vikas.prasad@flipkart.com',
    'harpreetsingh7.vc@flipkart.com',
    'hs6727586@gmail.com'
]
NOTIFY_EMAILS = ['navin.chandra@flipkart.com', 'harpreetsingh7.vc@flipkart.com']
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASS = os.getenv('SMTP_PASS', '')


def load_auth():
    try:
        with open(AUTH_PATH, encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_auth(data):
    with open(AUTH_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_pending():
    try:
        with open(PENDING_PATH, encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_pending(data):
    with open(PENDING_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_vendors():
    with open(VENDORS_PATH, encoding='utf-8') as f:
        return json.load(f)

def save_vendors(data):
    with open(VENDORS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def hash_password(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def verify_password(pwd: str, hashed: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def create_token(email: str, role: str) -> str:
    payload = {'email': email, 'role': role, 'exp': datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(payload, SECRET, algorithm='HS256')

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except:
        return None


def send_email(to_list, subject, body):
    if not SMTP_USER or not SMTP_PASS:
        print(f'[EMAIL SKIP] To: {to_list} | {subject}')
        return
    import threading
    def _send():
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = SMTP_USER
            msg['To'] = ', '.join(to_list)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(SMTP_USER, to_list, msg.as_string())
            print(f'[EMAIL OK] To: {to_list}')
        except Exception as e:
            print(f'Email error: {e}')
    threading.Thread(target=_send, daemon=True).start()


def register_vendor(email: str, password: str, vendor_name: str, phone: str):
    auth = load_auth()
    if any(v['email'] == email for v in auth):
        return {'ok': False, 'msg': 'Email already registered'}
    entry = {
        'id': f'v_{len(auth)+1}',
        'email': email,
        'password': hash_password(password),
        'vendor_name': vendor_name,
        'phone': phone,
        'status': 'pending',  # needs admin approval
        'created_at': datetime.now().isoformat()
    }
    auth.append(entry)
    save_auth(auth)
    # Notify admins
    send_email(NOTIFY_EMAILS,
        f'New Vendor Registration: {vendor_name}',
        f'New vendor registration request:\n\nName: {vendor_name}\nEmail: {email}\nPhone: {phone}\n\nPlease review at: https://ev-rental-in-minutes.onrender.com/admin'
    )
    return {'ok': True, 'msg': 'Registration submitted. Awaiting admin approval.'}


def login_vendor(email: str, password: str):
    auth = load_auth()
    vendor = next((v for v in auth if v['email'] == email), None)
    if not vendor:
        return {'ok': False, 'msg': 'Email not found'}
    if not verify_password(password, vendor['password']):
        return {'ok': False, 'msg': 'Incorrect password'}
    if vendor['status'] == 'pending':
        return {'ok': False, 'msg': 'Your account is pending admin approval'}
    if vendor['status'] == 'rejected':
        return {'ok': False, 'msg': 'Your account has been rejected'}
    token = create_token(email, 'vendor')
    return {'ok': True, 'token': token, 'vendor_name': vendor['vendor_name'], 'vendor_id': vendor['id']}


def login_admin(email: str, password: str):
    admin_pass = os.getenv('ADMIN_PASSWORD', '').strip()
    if not admin_pass:
        admin_pass = 'Flipkart@2025'
    print(f'[ADMIN LOGIN] email={email} pass_len={len(password)} env_pass_len={len(admin_pass)}')
    if email.strip().lower() not in [e.lower() for e in ADMIN_EMAILS]:
        return {'ok': False, 'msg': 'Not authorized'}
    if password.strip() != admin_pass:
        return {'ok': False, 'msg': 'Incorrect password'}
    token = create_token(email.strip(), 'admin')
    return {'ok': True, 'token': token}


def submit_change(token: str, change_type: str, payload: dict):
    user = decode_token(token)
    if not user or user.get('role') != 'vendor':
        return {'ok': False, 'msg': 'Unauthorized'}
    auth = load_auth()
    vendor = next((v for v in auth if v['email'] == user['email']), None)
    if not vendor:
        return {'ok': False, 'msg': 'Vendor not found'}
    pending = load_pending()
    entry = {
        'id': f'chg_{len(pending)+1}_{int(datetime.now().timestamp())}',
        'vendor_id': vendor['id'],
        'vendor_name': vendor['vendor_name'],
        'vendor_email': vendor['email'],
        'type': change_type,  # 'edit' or 'new'
        'payload': payload,
        'status': 'pending',
        'submitted_at': datetime.now().isoformat(),
        'reviewed_at': None,
        'review_note': ''
    }
    pending.append(entry)
    save_pending(pending)
    send_email(NOTIFY_EMAILS,
        f'New Change Request from {vendor["vendor_name"]}',
        f'Vendor {vendor["vendor_name"]} has submitted a change request.\n\nType: {change_type}\nDetails: {json.dumps(payload, indent=2)}\n\nReview at: https://ev-rental-in-minutes.onrender.com/admin'
    )
    return {'ok': True, 'msg': 'Change request submitted. Awaiting admin approval.'}


def review_change(token: str, change_id: str, action: str, note: str = ''):
    user = decode_token(token)
    if not user or user.get('role') != 'admin':
        return {'ok': False, 'msg': 'Unauthorized'}
    pending = load_pending()
    chg = next((c for c in pending if c['id'] == change_id), None)
    if not chg:
        return {'ok': False, 'msg': 'Change not found'}
    chg['status'] = action  # 'approved' or 'rejected'
    chg['reviewed_at'] = datetime.now().isoformat()
    chg['review_note'] = note
    chg['reviewed_by'] = user['email']
    save_pending(pending)

    if action == 'approved':
        vendors = load_vendors()
        p = chg['payload']
        if chg['type'] == 'new':
            vendors.append(p)
        elif chg['type'] == 'edit':
            for i, v in enumerate(vendors):
                if v.get('Vendor','').lower() == p.get('Vendor','').lower() and v.get('City','').lower() == p.get('City','').lower() and v.get('Make','').lower() == p.get('Make','').lower():
                    vendors[i] = p
                    break
        elif chg['type'] == 'delete':
            vendors = [v for v in vendors if not (
                v.get('Vendor','').lower() == p.get('Vendor','').lower() and
                v.get('City','').lower() == p.get('City','').lower() and
                v.get('Make','').lower() == p.get('Make','').lower()
            )]
        save_vendors(vendors)
        send_email([chg['vendor_email']],
            f'Your change request has been APPROVED',
            f'Hi {chg["vendor_name"]},\n\nYour change request has been approved and is now live.\n\nDetails: {json.dumps(chg["payload"], indent=2)}\n\n- Flipkart Minutes EV Assist'
        )
    else:
        send_email([chg['vendor_email']],
            f'Your change request has been REJECTED',
            f'Hi {chg["vendor_name"]},\n\nYour change request has been rejected.\n\nReason: {note}\n\nPlease contact support if you have questions.\n\n- Flipkart Minutes EV Assist'
        )
    return {'ok': True, 'msg': f'Change {action}'}


def approve_vendor(token: str, vendor_id: str, action: str):
    user = decode_token(token)
    if not user or user.get('role') != 'admin':
        return {'ok': False, 'msg': 'Unauthorized'}
    auth = load_auth()
    vendor = next((v for v in auth if v['id'] == vendor_id), None)
    if not vendor:
        return {'ok': False, 'msg': 'Vendor not found'}
    vendor['status'] = 'approved' if action == 'approve' else 'rejected'
    save_auth(auth)
    if action == 'approve':
        send_email([vendor['email']],
            'Your EV Assist vendor account is approved!',
            f'Hi {vendor["vendor_name"]},\n\nYour vendor account has been approved!\n\nLogin at: https://ev-rental-in-minutes.onrender.com/vendor\n\n- Flipkart Minutes EV Assist'
        )
    else:
        send_email([vendor['email']],
            'EV Assist vendor account update',
            f'Hi {vendor["vendor_name"]},\n\nYour vendor registration was not approved at this time.\n\n- Flipkart Minutes EV Assist'
        )
    return {'ok': True}
