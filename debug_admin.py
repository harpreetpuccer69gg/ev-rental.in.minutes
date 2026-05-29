import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/static/admin_dashboard.html', encoding='utf-8').read()

# Find button
idx = content.find('doAdminLogin()')
print('Found at index:', idx)
print('Context:', content[idx-300:idx+50])
