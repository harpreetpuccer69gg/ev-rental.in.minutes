import sys
sys.stdout.reconfigure(encoding='utf-8')

admin = open('app/static/admin_dashboard.html', encoding='utf-8').read()

# Add CSS for modal
old_css = '.pending-badge{'
new_css = '''.add-vendor-modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:600;align-items:center;justify-content:center;}
.add-vendor-modal.show{display:flex;}
.add-vendor-box{background:#fff;border-radius:16px;padding:24px;width:92%;max-width:500px;max-height:90vh;overflow-y:auto;}
.av-title{font-size:16px;font-weight:900;color:#002d62;margin-bottom:16px;}
.av-inp{width:100%;border:1.5px solid #e0e0e0;border-radius:10px;padding:11px 14px;font-size:13px;margin-bottom:10px;font-weight:500;}
.av-inp:focus{outline:none;border-color:#002d62;}
.av-label{font-size:12px;font-weight:700;color:#002d62;margin-bottom:3px;display:block;}
.av-btn{width:100%;background:#ffd600;color:#002d62;border:none;border-radius:10px;padding:13px;font-size:14px;font-weight:900;cursor:pointer;margin-top:4px;}
.pending-badge{'''

admin = admin.replace(old_css, new_css)

# Add modal HTML before closing body
old_body = '</body>\n</html>'
new_body = '''<!-- ADD VENDOR MODAL -->
<div class="add-vendor-modal" id="addVendorModal" onclick="closeAddVendor()">
  <div class="add-vendor-box" onclick="event.stopPropagation()">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
      <div class="av-title">Add New EV Listing</div>
      <button onclick="closeAddVendor()" style="background:none;border:none;font-size:20px;cursor:pointer;color:#757575;">✕</button>
    </div>
    <div id="avMsg" style="display:none;padding:10px 14px;border-radius:8px;font-size:13px;font-weight:600;margin-bottom:10px;"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
      <div><span class="av-label">Vendor Name *</span><input class="av-inp" id="avVendor" placeholder="e.g. Bounce"/></div>
      <div><span class="av-label">City *</span><input class="av-inp" id="avCity" placeholder="e.g. Bangalore"/></div>
      <div><span class="av-label">Make / Model *</span><input class="av-inp" id="avMake" placeholder="e.g. Bounce Infinity E1"/></div>
      <div><span class="av-label">Type *</span>
        <select class="av-inp" id="avType">
          <option>Hi-Speed</option><option>Low speed</option><option>E-Cycle</option>
        </select>
      </div>
      <div><span class="av-label">Weekly Rent (₹) *</span><input class="av-inp" id="avRent" placeholder="e.g. 1750"/></div>
      <div><span class="av-label">Range (km)</span><input class="av-inp" id="avRange" placeholder="e.g. 75"/></div>
      <div><span class="av-label">Security Deposit (₹)</span><input class="av-inp" id="avDeposit" placeholder="e.g. 500"/></div>
      <div><span class="av-label">Refundable Deposit (₹)</span><input class="av-inp" id="avRefund" placeholder="e.g. 500"/></div>
      <div><span class="av-label">Charging / Swap</span>
        <select class="av-inp" id="avCharge">
          <option>Charging</option><option>Swap</option>
        </select>
      </div>
      <div><span class="av-label">Status</span>
        <select class="av-inp" id="avStatus">
          <option>Live</option><option>Hidden</option>
        </select>
      </div>
      <div><span class="av-label">SPOC Name</span><input class="av-inp" id="avSpoc" placeholder="Contact person"/></div>
      <div><span class="av-label">SPOC Phone</span><input class="av-inp" id="avSpocPhone" placeholder="Contact number"/></div>
    </div>
    <span class="av-label">Battery Type</span>
    <input class="av-inp" id="avBattery" placeholder="e.g. Swap / Home Charging"/>
    <span class="av-label">Image URL (optional)</span>
    <input class="av-inp" id="avImage" placeholder="/static/images/..."/>
    <button class="av-btn" id="avSubmitBtn" onclick="submitAddVendor()">Add to Live Listings →</button>
  </div>
</div>
</body>
</html>'''

