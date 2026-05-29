import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/static/admin_dashboard.html', encoding='utf-8').read()

# Fix loadPending to correctly handle vendors array
old = "  const vendors = d.vendors || [];"
new = "  const vendors = (d.vendors || []).filter(v => v.status === 'pending');"
content = content.replace(old, new)

# Also fix showDashboard to call loadPending correctly
old2 = "function showDashboard() {\n  document.getElementById('loginSection').style.display = 'none';\n  document.getElementById('dashSection').style.display = 'block';\n  loadPending();\n}"
new2 = "function showDashboard() {\n  document.getElementById('loginSection').style.display = 'none';\n  document.getElementById('dashSection').style.display = 'block';\n  loadPending();\n  setInterval(loadPending, 30000); // auto-refresh every 30s\n}"
content = content.replace(old2, new2)

open('app/static/admin_dashboard.html', 'w', encoding='utf-8').write(content)
print('Fixed:', old in open('app/static/admin_dashboard.html', encoding='utf-8').read())
print('New filter added:', "filter(v => v.status === 'pending')" in content)
