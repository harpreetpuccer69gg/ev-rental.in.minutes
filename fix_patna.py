import json

with open('data/vendors.json', encoding='utf-8') as f:
    data = json.load(f)

filtered = [v for v in data if not (v.get('Vendor') == 'Motovolt' and v.get('City') == 'Patna')]
print(f'Removed {len(data)-len(filtered)} entry. Total: {len(filtered)}')

with open('data/vendors.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=4, ensure_ascii=False)
