import os,re,json,html,posixpath,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
SITE='/home/claude/site'; BASE='https://stayhere-eventzentrale-wedel.rmo1303.chatgpt.site'
PAGES=['index.html','haeuser.html','unterkuenfte/stayhere-01.html','unterkuenfte/stayhere-02.html','unterkuenfte/stayhere-03.html','gastgeber.html','wedel-elbe.html','hamburg-tipps.html','events.html','anreise-faq.html']
SEGS=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'segs.json'),encoding='utf-8'))
HERE=os.path.dirname(os.path.abspath(__file__))
M=json.load(open(os.path.join(HERE,'tr_map.json'),encoding='utf-8'))
if os.path.exists(os.path.join(HERE,'tr_extra.json')): M.update(json.load(open(os.path.join(HERE,'tr_extra.json'),encoding='utf-8')))
LI={'en':0,'es':1}
MON={'Januar':('January','enero'),'Februar':('February','febrero'),'März':('March','marzo'),'April':('April','abril'),'Mai':('May','mayo'),'Juni':('June','junio'),'Juli':('July','julio'),'November':('November','noviembre')}
MISSING=set()
FLAGS={
'de':'<svg viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#000"/><rect y="6.67" width="30" height="13.33" fill="#dd0000"/><rect y="13.33" width="30" height="6.67" fill="#ffce00"/></svg>',
'en':'<svg viewBox="0 0 60 40" aria-hidden="true"><rect width="60" height="40" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#C8102E" stroke-width="3"/><path d="M30,0 V40 M0,20 H60" stroke="#fff" stroke-width="13"/><path d="M30,0 V40 M0,20 H60" stroke="#C8102E" stroke-width="7"/></svg>',
'es':'<svg viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#aa151b"/><rect y="5" width="30" height="10" fill="#f1bf00"/></svg>'}
NAMES={'de':'Deutsch','en':'English','es':'Español'}
def loc(lang,path): return path if lang=='de' else lang+'/'+path
def tr(text,lang):
    k=html.unescape(text)
    if k in M: return M[k][LI[lang]]
    m=re.match(r'^Platz für ein Foto: (.*)$',k)
    if m: return ('Space for a photo: ' if lang=='en' else 'Espacio para una foto: ')+tr(m.group(1),lang)
    m=re.match(r'^(Hoch|Quer)format (.*)$',k)
    if m:
        w={'en':{'Hoch':'Portrait','Quer':'Landscape'},'es':{'Hoch':'Vertical','Quer':'Horizontal'}}[lang][m.group(1)]
        return w+' '+m.group(2)
    m=re.match(r'^(\d+)\.(?:–(\d+)\.)? (\w+) (\d{4})$',k)
    if m and m.group(3) in MON:
        d=m.group(1)+('–'+m.group(2) if m.group(2) else ''); mo=MON[m.group(3)][LI[lang]]
        return '%s %s %s'%(d,mo,m.group(4)) if lang=='en' else '%s de %s de %s'%(d,mo,m.group(4))
    if re.match(r'^[\d.,() %]+$',k): return k.replace(',','.') if lang=='en' else k
    if re.search(r'[a-zäöüß]{4,}',k) and not re.match(r'^(stayHere( Wedel)?( 0\d)?|Ruppert Gerhard Matzke|rmo1303@gmail\.com|Airbnb|Wunderflats|HVV|Klövensteen|28grad\.com|Wedel|Blankenese|Landungsbrücken|Elbphilharmonie Plaza|Stadthausbrücke|Speicherstadt|Miniatur Wunderland|Hamburg Dungeon|Jungfernstieg|Westfield Hamburg-Überseequartier|Tickets|Hamburg|Hamburg Messe|INTERNORGA|Haspa Marathon Hamburg|Rothenbaum|Kings of Leon|Barclays Arena|ELBJAZZ|POWERWOLF|Arena am Volkspark|Altona|Reeperbahn|St\. Pauli)$',k):
        MISSING.add(k)
    return k
KEEP={'@type','@context','@id','telephone','email','startDate','endDate','unitCode','eventAttendanceMode','additionalType','postalCode','addressCountry','image','knowsLanguage','inLanguage'}
def trj(o,lang,key=None):
    if isinstance(o,dict):
        d={k:trj(v,lang,k) for k,v in o.items()}
        if o.get('@type') in ('WebSite','FAQPage','VacationRental','ItemList') and '@context' in o: d['inLanguage']=lang
        if 'inLanguage' in o: d['inLanguage']=lang
        return d
    if isinstance(o,list): return [trj(v,lang,key) for v in o]
    if isinstance(o,str):
        if key in KEEP: return o
        if o.startswith(BASE):
            rest=o[len(BASE)+1:]; base,sep,frag=rest.partition('#')
            pth=base or 'index.html'
            return (url(lang,pth)+sep+frag) if (pth in PAGES and key!='@id') else o
        if o.startswith('http'): return o
        return tr(o,lang)
    return o
