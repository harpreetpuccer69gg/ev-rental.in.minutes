import re, subprocess, sys

with open('app/static/index.html', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
if not scripts:
    print('NO SCRIPT FOUND')
    sys.exit(1)

js = scripts[0]
print(f'JS length: {len(js)} chars')

with open('check_js.js', 'w', encoding='utf-8') as f:
    f.write(js)

result = subprocess.run(['node', '--check', 'check_js.js'], capture_output=True, text=True)
if result.returncode == 0:
    print('JS SYNTAX OK')
else:
    print('JS SYNTAX ERROR:')
    print(result.stderr)
