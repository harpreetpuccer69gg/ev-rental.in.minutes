import sys
sys.stdout.reconfigure(encoding='utf-8')

# ── FIX 1: vendor_portal.html ──
content = open('app/static/vendor_portal.html', encoding='utf-8').read()

# Replace openAddModal with safe null-check version
old_modal = '''function openAddModal() {
  document.getElementById('modalTitle').innerText = 'Add New EV Listing';
  document.getElementById('fEditMode').value = 'new';
  document.getElementById('fCity').value = '';
  document.getElementById('fMake').value = '';
  document.getElementById('fRent').value = '';
  document.getElementById('fRange').value = '';
  document.getElementById('fDeposit').value = '';
  document.getElementById('fRefund').value = '';
  document.getElementById('fSpoc').value = '';
  document.getElementById('fSpocPhone').value = '';
  document.getElementById('fImageUrl').value = '';
  document.getElementById('fImageUrl2').value = '';
  document.getElementById('fImageUrl3').value = '';
  document.getElementById('fVideoUrl').value = '';
  [1,2,3].forEach(n => {
    document.getElementById('imgPreview'+n).style.display='none';
    document.getElementById('img'+n+'Icon').style.display='block';
    document.getElementById('fImage'+n).value='';
  });
  document.getElementById('videoPreview').style.display='none';
  document.getElementById('videoName').innerText='Click to upload video';
  document.getElementById('fVideo').value='';
  document.getElementById('imgError').style.display='none';
  document.getElementById('modalMsg').className = 'msg';
  document.getElementById('editModal').classList.add('show');
}'''

new_modal = '''function safeSet(id, prop, val) {
  const el = document.getElementById(id);
  if (el) el[prop] = val;
}
function safeStyle(id, prop, val) {
  const el = document.getElementById(id);
  if (el) el.style[prop] = val;
}

function openAddModal() {
  safeSet('modalTitle','innerText','Add New EV Listing');
  safeSet('fEditMode','value','new');
  safeSet('fCity','value','');
  safeSet('fMake','value','');
  safeSet('fRent','value','');
  safeSet('fRange','value','');
  safeSet('fDeposit','value','');
  safeSet('fRefund','value','');
  safeSet('fSpoc','value','');
  safeSet('fSpocPhone','value','');
  safeSet('fImageUrl','value','');
  safeSet('fImageUrl2','value','');
  safeSet('fImageUrl3','value','');
  safeSet('fVideoUrl','value','');
  [1,2,3].forEach(n => {
    safeStyle('imgPreview'+n,'display','none');
    safeStyle('img'+n+'Icon','display','block');
    safeSet('fImage'+n,'value','');
  });
  safeStyle('videoPreview','display','none');
  safeSet('videoName','innerText','Click to upload video');
  safeSet('fVideo','value','');
  safeStyle('imgError','display','none');
  safeSet('modalMsg','className','msg');
  const modal = document.getElementById('editModal');
  if (modal) modal.classList.add('show');
}'''

content = content.replace(old_modal, new_modal)

# Also fix openEditModal null checks
old_edit = '''  document.getElementById('modalMsg').className = 'msg';
  document.getElementById('editModal').classList.add('show');
}'''
new_edit = '''  safeSet('modalMsg','className','msg');
  const modal = document.getElementById('editModal');
  if (modal) modal.classList.add('show');
}'''
content = content.replace(old_edit, new_edit, 1)

open('app/static/vendor_portal.html', 'w', encoding='utf-8').write(content)
print('vendor_portal.html fixed:', 'safeSet' in content)

# ── FIX 2: admin_dashboard.html - add Manage Vendors tab ──
admin = open('app/static/admin_dashboard.html', encoding='utf-8').read()

# Add new tab button
old_tabs = '''    <div class="tabs">
      <button class="tab active" onclick="switchTab(\'changes\')">Change Requests</button>
      <button class="tab" onclick="switchTab(\'vendors\')">New Vendor Approvals</button>
      <button class="tab" onclick="switchTab(\'history\')">History</button>
    </div>'''
new_tabs = '''    <div class="tabs">
      <button class="tab active" onclick="switchTab(\'changes\')">Change Requests</button>
      <button class="tab" onclick="switchTab(\'vendors\')">New Vendor Approvals</button>
      <button class="tab" onclick="switchTab(\'manage\')">Manage Vendors</button>
      <button class="tab" onclick="switchTab(\'history\')">History</button>
    </div>'''
admin = admin.replace(old_tabs, new_tabs)

# Add manage tab div after history tab div
old_history = '''    <!-- History -->
    <div id="historyTab" style="display:none;">
      <div id="historyArea"><div style="text-align:center;color:#9e9e9e;padding:30px;">Loading...</div></div>
    </div>'''
