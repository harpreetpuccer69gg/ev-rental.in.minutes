import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/static/vendor_portal.html', encoding='utf-8').read()

# Find the image upload section and replace it
old_img = '''    <label>EV Image</label>
    <img id="imgPreview" class="img-preview"/>
    <input type="file" id="fImage" accept="image/*" onchange="previewImage(this)" style="margin-bottom:12px;font-size:13px;"/>
    <input type="hidden" id="fImageUrl"/>
    <input type="hidden" id="fEditMode"/>
    <input type="hidden" id="fOriginalData"/>
    <button class="btn" onclick="submitChange()">Submit for Approval &rarr;</button>'''

new_img = '''    <div style="background:#f8faff;border-radius:10px;padding:14px;margin-bottom:12px;border:1.5px solid #e3eaff;">
      <div style="font-size:13px;font-weight:800;color:#002d62;margin-bottom:8px;">📸 EV Images <span style="color:#c62828;">*</span> (3 required)</div>
      <div style="font-size:11px;color:#757575;margin-bottom:10px;">Recommended: 1200×800px | Max 2MB each | JPG/PNG/WEBP</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
        <div>
          <div style="font-size:11px;font-weight:700;color:#002d62;margin-bottom:4px;">Image 1 <span style="color:#c62828;">*</span></div>
          <label style="display:block;width:100%;height:80px;border:2px dashed #e0e0e0;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#fff;" id="img1Label">
            <img id="imgPreview1" style="width:100%;height:100%;object-fit:cover;display:none;"/>
            <span id="img1Icon" style="font-size:24px;">📷</span>
            <input type="file" id="fImage1" accept="image/jpeg,image/png,image/webp" style="display:none;" onchange="previewImg(this,1)"/>
          </label>
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#002d62;margin-bottom:4px;">Image 2 <span style="color:#c62828;">*</span></div>
          <label style="display:block;width:100%;height:80px;border:2px dashed #e0e0e0;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#fff;" id="img2Label">
            <img id="imgPreview2" style="width:100%;height:100%;object-fit:cover;display:none;"/>
            <span id="img2Icon" style="font-size:24px;">📷</span>
            <input type="file" id="fImage2" accept="image/jpeg,image/png,image/webp" style="display:none;" onchange="previewImg(this,2)"/>
          </label>
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#002d62;margin-bottom:4px;">Image 3 <span style="color:#c62828;">*</span></div>
          <label style="display:block;width:100%;height:80px;border:2px dashed #e0e0e0;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#fff;" id="img3Label">
            <img id="imgPreview3" style="width:100%;height:100%;object-fit:cover;display:none;"/>
            <span id="img3Icon" style="font-size:24px;">📷</span>
            <input type="file" id="fImage3" accept="image/jpeg,image/png,image/webp" style="display:none;" onchange="previewImg(this,3)"/>
          </label>
        </div>
      </div>
      <div id="imgError" style="font-size:11px;color:#c62828;display:none;">Please upload all 3 images</div>
    </div>

    <div style="background:#f8faff;border-radius:10px;padding:14px;margin-bottom:12px;border:1.5px solid #e3eaff;">
      <div style="font-size:13px;font-weight:800;color:#002d62;margin-bottom:4px;">🎥 EV Video <span style="color:#9e9e9e;">(optional)</span></div>
      <div style="font-size:11px;color:#757575;margin-bottom:10px;">Recommended: 1280×720px (HD) | Max 30MB | MP4</div>
      <label style="display:block;width:100%;height:60px;border:2px dashed #e0e0e0;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;background:#fff;gap:8px;" id="videoLabel">
        <span style="font-size:20px;">🎬</span>
        <span id="videoName" style="font-size:12px;color:#757575;">Click to upload video</span>
        <input type="file" id="fVideo" accept="video/mp4" style="display:none;" onchange="previewVideo(this)"/>
      </label>
      <video id="videoPreview" controls style="width:100%;border-radius:8px;margin-top:8px;display:none;max-height:160px;"></video>
    </div>

    <input type="hidden" id="fImageUrl"/>
    <input type="hidden" id="fImageUrl2"/>
    <input type="hidden" id="fImageUrl3"/>
    <input type="hidden" id="fVideoUrl"/>
    <input type="hidden" id="fEditMode"/>
    <input type="hidden" id="fOriginalData"/>
    <button class="btn" onclick="submitChange()">Submit for Approval &rarr;</button>'''

content = content.replace(old_img, new_img)

# Replace previewImage function and submitChange with updated versions
old_preview = '''function previewImage(input) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => { document.getElementById('imgPreview').src = e.target.result; document.getElementById('imgPreview').style.display = 'block'; };
    reader.readAsDataURL(input.files[0]);
  }
}'''

new_preview = '''function previewImg(input, num) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  if (file.size > 2 * 1024 * 1024) { alert('Image ' + num + ' exceeds 2MB limit'); input.value = ''; return; }
  const reader = new FileReader();
  reader.onload = e => {
    const img = document.getElementById('imgPreview' + num);
    const icon = document.getElementById('img' + num + 'Icon');
    img.src = e.target.result;
    img.style.display = 'block';
    icon.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

function previewVideo(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  if (file.size > 30 * 1024 * 1024) { alert('Video exceeds 30MB limit'); input.value = ''; return; }
  const url = URL.createObjectURL(file);
  const vid = document.getElementById('videoPreview');
  vid.src = url; vid.style.display = 'block';
  document.getElementById('videoName').innerText = file.name;
}'''

