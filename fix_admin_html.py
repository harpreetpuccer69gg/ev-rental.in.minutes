content = open('app/static/admin_dashboard.html', encoding='utf-8').read()

# Fix 1: Add eye icon to password field
old_pass = '<input class="inp" id="adminPass" type="password" placeholder="••••••••"/>'
new_pass = '''<div style="position:relative;">
        <input class="inp" id="adminPass" type="password" placeholder="••••••••" style="margin-bottom:0;padding-right:44px;"/>
        <button type="button" onclick="togglePwd()" style="position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;font-size:18px;color:#757575;">👁</button>
      </div><div style="height:12px;"></div>'''
content = content.replace(old_pass, new_pass)

# Fix 2: Improve login button
old_btn = 'onclick="doAdminLogin()">Login &rarr;</button>'
new_btn = 'onclick="doAdminLogin()" id="loginBtn" style="background:#ffd600;color:#002d62;font-size:16px;font-weight:900;border-radius:12px;padding:15px;">Login →</button>'
content = content.replace(old_btn, new_btn)

# Fix 3: Add togglePwd + loading state to doAdminLogin
old_fn = 'async function doAdminLogin() {'
new_fn = '''function togglePwd() {
  const inp = document.getElementById('adminPass');
  const btn = inp.nextElementSibling;
  if (inp.type === 'password') { inp.type = 'text'; btn.innerText = '🙈'; }
  else { inp.type = 'password'; btn.innerText = '👁'; }
}

async function doAdminLogin() {'''
content = content.replace(old_fn, new_fn, 1)

# Fix 4: Add loading state inside doAdminLogin
old_fetch = "  const res = await fetch('/admin/login'"
new_fetch = """  const btn = document.getElementById('loginBtn');
  btn.innerText = 'Logging in...'; btn.disabled = true;
  const res = await fetch('/admin/login'"""
content = content.replace(old_fetch, new_fetch, 1)

old_after = "  const d = await res.json();\n  if (d.ok) {"
new_after = "  const d = await res.json();\n  btn.innerText = 'Login →'; btn.disabled = false;\n  if (d.ok) {"
content = content.replace(old_after, new_after, 1)

open('app/static/admin_dashboard.html', 'w', encoding='utf-8').write(content)
print('Done')
print('togglePwd added:', 'togglePwd' in content)
print('loginBtn added:', 'loginBtn' in content)
