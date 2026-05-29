import qrcode
from PIL import Image
import numpy as np
import os

base = os.path.dirname(os.path.abspath(__file__))
poster_src = os.path.join(base, 'ev image', 'POSTER OF EV.png')
out_path   = os.path.join(base, 'EV_Assist_QR_Poster.png')

URL = 'https://ev-whatsapp-bot-c7sg.onrender.com'

poster = Image.open(poster_src).convert('RGB')
W, H = poster.size
print(f'Poster: {W}x{H}')

# Manually set exact QR position based on visual inspection of poster
# Poster is 1181x868, QR is in bottom right corner
qr_x1 = 893
qr_y1 = 580
qr_x2 = 1155
qr_y2 = 840
qr_w  = qr_x2 - qr_x1
qr_h  = qr_y2 - qr_y1
print(f'QR area: ({qr_x1},{qr_y1}) to ({qr_x2},{qr_y2}) = {qr_w}x{qr_h}')

# Generate new QR
qr = qrcode.QRCode(
    version=2,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=1
)
qr.add_data(URL)
qr.make(fit=True)
qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

# Resize exactly to detected area
qr_img = qr_img.resize((qr_w, qr_h), Image.LANCZOS)

# Paste exactly over old QR
poster_rgba = poster.convert('RGBA')
qr_rgba = qr_img.convert('RGBA')
poster_rgba.paste(qr_rgba, (qr_x1, qr_y1))

poster_rgba.convert('RGB').save(out_path, 'PNG')
print(f'Saved: {out_path}')
