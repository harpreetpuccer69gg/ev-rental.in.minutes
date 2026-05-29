f = open('app/static/admin_dashboard.html', encoding='utf-8')
c = f.read()
f.close()

# Fix 1: duplicate id on login button - keep only one clean id
c = c.replace('id="loginBtn" id="loginBtn2"', 'id="loginBtn"')

# Fix 2: add id to toggle password button (find it by its unique style)
# The button is next to adminPass input, has font-size:18px style
old_toggle = '<button type="button" id="togglePwdBtn"'
if old_toggle not in c:
    # Find the button near adminPass and add id
    c = c.replace(
        '<button type="button"',
        '<button type="button" id="togglePwdBtn"',
        1  # only first occurrence = the password toggle
    )

# Fix 3: fix duplicate ids on inputs
c = c.replace('id="histSearch" placeholder="🔍 Search vendor..." id="histSearchInput"', 
               'id="histSearch" placeholder="🔍 Search vendor..."')
c = c.replace('id="vendorSearch" placeholder="🔍 Search vendor or city..." class="search-box" style="width:200px;" id="vendorSearchInput"',
               'id="vendorSearch" placeholder="🔍 Search vendor or city..." class="search-box" style="width:200px;"')

# Fix 4: update DOMContentLoaded to use correct id 'loginBtn' not 'loginBtn2'
c = c.replace("getElementById('loginBtn2')", "getElementById('loginBtn')")

f = open('app/static/admin_dashboard.html', 'w', encoding='utf-8')
f.write(c)
f.close()

# Verify
f = open('app/static/admin_dashboard.html', encoding='utf-8')
c2 = f.read()
f.close()
print('loginBtn2 gone:', 'loginBtn2' not in c2)
print('togglePwdBtn present:', 'togglePwdBtn' in c2)
print('duplicate histSearch gone:', 'histSearchInput' not in c2)
print('getElementById loginBtn:', "getElementById('loginBtn')" in c2)
print('Done')
