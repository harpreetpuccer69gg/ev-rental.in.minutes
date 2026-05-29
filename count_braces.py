with open('check_js.js', encoding='utf-8') as f:
    content = f.read()

opens = content.count('{')
closes = content.count('}')
print(f'Open braces: {opens}')
print(f'Close braces: {closes}')
print(f'Difference: {opens - closes}')

# Find where balance goes wrong
balance = 0
for i, line in enumerate(content.split('\n'), 1):
    balance += line.count('{') - line.count('}')
    if balance < 0:
        print(f'Balance went negative at line {i}: {repr(line)}')
        break
print(f'Final balance: {balance}')
