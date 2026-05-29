import shutil, os, json

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, 'ev image')
dst = os.path.join(base, 'app', 'static', 'images')

# Copy all city images
files = {
    'YULU Bangalore.jpeg': 'yulu_bangalore.jpeg',
    'Yulu Delhi.jpeg':     'yulu_delhi.jpeg',
    'Yulu Mumbai.png':     'yulu_mumbai.png',
    'Yului Hyderabad.png': 'yulu_hyderabad.png',
    'Yulu Kolkata.png':    'yulu_kolkata.png',
    'Yulu Coimbatore.png': 'yulu_coimbatore.png',
    'Yulu Bhopal.png':     'yulu_bhopal.png',
    'Yulu Indore.png':     'yulu_indore.png',
    'Yulu Kochi.png':      'yulu_kochi.png',
    'Yulu Madurai.png':    'yulu_madurai.png',
    'Yulu Vadodra.png':    'yulu_vadodara.png',
    'Yulu Zirakpur.png':   'yulu_zirakpur.png',
}

for s, d in files.items():
    sp = os.path.join(src, s)
    dp = os.path.join(dst, d)
    if os.path.exists(sp):
        shutil.copy2(sp, dp)
        print('Copied:', d, 'size='+str(os.path.getsize(dp)))
    else:
        print('NOT FOUND:', s)

# City -> image mapping
city_image = {
    'Bangalore':   '/static/images/yulu_bangalore.jpeg',
    'Delhi NCR':   '/static/images/yulu_delhi.jpeg',
    'Mumbai':      '/static/images/yulu_mumbai.png',
    'Hyderabad':   '/static/images/yulu_hyderabad.png',
    'Kolkata':     '/static/images/yulu_kolkata.png',
    'COIMBATORE':  '/static/images/yulu_coimbatore.png',
    'Coimbatore':  '/static/images/yulu_coimbatore.png',
    'Bhopal':      '/static/images/yulu_bhopal.png',
    'Indore':      '/static/images/yulu_indore.png',
    'Kochi':       '/static/images/yulu_kochi.png',
    'Madurai':     '/static/images/yulu_madurai.png',
    'Vadodara':    '/static/images/yulu_vadodara.png',
    'Zirakpur':    '/static/images/yulu_zirakpur.png',
}

# New cities to add (not in vendors.json yet)
new_cities = ['Bhopal', 'Indore', 'Kochi', 'Madurai', 'Vadodara', 'Zirakpur']

vendors_path = os.path.join(base, 'data', 'vendors.json')
data = json.load(open(vendors_path, encoding='utf-8'))

# Get a template Yulu entry to copy details from
template = next(v for v in data if v.get('Vendor') == 'Yulu')

# Update existing Yulu entries with city-specific images
for v in data:
    if v.get('Vendor') == 'Yulu':
        city = v.get('City', '')
        if city in city_image:
            v['Image'] = city_image[city]
            print('Updated:', city, '->', city_image[city])

# Add new city entries
existing_cities = [v['City'] for v in data if v.get('Vendor') == 'Yulu']
for city in new_cities:
    if city not in existing_cities:
        new_entry = dict(template)
        new_entry['City'] = city
        new_entry['Image'] = city_image[city]
        new_entry['SPOC'] = None
        new_entry['Phone'] = None
        new_entry['Email'] = None
        data.append(new_entry)
        print('Added new city:', city)

with open(vendors_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print('vendors.json updated')
print('DONE')
