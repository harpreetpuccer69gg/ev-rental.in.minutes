f = open('app/static/admin_dashboard.html', encoding='utf-8')
c = f.read()
f.close()

# Find the inline script block in head
s = c.find('<script defer>')
e = c.find('</script>', s) + len('</script>')
script_content = c[s+len('<script defer>'):e-len('</script>')]

# Build new script: expose all functions to window so onclick works
new_script = '<script>\n' + script_content + '\n// Expose to global scope for onclick handlers\nwindow.doAdminLogin = doAdminLogin;\nwindow.doLogout = doLogout;\nwindow.togglePwd = togglePwd;\nwindow.switchTab = switchTab;\nwindow.reviewChange = reviewChange;\nwindow.reviewVendor = reviewVendor;\nwindow.removeVendorEntry = removeVendorEntry;\nwindow.openAddVendor = openAddVendor;\nwindow.closeAddVendor = closeAddVendor;\nwindow.submitAddVendor = submitAddVendor;\nwindow.filterVendors = filterVendors;\nwindow.filterHistory = filterHistory;\nwindow.removeFromHistory = removeFromHistory;\n</script>'

final = c[:s] + new_script + c[e:]

f = open('app/static/admin_dashboard.html', 'w', encoding='utf-8')
f.write(final)
f.close()

# Verify
f = open('app/static/admin_dashboard.html', encoding='utf-8')
c2 = f.read()
f.close()
print('window.doAdminLogin present:', 'window.doAdminLogin' in c2)
print('script defer removed:', '<script defer>' not in c2)
print('Done')
