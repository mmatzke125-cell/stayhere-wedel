#!/usr/bin/env python3
"""Macht aus den .html-Adressen saubere Adressen ohne Endung.

Cloudflare Pages liefert haeuser.html unter /haeuser aus und leitet die
.html-Adresse dorthin um. Damit Links, Canonical, hreflang, Sitemap, JSON-LD und
llms.txt ohne Umweg auf die ausgelieferte Adresse zeigen, wird die Endung hier
aus allen Verweisen entfernt. Die Dateien selbst behalten ihren Namen.
"""
import os
import re
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/site"
BASE = "https://stayhere-wedel.de"


def fix_html(s):
    # href="…index.html" -> Verzeichnis
    s = re.sub(r'href="([^"]*?)index\.html(["#])',
               lambda m: 'href="%s%s' % (m.group(1) or "./", m.group(2)), s)
    # href="…seite.html" -> href="…seite"
    s = re.sub(r'href="([^"]*?)\.html(["#])', r'href="\1\2', s)
    # absolute Adressen in JSON-LD und Meta-Angaben
    s = re.sub(re.escape(BASE) + r'(/[^"\s<]*?)\.html', BASE + r'\1', s)
    return s


def fix_text(s):
    return re.sub(re.escape(BASE) + r'(/[^"\s<)]*?)\.html', BASE + r'\1', s)


n = 0
for root, _, files in os.walk(SITE):
    for f in files:
        p = os.path.join(root, f)
        if f.endswith(".html"):
            t = open(p, encoding="utf-8").read()
            u = fix_html(t)
        elif f in ("sitemap.xml", "llms.txt", "robots.txt"):
            t = open(p, encoding="utf-8").read()
            u = fix_text(t)
        else:
            continue
        if u != t:
            open(p, "w", encoding="utf-8").write(u)
            n += 1
print("Adressen bereinigt in %d Dateien" % n)
