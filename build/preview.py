import os,re,base64,posixpath
SITE='/home/claude/site'; OUT='/home/claude/out/stayhere-vorschau.html'
base=['index.html','haeuser.html','unterkuenfte/stayhere-01.html','unterkuenfte/stayhere-02.html','unterkuenfte/stayhere-03.html','gastgeber.html','wedel-elbe.html','hamburg-tipps.html','events.html','anreise-faq.html']
pages=base+['impressum.html']+['en/'+b for b in base]+['es/'+b for b in base]
def view_of(p):
    n=posixpath.basename(p)[:-5]; n='start' if n=='index' else n
    pre=p.split('/')[0]
    return (pre+'-'+n) if pre in ('en','es') else n
css=open(SITE+'/css/site.css',encoding='utf-8').read()
def font(m):
    b=open(SITE+'/fonts/'+m.group(1),'rb').read()
    return 'url("data:font/woff2;base64,%s")'%base64.b64encode(b).decode()
css=re.sub(r'url\("\.\./fonts/([^"]+)"\)',font,css)
css+='\n.view[hidden]{display:none}\n'
views=[]
for p in pages:
    s=open(os.path.join(SITE,p),encoding='utf-8').read()
    body=re.search(r'<body>(.*)</body>',s,re.S).group(1)
    body=re.sub(r'<script[^>]*>.*?</script>','',body,flags=re.S)
    body=re.sub(r'<a class="skip"[^>]*>.*?</a>','',body,flags=re.S)
    cur=view_of(p); d=posixpath.dirname(p)
    def fix(m):
        href=m.group(1)
        if href.startswith(('http','mailto:','tel:')): return m.group(0)
        path,_,frag=href.partition('#')
        v=cur if path=='' else view_of(posixpath.normpath(posixpath.join(d,path)))
        return 'href="#%s"%s'%(v,' data-anchor="%s"'%frag if frag else '')
    body=re.sub(r'href="([^"]*)"',fix,body)
    views.append('<div class="view" data-view="%s" hidden>%s</div>'%(cur,body))
events_js=open(SITE+'/js/events.js',encoding='utf-8').read()
IMG={}
if os.path.isdir(SITE+'/img'):
    for f in sorted(os.listdir(SITE+'/img')):
        IMG[f]='data:image/jpeg;base64,'+base64.b64encode(open(SITE+'/img/'+f,'rb').read()).decode()
import json as _json
views=[re.sub(r'src="(?:\.\./)*img/([^"]+)"',r'data-img="\1"',v) for v in views]
views=[v.replace(' loading="lazy"','') for v in views]
img_js='var IMG='+_json.dumps(IMG)+';[].forEach.call(document.querySelectorAll("img[data-img]"),function(i){i.src=IMG[i.getAttribute("data-img")]||"";});'

js=r"""(function(){
var views=[].slice.call(document.querySelectorAll('.view')),by={},cur=null;
views.forEach(function(v){by[v.getAttribute('data-view')]=v;});
var menus=[].slice.call(document.querySelectorAll('details.menu'));
function closeMenus(except){menus.forEach(function(m){if(m!==except){m.open=false;}});}
menus.forEach(function(m){m.addEventListener('toggle',function(){if(m.open){closeMenus(m);}});});
function fromHash(){var n='';try{n=decodeURIComponent(location.hash.slice(1));}catch(e){}return by[n]?n:'start';}
function langOf(n){return n.indexOf('en-')===0?'en':(n.indexOf('es-')===0?'es':'de');}
function show(n,anchor){if(!by[n]){n='start';}cur=n;var v=by[n];
 views.forEach(function(x){x.hidden=x!==v;});closeMenus();document.documentElement.lang=langOf(n);
 if(anchor){var el=v.querySelector('[id="'+anchor+'"]');
  if(el){var e=el;while(e&&e!==v){if(e.tagName==='DETAILS'){e.open=true;}e=e.parentElement;}el.scrollIntoView();return;}}
 window.scrollTo(0,0);}
document.addEventListener('click',function(e){
 var t=e.target;while(t&&t!==document&&!(t.tagName&&t.tagName.toLowerCase()==='a')){t=t.parentNode;}
 var href=t&&t.getAttribute?t.getAttribute('href'):null;
 if(href&&href.charAt(0)==='#'){e.preventDefault();var n=href.slice(1);
  show(n,t.getAttribute('data-anchor'));
  try{if(location.hash.slice(1)!==cur){location.hash=cur;}}catch(err){}
  return;}
 menus.forEach(function(m){if(m.open&&!m.contains(e.target)){m.open=false;}});});
document.addEventListener('keydown',function(e){if(e.key==='Escape'){closeMenus();}});
window.addEventListener('hashchange',function(){var n=fromHash();if(n!==cur){show(n,null);}});
[].forEach.call(document.querySelectorAll('[data-gmap]'),function(b){b.addEventListener('click',function(){
 var fig=b.closest('.map'),svg=fig.querySelector('.mapsvg'),f=document.createElement('iframe');
 f.src=b.getAttribute('data-gmap');f.title='Google-Karte';f.setAttribute('referrerpolicy','no-referrer');
 if(svg){fig.replaceChild(f,svg);}b.parentNode.parentNode.removeChild(b.parentNode);});});
show(fromHash(),null);
})();"""
doc='<!DOCTYPE html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Ferienwohnungen in Wedel bei Hamburg | stayHere</title>\n<meta name="robots" content="noindex">\n<style>\n%s</style>\n</head>\n<body>\n%s\n<script>\n%s\n%s</script>\n</body>\n</html>\n'%(css,'\n'.join(views),img_js+'\n'+js,events_js)
open(OUT,'w',encoding='utf-8').write(doc); print(len(doc)//1024,'KB')
