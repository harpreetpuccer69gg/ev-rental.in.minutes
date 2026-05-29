import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/main.py', encoding='utf-8').read()

new_route = '''@app.post("/admin/remove-vendor")
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


'''

content = content.replace('@app.head("/health")', new_route + '@app.head("/health")')
open('app/main.py', 'w', encoding='utf-8').write(content)
print('Done:', 'remove-vendor' in content)
