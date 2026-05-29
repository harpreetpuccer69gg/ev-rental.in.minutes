f=open('app/static/index.html',encoding='utf-8')
c=f.read()
f.close()
lines=c.split('\n')
out=open('detail_lines.txt','w',encoding='utf-8')
out.write('TOTAL:'+str(len(lines))+'\n')
# CSS around line 185-270
for i in range(184,270):
    out.write(str(i+1)+'|'+lines[i][:150]+'\n')
out.write('---HTML---\n')
# HTML around line 380-430
for i in range(379,440):
    out.write(str(i+1)+'|'+lines[i][:150]+'\n')
out.close()
print('done')
