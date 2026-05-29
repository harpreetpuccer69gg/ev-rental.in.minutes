with open('check_js.js', encoding='utf-8') as f:
    lines = f.readlines()

balance = 0
last_func = ''
for i, line in enumerate(lines, 1):
    if 'function ' in line:
        last_func = f'L{i}: {line.strip()}'
    prev = balance
    balance += line.count('{') - line.count('}')
    if prev == 0 and balance > 0:
        open_func = last_func

with open('out2.txt','w') as f:
    f.write(f'Final balance: {balance}\n')
    f.write(f'Last opened func: {open_func}\n')
