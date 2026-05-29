from rembg import remove
from PIL import Image
import os

folder = os.path.join(os.path.dirname(__file__), 'app', 'static', 'images') + os.sep

files_to_convert = [
    ('bgauss.jpg', 'bgauss.png'),
    ('blive.jpeg', 'blive.png'),
    ('emo.jpg', 'emo.png'),
    ('gogreen.jpeg', 'gogreen.png'),
    ('yugo.jpeg', 'yugo.png'),
    ('yulu.avif', 'yulu.png'),
]

pngs = [
    'esprinto.png','freedo.png','nexzu.png','voltup.png','tezzfleet.png',
    'zeway.png','zorro.png','kinetic.png','kinetic2.png','motovolt.png',
    'motovolt2.png','motovolt_m7.png','baaz.png','baaz1.png','bounce.png',
    'yuvwaa.png','maki_ewent.png','speedz.png'
]

print('Starting...')
for src, dst in files_to_convert:
    sp = folder + src
    dp = folder + dst
    if not os.path.exists(sp):
        print(f'SKIP: {src}')
        continue
    print(f'Processing {src}...')
    img = Image.open(sp).convert('RGBA')
    result = remove(img)
    result.save(dp, 'PNG')
    os.remove(sp)
    print(f'  Done -> {dst}')

for name in pngs:
    p = folder + name
    if not os.path.exists(p):
        print(f'SKIP: {name}')
        continue
    print(f'Processing {name}...')
    img = Image.open(p).convert('RGBA')
    result = remove(img)
    result.save(p, 'PNG')
    print(f'  Done -> {name}')

print('ALL COMPLETE')
