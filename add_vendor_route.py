import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/main.py', encoding='utf-8').read()

new_route = '''@app.post("/admin/add-vendor")
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


'''

content = content.replace('@app.post("/admin/remove-vendor")', new_route + '@app.post("/admin/remove-vendor")')
open('app/main.py', 'w', encoding='utf-8').write(content)
print('Done:', 'add-vendor' in content)
