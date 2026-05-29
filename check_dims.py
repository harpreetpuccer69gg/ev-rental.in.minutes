from PIL import Image

imgs = [
    'app/static/images/bounce_poster.png',
    'app/static/images/yulu_poster.jpeg',
    'app/static/images/fk_poster.png',
]
for p in imgs:
    try:
        img = Image.open(p)
        w, h = img.size
        ratio = round(w/h, 2)
        print(f'{p}: {w}x{h} ratio={ratio}')
    except Exception as e:
        print(f'{p}: ERROR {e}')
