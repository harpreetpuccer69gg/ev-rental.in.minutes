from PIL import Image

TARGET_W = 800
TARGET_H = 300

posters = [
    ('app/static/images/bounce_poster.png', 'PNG'),
    ('app/static/images/yulu_poster.jpeg', 'JPEG'),
]

for path, fmt in posters:
    img = Image.open(path).convert('RGB')
    ow, oh = img.size
    # Scale to fill target width, crop height to center
    scale = TARGET_W / ow
    new_h = int(oh * scale)
    img = img.resize((TARGET_W, new_h), Image.LANCZOS)
    # Crop vertically to TARGET_H from center
    if new_h > TARGET_H:
        top = (new_h - TARGET_H) // 2
        img = img.crop((0, top, TARGET_W, top + TARGET_H))
    elif new_h < TARGET_H:
        # Pad with background color
        bg = Image.new('RGB', (TARGET_W, TARGET_H), (11, 58, 117))
        bg.paste(img, (0, (TARGET_H - new_h) // 2))
        img = bg
    img.save(path, fmt, quality=92)
    print(f'Saved {path}: {img.size}')