def langs_html(lang,path):
    here=posixpath.dirname(loc(lang,path)); items=[]
    for l in ('de','en','es'):
        tp=path if (l=='de' or path!='impressum.html') else 'index.html'
        href=posixpath.relpath(loc(l,tp),here or '.')
        items.append('<li><a href="%s" hreflang="%s" lang="%s" aria-label="%s" title="%s"%s>%s</a></li>'%(href,l,l,NAMES[l],NAMES[l],' aria-current="true"' if l==lang else '',FLAGS[l]))
    return '<ul class="langs">%s</ul>'%''.join(items)
def url(lang,path):
    p=loc(lang,path); return BASE+'/'+(p[:-10] if p.endswith('index.html') else p)
def hreflang(path):
    if path=='impressum.html': return ''
    return '\n'.join('<link rel="alternate" hreflang="%s" href="%s">'%(l,url(l,path)) for l in ('de','en','es'))+'\n<link rel="alternate" hreflang="x-default" href="%s">'%url('de',path)
out_pages=[]
for path in PAGES+['impressum.html']:
    src=open(os.path.join(SITE,path),encoding='utf-8').read()
    de=src.replace('<!--HREFLANG-->',hreflang(path)).replace('<!--LANGS-->',langs_html('de',path))
    if path=='impressum.html':
        open(os.path.join(SITE,path),'w',encoding='utf-8').write(de); continue
    for lang in ('en','es'):
        def ldfix(m):
            return '<script type="application/ld+json">'+json.dumps(trj(json.loads(m.group(1)),lang),ensure_ascii=False)+'</script>'
        s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',ldfix,src,flags=re.S)
        LD=[]
        def stash(m): LD.append(m.group(0)); return '<!--LD%d-->'%(len(LD)-1)
        s=re.sub(r'<script type="application/ld\+json">.*?</script>',stash,s,flags=re.S)
        d=posixpath.dirname(path); here=posixpath.dirname(loc(lang,path))
        def fix(m):
            attr,h=m.group(1),m.group(2)
            if h.startswith(('http','mailto:','tel:','#')): return m.group(0)
            pth,sep,frag=h.partition('#')
            root=posixpath.normpath(posixpath.join(d,pth))
            target=root if (root.split('/')[0] in ('css','js','fonts','img') or root=='impressum.html') else lang+'/'+root
            return '%s="%s%s%s"'%(attr,posixpath.relpath(target,here or '.'),sep,frag)
        s=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="%s">'%url(lang,path),s)
        s=re.sub(r'<meta property="og:url" content="[^"]*">','<meta property="og:url" content="%s">'%url(lang,path),s)
        s=s.replace('content="de_DE"','content="%s"'%{'en':'en_GB','es':'es_ES'}[lang]).replace('<html lang="de">','<html lang="%s">'%lang)
        s=re.sub(r'\b(href|src)="([^"]*)"',lambda m: m.group(0) if 'canonical' in m.string[max(0,m.start()-25):m.start()] else fix(m),s)
        def txt(m):
            t=m.group(1); st=t.strip()
            if not st: return m.group(0)
            lead=t[:len(t)-len(t.lstrip())]; trail=t[len(t.rstrip()):]
            return '>'+lead+html.escape(tr(st,lang),quote=False)+trail+'<'
        s=re.sub(r'>([^<>]+)<',txt,s)
        s=re.sub(r'(aria-label|alt)="([^"]*)"',lambda m:'%s="%s"'%(m.group(1),html.escape(tr(m.group(2),lang),quote=True)) if m.group(2) not in NAMES.values() else m.group(0),s)
        s=re.sub(r'(<meta (?:name="description"|property="og:title"|property="og:description") content=")([^"]*)(")',lambda m:m.group(1)+html.escape(tr(m.group(2),lang),quote=True)+m.group(3),s)
        for i,b in enumerate(LD): s=s.replace('<!--LD%d-->'%i,b)
        s=s.replace('<!--HREFLANG-->',hreflang(path)).replace('<!--LANGS-->',langs_html(lang,path))
        full=os.path.join(SITE,loc(lang,path)); os.makedirs(os.path.dirname(full),exist_ok=True)
        open(full,'w',encoding='utf-8').write(s); out_pages.append(loc(lang,path))
    open(os.path.join(SITE,path),'w',encoding='utf-8').write(de)
# Sitemap mit allen Sprachen
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path in PAGES:
    for l in ('de','en','es'): sm.append('  <url><loc>%s</loc><lastmod>2026-11-16</lastmod></url>'%url(l,path))
sm.append('</urlset>'); open(os.path.join(SITE,'sitemap.xml'),'w',encoding='utf-8').write('\n'.join(sm)+'\n')
print(len(out_pages),'übersetzte Seiten; nicht übersetzt:',len(MISSING))
for m in sorted(MISSING): print('  ?',m)
