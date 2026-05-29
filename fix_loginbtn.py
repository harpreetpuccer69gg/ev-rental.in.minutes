import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/static/admin_dashboard.html', encoding='utf-8').read()

# Fix 1: Add id to button
content = content.replace(
    '<button class="btn" onclick="doAdminLogin()">Login \u2192</button>',
    '<button class="btn" id="loginBtn" onclick="doAdminLogin()">Login \u2192</button>'
)

# Fix 2: Remove btn lines from doAdminLogin since id may not exist
old = "  const btn = document.getElementById('loginBtn');\n  btn.innerText = 'Logging in...'; btn.disabled = true;\n  const res = await fetch('/admin/login'"
new = "  const res = await fetch('/admin/login'"
content = content.replace(old, new)

old2 = "  btn.innerText = 'Login \u2192'; btn.disabled = false;\n  if (d.ok) {"
new2 = "  if (d.ok) {"
content = content.replace(old2, new2)

open('app/static/admin_dashboard.html', 'w', encoding='utf-8').write(content)
print('loginBtn in content:', 'id="loginBtn"' in content)
print('Done')
