import sys
sys.stdout.reconfigure(encoding='utf-8')

content = open('app/main.py', encoding='utf-8').read()
idx = content.find('/admin/pending')
print(content[idx:idx+400])
