import json

with open('data/vendors.json', encoding='utf-8') as f:
    data = json.load(f)

for i, v in enumerate(data):
    if v.get('Vendor') == 'Evify' and v.get('City') in ['Surat', 'Vadodara']:
        print(i, v['City'], '|', v['Make'], '|', v['Approx Rental/Week'])
