import json

with open('data/vendors.json', encoding='utf-8') as f:
    data = json.load(f)

new_data = []
for v in data:
    # Remove Bgauss Oowah from Surat and Vadodara only
    if v.get('Vendor') == 'Evify' and v.get('City') in ['Surat', 'Vadodara'] and v.get('Make') == 'Bgauss Oowah':
        print('Removed:', v['City'], v['Make'])
        continue
    # Update Hero NYX rent in Surat and Vadodara
    if v.get('Vendor') == 'Evify' and v.get('City') in ['Surat', 'Vadodara'] and v.get('Make') == 'Hero NYX':
        v['Approx Rental/Week'] = '1099-1470'
        print('Updated:', v['City'], v['Make'], '->', v['Approx Rental/Week'])
    new_data.append(v)

with open('data/vendors.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4, ensure_ascii=False)

print('Total entries:', len(new_data))
