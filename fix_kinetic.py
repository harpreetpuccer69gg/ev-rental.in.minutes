import json

with open('data/vendors.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for v in data:
    if v.get('Vendor') == 'Kinetic Green' and v.get('City') == 'Delhi NCR':
        v['Approx Rental/Week'] = '1775'
        v['Range (Km)'] = '70-80'
        v['Security Deposit'] = '6450'
        v['Refundable Deposit'] = '5450'

with open('data/vendors.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

for v in data:
    if v.get('Vendor') == 'Kinetic Green':
        print(v['City'], '|', v['Approx Rental/Week'], '|', v['Range (Km)'], '|', v['Security Deposit'], '|', v['Refundable Deposit'])
