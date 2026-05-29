import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/main.py', encoding='utf-8').read()

# Find a good insertion point
idx = content.find('def health()')
print('health found at:', idx)
print(repr(content[idx-50:idx+100]))
