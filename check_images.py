import struct, os

folder = 'app/static/images'
imgs = ['baaz.png','bgauss.png','bounce.png','esprinto.png','freedo.png',
        'kinetic.png','maki_ewent.png','motovolt.png','motovolt_m7.png',
        'nexzu.png','speedz.png','tezzfleet.png','voltup.png',
        'yulu.png','yuvwaa.png','zeway.png','zorro.png']

for fname in imgs:
    p = os.path.join(folder, fname)
    sz = os.path.getsize(p)
    f = open(p, 'rb')
    f.read(8)
    length = struct.unpack('>I', f.read(4))[0]
    f.read(4)
    data = f.read(length)
    ct = data[9]
    f.close()
    status = 'TRANSPARENT' if ct in (4, 6) else 'HAS-BG'
    print(fname, sz, status)
