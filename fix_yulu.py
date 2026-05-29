import json

with open('data/vendors.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_data = []
for v in data:
    if v.get('Vendor') == 'Yulu' and v.get('City') in ['Bangalore', 'Delhi NCR']:
        gr = dict(v)
        gr['Make'] = 'Yulu Dex GR'
        gr['Approx Rental/Week'] = '1364'
        gr['Security Deposit'] = '499'
        gr['Range (Km)'] = '400'
        gr['Image'] = '/static/images/yulu_dex_gr.avif'

        nv = dict(v)
        nv['Make'] = 'Yulu Dex NV'
        nv['Approx Rental/Week'] = '1231'
        nv['Security Deposit'] = '499'
        nv['Range (Km)'] = '400'
        nv['Image'] = '/static/images/yulu_dex_nv.png'

        new_data.append(gr)
        new_data.append(nv)
    else:
        new_data.append(v)

with open('data/vendors.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4, ensure_ascii=False)

print(f'Total entries: {len(new_data)}')
for v in new_data:
    if v.get('Vendor') == 'Yulu' and v.get('City') in ['Bangalore', 'Delhi NCR']:
        print(v['City'], '|', v['Make'], '|', v['Approx Rental/Week'], '|', v['Security Deposit'])
