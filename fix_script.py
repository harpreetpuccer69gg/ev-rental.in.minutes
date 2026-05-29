f = open('app/static/admin_dashboard.html', encoding='utf-8')
c = f.read()
f.close()

# Find the script block
s = c.find('<script>')
e = c.find('</script>', s) + len('</script>')
script = c[s:e]
print(f'Script found at {s}-{e}, length {e-s}')

# Find head close
h = c.find('</head>')
print(f'Head closes at {h}')
print(f'Script is after head: {s > h}')

# Move script to head with defer
without = c[:s].rstrip() + '\n' + c[e:].lstrip()
h2 = without.find('</head>')
final = without[:h2] + script.replace('<script>', '<script defer>', 1) + '\n' + without[h2:]

f = open('app/static/admin_dashboard.html', 'w', encoding='utf-8')
f.write(final)
f.close()

# Verify
f = open('app/static/admin_dashboard.html', encoding='utf-8')
c2 = f.read()
f.close()
h3 = c2.find('</head>')
s3 = c2.find('<script defer>')
print(f'After fix - head at {h3}, script defer at {s3}, script before head: {s3 < h3}')
