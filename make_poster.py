import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Settings
URL = 'https://ev-whatsapp-bot-c7sg.onrender.com'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EV_Assist_QR_Poster.png')

W, H = 800, 1100
NAVY = (0, 45, 98)
YELLOW = (255, 214, 0)
WHITE = (255, 255, 255)
LIGHT = (241, 243, 246)

# Create canvas
img = Image.new('RGB', (W, H), NAVY)
draw = ImageDraw.Draw(img)

# Top yellow bar
draw.rectangle([0, 0, W, 12], fill=YELLOW)
draw.rectangle([0, H-12, W, H], fill=YELLOW)

# Try to load logo
logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'images', 'logo.png')
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert('RGBA')
    logo_w = 220
    ratio = logo_w / logo.width
    logo_h = int(logo.height * ratio)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    logo_x = (W - logo_w) // 2
    img.paste(logo, (logo_x, 40), logo)
    title_y = 40 + logo_h + 20
else:
    title_y = 60

# Try fonts
try:
    font_big   = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 42)
    font_med   = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 28)
    font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",   22)
    font_tiny  = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",   18)
except:
    font_big = font_med = font_small = font_tiny = ImageFont.load_default()

# Title
def center_text(draw, text, y, font, color):
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw)//2, y), text, font=font, fill=color)

center_text(draw, 'EV Assist', title_y, font_big, YELLOW)
center_text(draw, 'Flipkart Minutes', title_y + 52, font_med, WHITE)

# Divider
div_y = title_y + 100
draw.rectangle([60, div_y, W-60, div_y+3], fill=YELLOW)

# Tagline
center_text(draw, 'Find & Book EV Rentals', div_y + 20, font_med, WHITE)
center_text(draw, 'for Delivery Riders', div_y + 56, font_med, WHITE)

# Features box
box_y = div_y + 110
draw.rounded_rectangle([50, box_y, W-50, box_y+180], radius=16, fill=(255,255,255,30))
features = [
    '🛵  13 Cities Across India',
    '⚡  40+ EV Vendors',
    '💰  Weekly Budget Filter',
    '🌐  Hindi, Bengali, Kannada & English',
]
for i, feat in enumerate(features):
    center_text(draw, feat, box_y + 18 + i*40, font_small, WHITE)

# QR Code
qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=2)
qr.add_data(URL)
qr.make(fit=True)
qr_img = qr.make_image(fill_color=NAVY, back_color=WHITE).convert('RGB')
qr_size = 280
qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

# White card behind QR
qr_x = (W - qr_size) // 2
qr_y = box_y + 210
draw.rounded_rectangle([qr_x-20, qr_y-20, qr_x+qr_size+20, qr_y+qr_size+20], radius=20, fill=WHITE)
img.paste(qr_img, (qr_x, qr_y))

# Scan text
center_text(draw, 'Scan to Book Your EV Now!', qr_y + qr_size + 30, font_med, YELLOW)

# URL
center_text(draw, URL, qr_y + qr_size + 72, font_tiny, (144, 202, 249))

# Bottom text
center_text(draw, 'Affordable  |  Instant Booking  |  Vendor Support', H - 50, font_tiny, (144, 202, 249))

img.save(OUT, 'PNG', quality=95)
print('Saved:', OUT)
