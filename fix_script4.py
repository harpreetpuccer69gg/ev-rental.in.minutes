import re

f = open('app/static/admin_dashboard.html', encoding='utf-8')
c = f.read()
f.close()

# Replace all onclick attributes with unique IDs
replacements = [
    ('onclick="togglePwd(\'adminPass\',this)"', 'id="togglePwdBtn"'),
    ('onclick="doLogout()"', 'id="logoutBtn"'),
    ('onclick="openAddVendor()"', 'id="openAddVendorBtn"'),
    ('onclick="closeAddVendor()"', 'id="closeAddVendorBtn"'),
    ('onclick="submitAddVendor()"', 'id="submitAddVendorBtn"'),
    ('onclick="filterVendors()"', 'id="vendorSearchInp"'),
]

for old, new in replacements:
    c = c.replace(old, new)

# Fix vendorSearch input - it already has id, just remove oninput
c = c.replace('id="vendorSearch"', 'id="vendorSearch"')
c = c.replace('oninput="filterVendors()"', 'id="vendorSearchInput"')
c = c.replace('oninput="filterHistory()"', 'id="histSearchInput"')

# Add comprehensive DOMContentLoaded listeners
listener_code = """
document.addEventListener('DOMContentLoaded', function() {
  // Login
  var lb = document.getElementById('loginBtn2');
  if (lb) lb.addEventListener('click', doAdminLogin);

  // Toggle password
  var tp = document.getElementById('togglePwdBtn');
  if (tp) tp.addEventListener('click', function() {
    var inp = document.getElementById('adminPass');
    if (inp.type === 'password') { inp.type = 'text'; this.innerText = '🙈'; }
    else { inp.type = 'password'; this.innerText = '👁'; }
  });

  // Enter key on password
  var ap = document.getElementById('adminPass');
  if (ap) ap.addEventListener('keydown', function(e){ if(e.key==='Enter') doAdminLogin(); });

  // Logout
  var lo = document.getElementById('logoutBtn');
  if (lo) lo.addEventListener('click', doLogout);

  // Add EV button
  var av = document.getElementById('openAddVendorBtn');
  if (av) av.addEventListener('click', openAddVendor);

  // Close modal
  var ca = document.getElementById('closeAddVendorBtn');
  if (ca) ca.addEventListener('click', closeAddVendor);

  // Submit add vendor
  var sa = document.getElementById('submitAddVendorBtn');
  if (sa) sa.addEventListener('click', submitAddVendor);

  // Vendor search
  var vs = document.getElementById('vendorSearch');
  if (vs) vs.addEventListener('input', filterVendors);

  // History search
  var hs = document.getElementById('histSearch');
  if (hs) hs.addEventListener('input', function(){ filterHistory(); });

  // Modal backdrop close
  var modal = document.getElementById('addVendorModal');
  if (modal) modal.addEventListener('click', function(e){
    if (e.target === modal) closeAddVendor();
  });
  var box = document.querySelector('.add-vendor-box');
  if (box) box.addEventListener('click', function(e){ e.stopPropagation(); });
});
"""

# Remove old DOMContentLoaded block if exists
c = re.sub(r'\n// Attach all event listeners.*?}\);\n', '\n', c, flags=re.DOTALL)

# Insert before </script></head>
c = c.replace('</script>\n</head>', listener_code + '</script>\n</head>')

# Remove onclick from modal backdrop (handled by addEventListener now)
c = c.replace(' onclick="closeAddVendor()"', '')
c = c.replace(' onclick="event.stopPropagation()"', '')

f = open('app/static/admin_dashboard.html', 'w', encoding='utf-8')
f.write(c)
f.close()

# Verify no onclick left for critical buttons
remaining = re.findall(r'onclick="[^"]*"', c)
print(f'Remaining onclicks ({len(remaining)}):')
for r in remaining[:20]:
    print(' ', r)
print('Done')
