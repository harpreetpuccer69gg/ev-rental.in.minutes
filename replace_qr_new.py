from PIL import Image
import qrcode, os

poster = Image.open(r'ev image/POSTER OF EV.png').convert('RGB')

qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=6, border=1)
qr.add_data('https://ev-rental-in-minutes.onrender.com')
qr.make(fit=True)
qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
qr_img = qr_img.resize((247, 250), Image.LANCZOS)
poster.paste(qr_img, (898, 590))

out = r'app\static\images\fk_poster.png'
if os.path.exists(out):
    os.remove(out)
poster.save(out, 'PNG')
