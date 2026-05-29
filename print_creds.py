import json, sys
with open('credentials.json','r') as f:
    data = json.load(f)
out = json.dumps(data, separators=(',',':'))
print(out)
sys.stdout.flush()
