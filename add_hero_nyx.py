import json

with open('data/vendors.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

surat_evify = next(v for v in data if v.get('Vendor') == 'Evify' and v.get('City') == 'Surat')
vad_evify = next(v for v in data if v.get('Vendor') == 'Evify' and v.get('City') == 'Vadodara')

hero_nyx_surat = {
    "City": "Surat",
    "Vendor": "Evify",
    "Status": "Live",
    "Battery Type": "Home/Store Charging",
    "Make": "Hero NYX",
    "Type": "Hi-Speed",
    "Approx Rental/Week": "1120-1470",
    "Range (Km)": "80",
    "Security Deposit": "2000",
    "Refundable Deposit": "1000",
    "Charging/Swap": "Charging",
    "SPOC": surat_evify.get("SPOC"),
    "Phone": surat_evify.get("Phone"),
    "Email": surat_evify.get("Email"),
    "Image": "/static/images/evify_hero_nyx.jpeg"
}

hero_nyx_vad = {
    "City": "Vadodara",
    "Vendor": "Evify",
    "Status": "Live",
    "Battery Type": "Home/Store Charging",
    "Make": "Hero NYX",
    "Type": "Hi-Speed",
    "Approx Rental/Week": "1120-1470",
    "Range (Km)": "80",
    "Security Deposit": "2000",
    "Refundable Deposit": "1000",
    "Charging/Swap": "Charging",
    "SPOC": vad_evify.get("SPOC"),
    "Phone": vad_evify.get("Phone"),
    "Email": vad_evify.get("Email"),
    "Image": "/static/images/evify_hero_nyx.jpeg"
}

data.append(hero_nyx_surat)
data.append(hero_nyx_vad)

with open('data/vendors.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f'Total entries: {len(data)}')
for v in [hero_nyx_surat, hero_nyx_vad]:
    print(v['City'], '|', v['Make'], '|', v['Approx Rental/Week'], '|', v['Security Deposit'], '|', v['SPOC'])
