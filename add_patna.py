with open('app/static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '<option>Mumbai</option>\n      <option>Pune</option>'
new = '<option>Mumbai</option>\n      <option>Patna</option><option>Pune</option>'

count = content.count(old)
print('Replacements to make:', count)
content = content.replace(old, new)
print('Patna occurrences after:', content.count('Patna'))

with open('app/static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
