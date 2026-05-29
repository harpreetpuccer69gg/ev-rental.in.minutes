with open('app/static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences of Patna
print('Patna occurrences:', content.count('Patna'))

# Find context around Mumbai option
idx = content.find('Mumbai')
print('Context around Mumbai:')
print(repr(content[idx-50:idx+100]))
