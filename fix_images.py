from rembg import remove
from PIL import Image
import os

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, 'ev image') + os.sep
dst = os.path.join(base, 'app', 'static', 'images') + os.sep

to_process = [
    (src+'YULU DEX GR.avif', dst+'yulu.png'),
    (src+'Bounce.png', dst+'bounce.png'),
    (src+'BGauss C12i max.jpg', dst+'bgauss.png'),
    (src+'Go_green.jpeg', dst+'gogreen.png'),
    (src+'Yugo Rides.jpeg', dst+'yugo.png'),
]

for s, d in to_process:
    if os.path.exists(s):
        print('Processing', os.path.basename(s), '...')
        img = Image.open(s).convert('RGBA')
        result = remove(img)
        result.save(d, 'PNG')
        print('  Saved', os.path.basename(d), 'size='+str(os.path.getsize(d)))
    else:
        print('NOT FOUND:', s)

print('DONE')
