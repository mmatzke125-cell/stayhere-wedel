import os,re,json,html
from html.parser import HTMLParser
SITE='/home/claude/site'
PAGES=['index.html','haeuser.html','unterkuenfte/stayhere-01.html','unterkuenfte/stayhere-02.html','unterkuenfte/stayhere-03.html','gastgeber.html','wedel-elbe.html','hamburg-tipps.html','events.html','anreise-faq.html','impressum.html']
ATTRS={'aria-label','alt'}
class P(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.skip=0; s.out=[]
    def handle_starttag(s,t,a):
        if t in('script','style'): s.skip+=1
        d=dict(a)
        for k in ATTRS:
            if d.get(k): s.out.append(d[k])
        if t=='meta' and (d.get('name')=='description'): s.out.append(d['content'])
    def handle_endtag(s,t):
        if t in('script','style'): s.skip-=1
    def handle_data(s,data):
        if not s.skip and data.strip(): s.out.append(data.strip())
segs=[]
for p in PAGES:
    q=P(); q.feed(open(os.path.join(SITE,p),encoding='utf-8').read()); segs+=q.out
uniq=list(dict.fromkeys(segs))
json.dump(uniq,open('segs.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(segs),len(uniq),sum(len(x.split()) for x in uniq))
