with open('check_js.js', encoding='utf-8') as f:
    lines = f.readlines()
print(f'Total lines: {len(lines)}')
for i, l in enumerate(lines[450:], start=451):
    print(f'{i}: {repr(l)}')
