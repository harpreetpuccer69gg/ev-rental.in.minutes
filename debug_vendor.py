import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/static/vendor_portal.html', encoding='utf-8').read()

# Find openAddModal function
idx = content.find('function openAddModal')
print(content[idx:idx+800])
