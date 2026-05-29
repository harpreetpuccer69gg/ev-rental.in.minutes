f = open('app/static/index.html', encoding='utf-8')
c = f.read()
f.close()

# Replace individual CSS rules precisely
replacements = [
    # Detail page background
    ('background:#f1f3f6;z-index:400;', 'background:#0f172a;z-index:400;'),
    # Detail header
    ('.detail-header{background:#002d62;', '.detail-header{background:linear-gradient(135deg,#002d62,#0f172a);border-bottom:1px solid rgba(255,255,255,0.08);'),
    # Back button
    ('.back-btn{background:none;border:none;color:#ffd600;font-size:22px;', '.back-btn{background:rgba(255,255,255,0.1);border:none;color:#ffd600;font-size:18px;border-radius:8px;'),
    # dmedia-wrap background
    ('background:#f8f9ff;overflow:hidden;border-bottom:1px solid #e0e0e0;display:flex;', 'background:linear-gradient(180deg,#1e3a5f 0%,#0f172a 100%);overflow:hidden;display:flex;'),
    # dmedia-slide background
    ('background:#f8f9ff;flex-shrink:0;overflow:hidden;', 'background:transparent;flex-shrink:0;overflow:hidden;'),
    # dmedia-slide img - add drop shadow
    ('object-position:center center;display:block;margin:0 auto;}', 'object-position:center center;display:block;margin:0 auto;filter:drop-shadow(0 8px 24px rgba(0,0,0,0.5));}'),
    # dmedia-dot color
    ('background:rgba(0,0,0,0.25);border:none;', 'background:rgba(255,255,255,0.3);border:none;'),
    # dmedia-dot active
    ('.dmedia-dot.active{background:#002d62;', '.dmedia-dot.active{background:#ffd600;'),
    # detail-body
    ('.detail-body{max-width:500px;margin:0 auto;padding:16px;}', '.detail-body{max-width:500px;margin:0 auto;padding:16px;background:#0f172a;min-height:60vh;}'),
    # detail-name color
    ('color:#002d62;margin-bottom:6px;line-height:1.2;}', 'color:#fff;margin-bottom:4px;line-height:1.2;}'),
    # detail-item background
    ('background:#fff;border-radius:12px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,0.06);}', 'background:rgba(255,255,255,0.07);border-radius:14px;padding:14px;border:1px solid rgba(255,255,255,0.08);}'),
    # detail-item-label color
    ('color:#9e9e9e;font-weight:600;', 'color:rgba(255,255,255,0.45);font-weight:700;'),
    # detail-item-val color
    ('color:#212121;}', 'color:#fff;}'),
    # detail-price-box
    ('.detail-price-box{background:#002d62;border-radius:14px;padding:16px;', '.detail-price-box{background:linear-gradient(135deg,#002d62,#1a4a8a);border-radius:16px;padding:18px;border:1px solid rgba(255,214,0,0.2);'),
    # detail-price-val size
    ('color:#ffd600;font-size:26px;font-weight:900;}', 'color:#ffd600;font-size:28px;font-weight:900;}'),
    # dpop background
    ('.dpop{background:#fff;border-radius:20px 20px 0 0;', '.dpop{background:#1e293b;border-radius:24px 24px 0 0;border-top:1px solid rgba(255,255,255,0.1);'),
    # dpop-handle color
    ('background:#e0e0e0;border-radius:2px;', 'background:rgba(255,255,255,0.2);border-radius:2px;'),
    # dpop-title color
    ('color:#002d62;margin-bottom:16px;}', 'color:#fff;margin-bottom:16px;}'),
    # detail-book-btn
    ('.detail-book-btn{width:100%;background:#ffd600;', '.detail-book-btn{width:100%;background:linear-gradient(135deg,#ffd600,#ffca00);box-shadow:0 4px 20px rgba(255,214,0,0.35);'),
]

for old, new in replacements:
    if old in c:
        c = c.replace(old, new, 1)
        print(f'OK: {old[:50]}')
    else:
        print(f'MISS: {old[:50]}')

f = open('app/static/index.html', 'w', encoding='utf-8')
f.write(c)
f.close()
print('Done')