content = content.replace(old_preview, new_preview)

# Update submitChange to handle 3 images + video
old_submit_img = '''  let imageUrl = document.getElementById('fImageUrl').value;
  const fileInput = document.getElementById('fImage');
  if (fileInput.files && fileInput.files[0]) {
    const fd = new FormData();
    fd.append('token', token);
    fd.append('file', fileInput.files[0]);
    const imgRes = await fetch('/vendor/upload-image', {method:'POST', body: fd});
    const imgData = await imgRes.json();
    if (imgData.ok) imageUrl = imgData.image_url;
  }'''

new_submit_img = '''  // Validate 3 images mandatory
  const img1 = document.getElementById('fImage1');
  const img2 = document.getElementById('fImage2');
  const img3 = document.getElementById('fImage3');
  const existImg1 = document.getElementById('fImageUrl').value;
  const existImg2 = document.getElementById('fImageUrl2').value;
  const existImg3 = document.getElementById('fImageUrl3').value;
  if ((!img1.files || !img1.files[0]) && !existImg1) { document.getElementById('imgError').style.display='block'; btn.innerText='Submit for Approval →'; btn.disabled=false; return; }
  if ((!img2.files || !img2.files[0]) && !existImg2) { document.getElementById('imgError').style.display='block'; btn.innerText='Submit for Approval →'; btn.disabled=false; return; }
  if ((!img3.files || !img3.files[0]) && !existImg3) { document.getElementById('imgError').style.display='block'; btn.innerText='Submit for Approval →'; btn.disabled=false; return; }
  document.getElementById('imgError').style.display='none';

  async function uploadFile(fileInput, existingUrl) {
    if (fileInput.files && fileInput.files[0]) {
      const fd = new FormData();
      fd.append('token', token);
      fd.append('file', fileInput.files[0]);
      const r = await fetch('/vendor/upload-image', {method:'POST', body: fd});
      const d = await r.json();
      return d.ok ? d.image_url : existingUrl;
    }
    return existingUrl;
  }

  const imageUrl = await uploadFile(img1, existImg1);
  const imageUrl2 = await uploadFile(img2, existImg2);
  const imageUrl3 = await uploadFile(img3, existImg3);

  let videoUrl = document.getElementById('fVideoUrl').value;
  const vidInput = document.getElementById('fVideo');
  if (vidInput.files && vidInput.files[0]) {
    const fd = new FormData();
    fd.append('token', token);
    fd.append('file', vidInput.files[0]);
    const r = await fetch('/vendor/upload-image', {method:'POST', body: fd});
    const d = await r.json();
    if (d.ok) videoUrl = d.image_url;
  }'''

content = content.replace(old_submit_img, new_submit_img)

# Update payload to include all images and video
old_payload = "    Image: imageUrl,"
new_payload = "    Image: imageUrl,\n    Image2: imageUrl2,\n    Image3: imageUrl3,\n    Video: videoUrl,"
content = content.replace(old_payload, new_payload)

# Update openAddModal to clear new fields
old_clear = "  document.getElementById('fImageUrl').value = '';\n  document.getElementById('imgPreview').style.display = 'none';"
new_clear = """  document.getElementById('fImageUrl').value = '';
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
  document.getElementById('imgError').style.display='none';"""
content = content.replace(old_clear, new_clear)

# Update openEditModal to populate existing images
old_edit_img = """  document.getElementById('fImageUrl').value = v.Image || '';
  if (v.Image) { document.getElementById('imgPreview').src = v.Image; document.getElementById('imgPreview').style.display = 'block'; }"""
new_edit_img = """  document.getElementById('fImageUrl').value = v.Image || '';
  document.getElementById('fImageUrl2').value = v.Image2 || '';
  document.getElementById('fImageUrl3').value = v.Image3 || '';
  document.getElementById('fVideoUrl').value = v.Video || '';
  [1,2,3].forEach(n => {
    const key = n===1?'Image':('Image'+n);
    const img = document.getElementById('imgPreview'+n);
    const icon = document.getElementById('img'+n+'Icon');
    if (v[key]) { img.src=v[key]; img.style.display='block'; icon.style.display='none'; }
    else { img.style.display='none'; icon.style.display='block'; }
  });
  if (v.Video) { document.getElementById('videoPreview').src=v.Video; document.getElementById('videoPreview').style.display='block'; document.getElementById('videoName').innerText='Video uploaded'; }
  else { document.getElementById('videoPreview').style.display='none'; document.getElementById('videoName').innerText='Click to upload video'; }"""
content = content.replace(old_edit_img, new_edit_img)

open('app/static/vendor_portal.html', 'w', encoding='utf-8').write(content)
print('Done')
print('previewImg added:', 'function previewImg' in content)
print('previewVideo added:', 'function previewVideo' in content)
print('imgError added:', 'imgError' in content)
print('fImage1 added:', 'fImage1' in content)
print('fVideo added:', 'fVideo' in content)
