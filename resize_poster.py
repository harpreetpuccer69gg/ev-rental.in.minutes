from PIL import Image
import os

src = r'app\static\images\yulu_poster.jpeg'
out = r'app\static\images\yulu_poster.jpeg'

img = Image.open(src).convert('RGB')
w, h = img.size
print(f'Original: {w}x{h}')

# Pad vertically to 3:1 ratio with brand blue background
target_h = w // 3  # 1600 // 3 = 533
new_img = Image.new('RGB', (w, target_h), (11, 58, 117))
offset = (target_h - h) // 2
new_img.paste(img, (0, offset))

tmp = r'app\static\images\yulu_tmp.jpeg'
new_img.save(tmp, 'JPEG', quality=92)
print(f'Saved tmp: {os.path.getsize(tmp)} bytes')

os.replace(tmp, out)
print(f'Done: {Image.open(out).size}')
