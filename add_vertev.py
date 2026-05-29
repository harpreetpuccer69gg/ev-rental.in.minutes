import json

with open('data/vendors.json', encoding='utf-8') as f:
    data = json.load(f)

vertev_entries = [
    # 5 Patna entries
    {"City":"Patna","Vendor":"Vertev","Status":"Live","Battery Type":"Home/Store Charging","Make":"Seisha","Type":"Low speed","Approx Rental/Week":"1470","Range (Km)":"70","Security Deposit":"3000","Refundable Deposit":"3000","Charging/Swap":"Charging","SPOC":None,"Phone":None,"Email":None,"Image":"/static/images/vertev_seisha_patna.jpg"},
    {"City":"Patna","Vendor":"Vertev","Status":"Live","Battery Type":"Home/Store Charging","Make":"Hero","Type":"Low speed","Approx Rental/Week":"1470","Range (Km)":"70","Security Deposit":"3000","Refundable Deposit":"3000","Charging/Swap":"Charging","SPOC":None,"Phone":None,"Email":None,"Image":"/static/images/vertev_hero_patna.jpg"},
    {"City":"Patna","Vendor":"Vertev","Status":"Live","Battery Type":"Home/Store Charging","Make":"BGauss","Type":"Hi-Speed","Approx Rental/Week":"1470","Range (Km)":"100-110","Security Deposit":"3000","Refundable Deposit":"3000","Charging/Swap":"Charging","SPOC":None,"Phone":None,"Email":None,"Image":"/static/images/vertev_bgauss_patna.jpeg"},
    {"City":"Patna","Vendor":"Vertev","Status":"Live","Battery Type":"Home/Store Charging","Make":"Stella","Type":"Low speed","Approx Rental/Week":"1470","Range (Km)":"70","Security Deposit":"3000","Refundable Deposit":"3000","Charging/Swap":"Charging","SPOC":None,"Phone":None,"Email":None,"Image":"/static/images/vertev_kolkata.jpg"},
    {"City":"Patna","Vendor":"Vertev","Status":"Live","Battery Type":"Home/Store Charging","Make":"Fdatq","Type":"Low speed","Approx Rental/Week":"1470","Range (Km)":"70","Security Deposit":"3000","Refundable Deposit":"3000","Charging/Swap":"Charging","SPOC":None,"Phone":None,"Email":None,"Image":"/static/images/vertev_bangalore.jpg"},
    # Kolkata entry
    {"City":"Kolkata","Vendor":"Vertev","Status":"Live","Battery Type":"Home/Store Charging","Make":"Stella","Type":"Low speed","Approx Rental/Week":"1470","Range (Km)":"70","Security Deposit":"3000","Refundable Deposit":"3000","Charging/Swap":"Charging","SPOC":None,"Phone":None,"Email":None,"Image":"/static/images/vertev_kolkata.jpg"},
    # Bangalore entry
    {"City":"Bangalore","Vendor":"Vertev","Status":"Live","Battery Type":"Home/Store Charging","Make":"Fdatq","Type":"Low speed","Approx Rental/Week":"1470","Range (Km)":"70","Security Deposit":"2500","Refundable Deposit":"1500","Charging/Swap":"Charging","SPOC":None,"Phone":None,"Email":None,"Image":"/static/images/vertev_bangalore.jpg"},
]

data.extend(vertev_entries)

with open('data/vendors.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f'Total entries: {len(data)}')
for v in vertev_entries:
    print(v['City'], '|', v['Make'], '|', v['Type'], '|', v['Approx Rental/Week'], '|', v['Security Deposit'], '|', v['Refundable Deposit'])