new_history = '''    <!-- History -->
    <div id="historyTab" style="display:none;">
      <div id="historyArea"><div style="text-align:center;color:#9e9e9e;padding:30px;">Loading...</div></div>
    </div>

    <!-- Manage Vendors -->
    <div id="manageTab" style="display:none;">
      <div class="card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
          <div class="card-title" style="margin-bottom:0;">Live Vendors</div>
          <input id="vendorSearch" placeholder="Search vendor..." style="border:1.5px solid #e0e0e0;border-radius:8px;padding:8px 12px;font-size:13px;" oninput="filterVendors()"/>
        </div>
        <div id="manageArea"><div style="text-align:center;color:#9e9e9e;padding:20px;">Loading...</div></div>
      </div>
    </div>'''
admin = admin.replace(old_history, new_history)

# Add switchTab manage case and loadVendors function
old_switch = '''function switchTab(tab) {
  [\'changes\',\'vendors\',\'history\'].forEach(t => {
    document.getElementById(t+\'Tab\').style.display = t === tab ? \'block\' : \'none\';
  });
  document.querySelectorAll(\'.tab\').forEach((t, i) => {
    t.classList.toggle(\'active\', [\'changes\',\'vendors\',\'history\'][i] === tab);
  });
}'''
new_switch = '''let allVendors = [];

function switchTab(tab) {
  [\'changes\',\'vendors\',\'manage\',\'history\'].forEach(t => {
    document.getElementById(t+\'Tab\').style.display = t === tab ? \'block\' : \'none\';
  });
  document.querySelectorAll(\'.tab\').forEach((t, i) => {
    t.classList.toggle(\'active\', [\'changes\',\'vendors\',\'manage\',\'history\'][i] === tab);
  });
  if (tab === \'manage\') loadVendors();
}

async function loadVendors() {
  const res = await fetch(\'/vendors\');
  allVendors = await res.json();
  renderVendors(allVendors);
}

function filterVendors() {
  const q = document.getElementById(\'vendorSearch\').value.toLowerCase();
  renderVendors(allVendors.filter(v => (v.Vendor||\'').toLowerCase().includes(q) || (v.City||\'').toLowerCase().includes(q)));
}

function renderVendors(list) {
  const area = document.getElementById(\'manageArea\');
  if (!list.length) { area.innerHTML = \'<div style="text-align:center;color:#9e9e9e;padding:20px;">No vendors found.</div>\'; return; }
  const grouped = {};
  list.forEach(v => { if (!grouped[v.Vendor]) grouped[v.Vendor] = []; grouped[v.Vendor].push(v); });
  area.innerHTML = Object.keys(grouped).sort().map(vendor => `
    <div style="background:#f8faff;border-radius:12px;padding:14px;margin-bottom:10px;border:1.5px solid #e3eaff;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <div style="font-size:14px;font-weight:800;color:#002d62;">${vendor}</div>
        <span style="background:#e8f5e9;color:#2e7d32;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:700;">${grouped[vendor].length} listing(s)</span>
      </div>
      ${grouped[vendor].map(v => `
        <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-top:1px solid #e0e0e0;flex-wrap:wrap;gap:6px;">
          <div style="font-size:12px;color:#424242;">${v.City} | ${v.Make||\'\'} | ${v.Type||\'\'} | ₹${v[\'Approx Rental/Week\']||\'N/A\'}/week</div>
          <button onclick=\'removeVendorEntry(${JSON.stringify(JSON.stringify(v))})\' style="background:#ffebee;color:#c62828;border:none;border-radius:6px;padding:5px 12px;font-size:11px;font-weight:700;cursor:pointer;">Remove</button>
        </div>`).join(\'\')}
    </div>`).join(\'\');
}

async function removeVendorEntry(vStr) {
  const v = JSON.parse(vStr);
  if (!confirm(`Remove ${v.Vendor} - ${v.Make} in ${v.City}?`)) return;
  const res = await fetch(\'/admin/remove-vendor\', {method:\'POST\', headers:{\'Content-Type\':\'application/json\'}, body: JSON.stringify({token: adminToken, vendor: v.Vendor, city: v.City, make: v.Make})});
  const d = await res.json();
  alert(d.msg || (d.ok ? \'Removed\' : \'Error\'));
  if (d.ok) loadVendors();
}'''
admin = admin.replace(old_switch, new_switch)

open('app/static/admin_dashboard.html', 'w', encoding='utf-8').write(admin)
print('admin_dashboard.html fixed:', 'manageTab' in admin)
print('loadVendors added:', 'loadVendors' in admin)
