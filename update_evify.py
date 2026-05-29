from rembg import remove
from PIL import Image
import os, json

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, 'ev image', 'evify 1.webp')
dst = os.path.join(base, 'app', 'static', 'images', 'evify.png')

# Process image
img = Image.open(src).convert('RGBA')
result = remove(img)
result.save(dst, 'PNG')
print('Evify image saved:', os.path.getsize(dst), 'bytes')

# Update vendors.json
vendors_path = os.path.join(base, 'data', 'vendors.json')
data = json.load(open(vendors_path, encoding='utf-8'))

for v in data:
    if v.get('Vendor') == 'Evify':
        v['Image'] = '/static/images/evify.png'
        print('Updated Evify image for city:', v.get('City'))
    if v.get('Vendor') == 'EcoEV':
        v['Status'] = 'Hidden'
        print('Hidden EcoEV for city:', v.get('City'))

with open(vendors_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print('vendors.json updated')
print('DONE')