admin = admin.replace(old_body, new_body)

# Add button in manage tab header
old_manage_header = '''        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
          <div class="card-title" style="margin-bottom:0;">Live Vendors</div>
          <input id="vendorSearch" placeholder="Search vendor..." style="border:1.5px solid #e0e0e0;border-radius:8px;padding:8px 12px;font-size:13px;" oninput="filterVendors()"/>
        </div>'''
new_manage_header = '''        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
          <div class="card-title" style="margin-bottom:0;">Live Vendors</div>
          <div style="display:flex;gap:8px;align-items:center;">
            <input id="vendorSearch" placeholder="Search vendor..." style="border:1.5px solid #e0e0e0;border-radius:8px;padding:8px 12px;font-size:13px;" oninput="filterVendors()"/>
            <button onclick="openAddVendor()" style="background:#002d62;color:#ffd600;border:none;border-radius:8px;padding:9px 16px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;">+ Add EV</button>
          </div>
        </div>'''
admin = admin.replace(old_manage_header, new_manage_header)

# Add JS functions before closing script tag
old_script_end = 'function showMsg(id, msg, type) {'
new_script_end = '''function openAddVendor() {
  ['avVendor','avCity','avMake','avRent','avRange','avDeposit','avRefund','avSpoc','avSpocPhone','avBattery','avImage'].forEach(id => {
    const el = document.getElementById(id); if(el) el.value='';
  });
  const msg = document.getElementById('avMsg');
  if(msg){msg.style.display='none';}
  document.getElementById('addVendorModal').classList.add('show');
}

function closeAddVendor() {
  document.getElementById('addVendorModal').classList.remove('show');
}

async function submitAddVendor() {
  const vendor = document.getElementById('avVendor').value.trim();
  const city = document.getElementById('avCity').value.trim();
  const make = document.getElementById('avMake').value.trim();
  const rent = document.getElementById('avRent').value.trim();
  if (!vendor || !city || !make || !rent) {
    showAvMsg('Please fill Vendor, City, Make and Rent fields', 'error'); return;
  }
  const btn = document.getElementById('avSubmitBtn');
  btn.innerText = 'Adding...'; btn.disabled = true;
  const payload = {
    Vendor: vendor, City: city, Make: make,
    Type: document.getElementById('avType').value,
    'Approx Rental/Week': rent,
    'Range (Km)': document.getElementById('avRange').value.trim(),
    'Security Deposit': document.getElementById('avDeposit').value.trim(),
    'Refundable Deposit': document.getElementById('avRefund').value.trim(),
    'Charging/Swap': document.getElementById('avCharge').value,
    'Battery Type': document.getElementById('avBattery').value.trim(),
    Status: document.getElementById('avStatus').value,
    SPOC: document.getElementById('avSpoc').value.trim(),
    Phone: document.getElementById('avSpocPhone').value.trim(),
    Image: document.getElementById('avImage').value.trim() || null,
    Email: null, Refundable_Deposit: null
  };
  const res = await fetch('/admin/add-vendor', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: adminToken, payload})});
  const d = await res.json();
  btn.innerText = 'Add to Live Listings →'; btn.disabled = false;
  if (d.ok) {
    showAvMsg('Added successfully!', 'success');
    setTimeout(() => { closeAddVendor(); loadVendors(); }, 1500);
  } else {
    showAvMsg(d.msg || 'Error adding vendor', 'error');
  }
}

function showAvMsg(msg, type) {
  const el = document.getElementById('avMsg');
  if (!el) return;
  el.innerText = msg;
  el.style.display = 'block';
  el.style.background = type === 'success' ? '#e8f5e9' : '#ffebee';
  el.style.color = type === 'success' ? '#2e7d32' : '#c62828';
}

function showMsg(id, msg, type) {'''

admin = admin.replace(old_script_end, new_script_end)

open('app/static/admin_dashboard.html', 'w', encoding='utf-8').write(admin)
print('Done')
print('addVendorModal:', 'addVendorModal' in admin)
print('submitAddVendor:', 'submitAddVendor' in admin)
