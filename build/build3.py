#!/usr/bin/env python3
"""stayHere Wedel, dritte Fassung: Inhalte auf eigene Seiten verteilt, Aufklapp-Bereiche, Querverweise.
Fotos: Datei img/<platz>.jpg (oder .webp/.png) nach ASSETS/img legen, dann neu bauen."""
import html
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as old  # Daten und JSON-LD-Helfer der ersten Fassung
import map_render  # zeichnet die Karte von Wedel

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/site"
ASSETS = "/home/claude/assets"
FONTS = os.path.join(ASSETS, "fonts-src/node_modules/@fontsource/jost/files")

BASE, STAND, MAIL, TEL, TEL_SHOW, HVV = old.BASE, old.STAND, old.MAIL, old.TEL, old.TEL_SHOW, old.HVV
A1, A2, A3, W2 = old.AIRBNB_01, old.AIRBNB_02, old.AIRBNB_03, old.WUNDERFLATS_02
url_of, ld, crumbs_ld, rental_ld, places_ld = old.url_of, old.ld, old.crumbs_ld, old.rental_ld, old.places_ld
LASTMOD = "2026-11-16"
H1P, H2P, H3P = "unterkuenfte/stayhere-01.html", "unterkuenfte/stayhere-02.html", "unterkuenfte/stayhere-03.html"

RAIL = [
    ("haeuser.html", "Kapitel 1", "Ankommen", "Die Unterkünfte"),
    ("wedel-elbe.html", "Kapitel 2", "Umsehen", "Wedel und die Elbe"),
    ("hamburg-tipps.html", "Kapitel 3", "Losfahren", "Hamburg, Events, Messen"),
]
PAGES, SHOTS, CUR = [], [], [""]

# stayHere 02 wird nur noch ab einem Monat über Wunderflats vermietet.
FAQ = []
for _q, _a in old.FAQ:
    if _q.startswith("Kann ich länger als einen Monat"):
        _q, _a = ("Wird stayHere 02 auch für einzelne Nächte vermietet?",
                  "Nein. stayHere 02 wird nur noch ab einem Monat vermietet, möbliert über Wunderflats für 1 bis "
                  "6 Monate. Die aktuelle Miete steht im Inserat. Für kürzere Aufenthalte gibt es stayHere 01 "
                  "und stayHere 03.")
    elif _q.startswith("Wie komme ich zur FH"):
        continue
    elif _q.startswith("Wo liegen"):
        _a = _a.replace("stayHere 03 nahe der FH Wedel", "stayHere 03 in einem ruhigen Wohngebiet")
    elif _q.startswith("Wie buche ich"):
        _a = ("stayHere 01 und stayHere 03 buchst du über Airbnb. stayHere 02 mietest du ab einem Monat über "
              "Wunderflats. Dort siehst du jeweils Preise, freie Termine und Bedingungen.")
    FAQ.append((_q, _a))
EVENTS = [e[:6] + ([a for a in e[6] if a != "02"],) + e[7:] for e in old.EVENTS]


# ---------------------------------------------------------------- Bausteine
def ext(href, text, cls=None):
    """Link nach außen. Öffnet einen neuen Tab, sonst führt er in der Vorschau ins Leere."""
    return '<a%s href="%s" target="_blank" rel="noopener">%s</a>' % (
        ' class="%s"' % cls if cls else "", href, text)


def inn(href, text, cls=None):
    return '<a%s href="{R}%s">%s</a>' % (' class="%s"' % cls if cls else "", href, text)


def find_image(slot):
    for e in ("jpg", "jpeg", "webp", "png"):
        p = os.path.join(ASSETS, "img", slot + "." + e)
        if os.path.exists(p):
            return p
    return None


FMT = {"wide": "Querformat 3:2", "tall": "Hochformat 2:3", "portrait": "Hochformat 4:5"}


def ph(slot, desc, fmt="wide", caption=None, eager=False):
    SHOTS.append((CUR[0], slot, desc, FMT[fmt]))
    src = find_image(slot)
    if src:
        os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
        shutil.copy(src, os.path.join(OUT, "img", os.path.basename(src)))
        inner = '<img src="{R}img/%s" alt="%s"%s>' % (
            os.path.basename(src), html.escape(desc, quote=True), "" if eager else ' loading="lazy"')
    else:
        inner = ('<div class="ph-box" role="img" aria-label="Platz für ein Foto: %s">'
                 '<span class="label">Foto folgt</span><strong>%s</strong>'
                 '<span class="ph-meta">%s · img/%s.jpg</span></div>') % (
                     html.escape(desc, quote=True), desc, FMT[fmt], slot)
    cap = '<figcaption class="label">%s</figcaption>' % caption if caption else ""
    return '<figure class="ph %s">%s%s</figure>' % (fmt, inner, cap)


def rail(cur):
    items = []
    for i, (href, k, t, d) in enumerate(RAIL, start=1):
        cls = "is-current" if i == cur else ("is-done" if i < cur else "")
        aria = ' aria-current="step"' if i == cur else ""
        items.append('<li class="%s"><a href="{R}%s"%s><span class="label">%s</span><span class="t">%s</span>'
                     '<span class="d">%s</span></a></li>' % (cls, href, aria, k, t, d))
    return '<nav class="rail" aria-label="Kapitel der Geschichte"><ol>%s</ol></nav>' % "".join(items)


def intro(label, h1, sub=None, cur=0, emblem=None, with_rail=True):
    kicker = " kicker" if label.startswith("Kapitel") else ""
    return ('<section class="intro"><div class="wrap">%s%s<h1>%s</h1>%s%s</div></section>' % (
        '<p class="emblem num" aria-hidden="true">%s</p>' % emblem if emblem else "",
        '<p class="label%s">%s</p>' % (kicker, label) if label else "", h1, '<p class="sub">%s</p>' % sub if sub else "", rail(cur) if with_rail else ""))


def railsec(cur):
    return '<section class="intro railonly"><div class="wrap">%s</div></section>' % rail(cur)


def hero(slot, desc):
    return '<section class="hero"><div class="wrap">%s</div></section>' % ph(slot, desc, "wide", eager=True)


def duo(label, statement, body):
    return ('<div class="duo"><div class="duo-head"><h2 class="label">%s</h2><p class="statement">%s</p></div>'
            '<div class="prose">%s</div></div>' % (label, statement, body))


def lines(rows):
    return '<dl class="lines num">%s</dl>' % "".join(
        '<div><dt class="label">%s</dt><dd>%s</dd></div>' % (k, v) for k, v in rows)


GQ = {"01": "Moorwegsiedlung, Wedel", "02": "S-Bahnhof Wedel", "03": "Feldstraße, Wedel",
      None: "Supermarkt Wedel"}


def karte(active=None):
    """Karte mit den drei Umkreisen. active hebt eine Unterkunft hervor."""
    q = GQ[active].replace(" ", "+").replace("ä", "%C3%A4").replace("ö", "%C3%B6").replace("ü", "%C3%BC").replace("ß", "%C3%9F")
    embed = "https://maps.google.com/maps?q=%s&z=14&output=embed" % q
    link = "https://www.google.com/maps/search/?api=1&query=%s" % q
    return map_render.map_figure(active, embed) + (
        '<p class="links">%s</p>' % ext(link, "Dieselbe Stelle in Google Maps öffnen"))


def ul(items):
    return '<ul class="dash">%s</ul>' % "".join("<li>%s</li>" % i for i in items)


def acc(items):
    """Aufklapp-Bereiche. Der Inhalt steht vollständig im HTML und ist nur zugeklappt."""
    out = []
    for it in items:
        ident = ' id="%s"' % it[2] if len(it) > 2 and it[2] else ""
        out.append('<details%s><summary><h3>%s</h3></summary><div class="acc-body">%s</div></details>' % (
            ident, it[0], it[1]))
    return '<div class="acc">%s</div>' % "".join(out)


def section(inner, cls="", ident=None):
    return '<section%s class="%s"><div class="wrap">%s</div></section>' % (
        ' id="%s"' % ident if ident else "", cls, inner)


def head(label, statement=None, tight=False):
    return '<div class="chapter-head"%s><h2 class="label">%s</h2>%s</div>' % (
        ' style="margin-bottom:1.25rem"' if tight else "", label,
        '<p class="statement">%s</p>' % statement if statement else "")


def nextchap(kicker, href, title, others=None):
    o = ""
    if others:
        o = '<ul class="others">%s</ul>' % "".join('<li>%s</li>' % inn(h, t) for h, t in others)
    return ('<section class="next"><div class="wrap"><p class="label">%s</p>%s%s</div></section>' % (
        kicker, inn(href, title, "big"), o))


S1 = """<ol class="s1" aria-label="Wichtige Halte der S1 ab Wedel">
<li class="start"><strong>Wedel</strong><span>Endstation, hier steigst du ein</span></li>
<li><strong>Blankenese</strong><span>Treppenviertel, Elbstrand</span></li>
<li><strong>Altona</strong><span>Ottensen, Umstieg zu anderen S-Bahnen</span></li>
<li><strong>Reeperbahn</strong><span>St. Pauli</span></li>
<li><strong>Landungsbrücken</strong><span>Hafen, Fähren, U3 zur Elbphilharmonie</span></li>
<li><strong>Stadthausbrücke</strong><span>Speicherstadt, Miniatur Wunderland</span></li>
<li><strong>Jungfernstieg</strong><span>Alster, Innenstadt, U4 zur HafenCity</span></li>
<li><strong>Hauptbahnhof</strong><span>Fernzüge; die S1 fährt weiter zum Flughafen</span></li>
</ol>"""

REV = {
    "01": dict(score="4,88", count=191, url=A1, page=H1P, extra=" 92 % der Bewertungen haben 5 Sterne.",
               praised="Gastfreundschaft, Lage, Einrichtung und Sauberkeit",
               cats=[("Sauberkeit", "4,8"), ("Genauigkeit der Angaben", "4,9"), ("Check-in", "4,9"),
                     ("Kommunikation", "4,9"), ("Lage", "4,8"), ("Preis-Leistung", "4,8")], quotes=[]),
    "02": dict(score="4,83", count=90, url=A2, page=H2P, extra="",
               praised="Gastfreundschaft, Lage, Anbindung und Ruhe",
               cats=[("Sauberkeit", "4,7"), ("Genauigkeit der Angaben", "4,8"), ("Check-in", "4,9"),
                     ("Kommunikation", "4,9"), ("Lage", "4,8"), ("Preis-Leistung", "4,7")], quotes=[]),
    "03": dict(score="5,0", count=11, url=A3, page=H3P, extra="",
               praised="Gastfreundschaft, Sauberkeit und Aufenthalte mit der Familie",
               cats=[("Sauberkeit", "4,7"), ("Genauigkeit der Angaben", "4,9"), ("Check-in", "5,0"),
                     ("Kommunikation", "4,9"), ("Lage", "4,7"), ("Preis-Leistung", "4,9")], quotes=[]),
}


def cats_html(num):
    return '<ul class="cats num">%s</ul>' % "".join(
        '<li><span>%s</span><span>%s</span></li>' % c for c in REV[num]["cats"])


def quotes_html(num):
    """Gästezitate erscheinen hier, sobald sie in REV[num]['quotes'] stehen: (Text, Vorname, Monat Jahr)."""
    return "".join('<blockquote><p class="statement">%s</p><p class="label">%s, %s</p></blockquote>' % q
                   for q in REV[num]["quotes"])


def review_body(num, link_host=True):
    r = REV[num]
    more = '<p class="links">%s%s</p>' % (
        ext(r["url"], "Alle %d Bewertungen auf Airbnb lesen" % r["count"]),
        inn("gastgeber.html", "Gastgeber und alle Unterkünfte") if link_host else inn(r["page"], "Zur Unterkunft"))
    return ('<p class="num">%s von 5 Sternen bei %d Bewertungen auf Airbnb. Gäste loben am häufigsten: %s.%s</p>'
            '%s%s%s<p class="muted small">Quelle: Airbnb, Stand %s.</p>' % (
                r["score"], r["count"], r["praised"], r["extra"], cats_html(num), quotes_html(num), more, STAND))


def book_lines():
    return lines([
        ("stayHere 01", "Souterrainwohnung für 4 Gäste. " + ext(A1, "Preise und freie Termine auf Airbnb")),
        ("stayHere 02", "Wohnung für 3 Gäste, Vermietung nur ab einem Monat. " +
         ext(W2, "Miete und freie Zeiträume auf Wunderflats")),
        ("stayHere 03", "Reihenhaus für 6 Gäste. " + ext(A3, "Preise und freie Termine auf Airbnb")),
        ("Fragen", '<a href="mailto:%s">%s</a> oder <a href="tel:%s">%s</a>' % (MAIL, MAIL, TEL, TEL_SHOW)),
    ])


def contact_small():
    return '<p class="muted small">Fragen vorab: <a href="mailto:%s">%s</a> oder <a href="tel:%s">%s</a></p>' % (
        MAIL, MAIL, TEL, TEL_SHOW)


# ---------------------------------------------------------------- Seitenrahmen
def menu(title, items, active, extra_cls=""):
    lis = "".join('<li><a href="%s"%s>%s%s</a></li>' % (
        href, ' rel="noopener"' if href.startswith("http") else "", name,
        "<span>%s</span>" % sub if sub else "") for href, name, sub in items)
    return ('<details class="menu %s" name="hauptmenue"><summary class="label%s">%s</summary>'
            '<ul class="menu-panel">%s</ul></details>' % (extra_cls, " is-active" if active else "", title, lis))


def page(path, title, desc, body, jsonld=(), active=None, robots="index,follow,max-image-preview:large",
         scripts=(), in_sitemap=True):
    root = "../" * path.count("/")
    r = lambda p: root + p
    nav = "".join([
        "<li>%s</li>" % menu("Unterkünfte", [
            (r("haeuser.html"), "Alle drei Unterkünfte im Überblick", None),
            (r(H1P), "stayHere 01", "Souterrainwohnung am Wald, bis 4 Gäste"),
            (r(H2P), "stayHere 02", "Wohnung nahe der S-Bahn, ab einem Monat"),
            (r(H3P), "stayHere 03", "Reihenhaus mit Garten, bis 6 Gäste"),
            (r("gastgeber.html"), "Gastgeber und Bewertungen", None)], active == "haeuser"),
        '<li><a class="label" href="%s"%s>Wedel &amp; Elbe</a></li>' % (
            r("wedel-elbe.html"), ' aria-current="page"' if active == "wedel" else ""),
        "<li>%s</li>" % menu("Hamburg", [
            (r("hamburg-tipps.html"), "Tipps entlang der S1", None),
            (r("events.html"), "Events und Messen 2027", None)], active == "hamburg"),
        '<li><a class="label" href="%s"%s>Anreise &amp; FAQ</a></li>' % (
            r("anreise-faq.html"), ' aria-current="page"' if active == "anreise" else ""),
    ])
    book = menu("Buchen", [
        (A1, "stayHere 01 auf Airbnb", "bis 4 Gäste"),
        (W2, "stayHere 02 auf Wunderflats", "ab einem Monat"),
        (A3, "stayHere 03 auf Airbnb", "bis 6 Gäste")], False, "menu-book")
    head_ld = "\n".join(ld(o) for o in jsonld)
    script_tags = "\n".join('<script src="%s%s" defer></script>' % (root, s) for s in ("js/site.js",) + tuple(scripts))
    doc = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="robots" content="%(robots)s">
<link rel="canonical" href="%(url)s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="stayHere Wedel">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(base)s/stayhere-hero.jpg">
<meta name="theme-color" content="#ffffff">
<!--HREFLANG-->
<link rel="stylesheet" href="%(root)scss/site.css">
%(head_ld)s
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="%(root)sindex.html">stayHere<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="4.6" r="2"/><path d="M12 6.6V21M8.2 10.4h7.6M4.8 14.2a7.2 7.2 0 0 0 14.4 0"/></svg></a>
<nav aria-label="Hauptnavigation"><ul class="nav">%(nav)s</ul></nav>
<div class="tools"><!--LANGS-->%(book)s</div>
</div>
</header>
<main id="inhalt">
%(body)s
</main>
<footer class="site-footer">
<div class="wrap">
<div>
<p class="label">stayHere Wedel</p>
<p>Drei privat geführte Unterkünfte in 22880 Wedel, Schleswig-Holstein, an der Elbe westlich von Hamburg.</p>
</div>
<div>
<p class="label">Kontakt</p>
<ul>
<li>Ruppert Gerhard Matzke</li>
<li><a href="mailto:%(mail)s">%(mail)s</a></li>
<li><a href="tel:%(tel)s">%(tel_show)s</a></li>
<li>Deutsch, Englisch, Spanisch</li>
</ul>
</div>
<div>
<p class="label">Die Geschichte</p>
<ul>
<li><a href="%(root)shaeuser.html">Kapitel 1: Die Unterkünfte</a></li>
<li><a href="%(root)swedel-elbe.html">Kapitel 2: Wedel und die Elbe</a></li>
<li><a href="%(root)shamburg-tipps.html">Kapitel 3: Hamburg</a></li>
<li><a href="%(root)sevents.html">Events und Messen</a></li>
</ul>
</div>
<div>
<p class="label">Praktisches</p>
<ul>
<li><a href="%(root)sgastgeber.html">Gastgeber und Bewertungen</a></li>
<li><a href="%(root)sanreise-faq.html">Anreise und häufige Fragen</a></li>
<li><a href="%(root)sanreise-faq.html#buchen">Buchen</a></li>
<li><a href="%(root)simpressum.html">Impressum und Datenschutz</a></li>
</ul>
</div>
<p class="fine">Angaben zu Ausstattung, Wegen und Bewertungen laut den Inseraten, Stand %(stand)s. Preise und freie Termine stehen auf der jeweiligen Buchungsplattform.</p>
</div>
</footer>
%(scripts)s
</body>
</html>
""" % dict(title=title, desc=html.escape(desc, quote=True), robots=robots, url=url_of(path), base=BASE, root=root,
           head_ld=head_ld, nav=nav, book=book, body=body.replace("{R}", root), mail=MAIL, tel=TEL,
           tel_show=TEL_SHOW, stand=STAND, scripts=script_tags)
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(doc)
    if in_sitemap:
        PAGES.append(path)


def event_rows(events):
    rows = []
    for start, end, datetext, name, kind, place, accs, url, hint in events:
        acc_links = ", ".join(inn("unterkuenfte/stayhere-%s.html" % a, "stayHere %s" % a) for a in accs)
        rows.append(
            '<li class="event" data-kind="%s"><p class="date num"><time datetime="%s">%s</time>'
            '<span class="label">%s</span></p><div class="body"><h3>%s</h3><p class="muted">%s</p>%s'
            '<p class="small">Passende Unterkünfte: %s</p><p class="links small">%s</p></div></li>' % (
                kind, start, datetext, kind, html.escape(name), place,
                "<p>%s</p>" % hint if hint else "", acc_links, ext(url, "Zur Seite des Veranstalters")))
    return "\n".join(rows)


def feature(figure, label, title, text, extra="", kicker=False, htag="h2", ident=None):
    return ('<article class="feature"%s>%s<div class="text"><p class="label%s">%s</p><%s class="statement">%s</%s>'
            '%s%s</div></article>' % (' id="%s"' % ident if ident else "", figure, " kicker" if kicker else "",
                                      label, htag, title, htag, text, extra))


# ---------------------------------------------------------------- Startseite
def build_index():
    CUR[0] = "Startseite"
    chapters = (
        feature(ph("start-kapitel-1", "Das schönste Zimmer einer der Unterkünfte", "portrait"),
                "Kapitel 1 · Ankommen", "Drei Unterkünfte in Wedel, für 3, 4 und 6 Gäste.",
                "<p>Eine Wohnung nahe der S-Bahn, eine Souterrainwohnung am Waldrand und ein Reihenhaus mit "
                "Garten.</p>",
                '<p class="links">%s%s%s</p><p class="actions">%s</p>' % (
                    inn(H1P, "stayHere 01"), inn(H2P, "stayHere 02"), inn(H3P, "stayHere 03"),
                    inn("haeuser.html", "Die Unterkünfte ansehen", "btn label")), kicker=True) +
        feature(ph("start-kapitel-2", "Elbdeich in der Wedeler Marsch", "portrait"),
                "Kapitel 2 · Umsehen",
                "Vor der Tür liegen ein Fluss mit großen Schiffen, ein Deich mit weitem Blick und ein Wald.",
                "<p>Willkomm-Höft, Elbdeich, Wedeler Marsch, Yachthafen und Klövensteen.</p>",
                '<p class="actions">%s</p>' % inn("wedel-elbe.html", "Wedel und die Elbe", "btn label"),
                kicker=True) +
        feature(ph("start-kapitel-3", "Landungsbrücken oder Speicherstadt", "portrait"),
                "Kapitel 3 · Losfahren",
                "In Wedel steigst du an der Endstation ein. Die S1 bringt dich ohne Umsteigen an den Hafen "
                "und in die Innenstadt.",
                "<p>Tipps entlang der Linie, dazu Messen, Konzerte und der Hafengeburtstag 2027.</p>",
                '<p class="actions">%s%s</p>' % (inn("hamburg-tipps.html", "Hamburg mit der S1", "btn label"),
                                                 inn("events.html", "Events und Messen 2027")), kicker=True))
    body = intro(
        "22880 Wedel · Schleswig-Holstein · Endstation der S1",
        "Ferienwohnungen in Wedel bei Hamburg",
        with_rail=False) + hero("start-hero", "Elbe bei Wedel oder das schönste Zimmer") + (
        '<section class="intro railonly"><div class="wrap"><p class="sub">Drei Unterkünfte zwischen Elbe und '
        'Wald, und eine S-Bahn, die ohne Umsteigen nach Hamburg fährt.</p>' + rail(0) + "</div></section>") + section(
        '<div class="stack">' + chapters + "</div>") + section(
        duo("Die Idee",
            "Ruhig wohnen am Rand von Hamburg, zwischen Elbe und Wald, und trotzdem in einem Zug in der Stadt sein.",
            "<p>stayHere sind drei privat geführte Unterkünfte in Wedel: eine Souterrainwohnung für 4 Gäste am "
            "Waldrand, ein Reihenhaus für 6 Gäste mit Garten und eine Wohnung für 3 Gäste nahe der S-Bahn. "
            "Alle haben eine eigene Küche und einen kostenlosen Parkplatz. Die Souterrainwohnung und das "
            "Reihenhaus buchst du auch für einzelne Nächte. Die Wohnung nahe der S-Bahn wird ab einem Monat "
            "vermietet.</p>"
            "<p>Diese Seite erzählt deinen Aufenthalt in drei Kapiteln. Du kommst in der Unterkunft an, siehst dich in "
            "Wedel und an der Elbe um und fährst mit der S1 nach Hamburg.</p>"), "rule") + section(
        head("Gut zu wissen", tight=True) + lines([
            ("Gastgeber", "Superhost auf Airbnb, seit 10 Jahren Gastgeber. " +
             inn("gastgeber.html", "Gastgeber und Bewertungen")),
            ("Anreise", "Mit der S1 ab Hamburg Hauptbahnhof und Flughafen, Parkplatz an jeder Unterkunft. " +
             inn("anreise-faq.html", "Anreise und häufige Fragen")),
            ("Vergleich", "Gäste, Betten, Wege und Parken in einer Tabelle. " +
             inn("haeuser.html#vergleich", "Die drei Unterkünfte im Vergleich")),
            ("Buchen", "Preise und freie Termine stehen im Inserat. " +
             inn("anreise-faq.html#buchen", "Alle Buchungswege")),
        ]), "rule")
    business = {
        "@context": "https://schema.org", "@type": "LodgingBusiness", "@id": BASE + "/#stayhere",
        "name": "stayHere Wedel",
        "description": "Drei privat geführte Ferienunterkünfte in Wedel bei Hamburg für 3, 4 und 6 Gäste, "
                       "nahe S-Bahn S1, Elbe und Klövensteen.",
        "url": BASE + "/", "image": BASE + "/stayhere-hero.jpg", "telephone": TEL_SHOW, "email": MAIL,
        "address": old.ADDRESS, "knowsLanguage": ["de", "en", "es"],
        "founder": {"@type": "Person", "name": "Ruppert Gerhard Matzke"},
        "sameAs": [A1, A3, W2],
    }
    website = {"@context": "https://schema.org", "@type": "WebSite", "name": "stayHere Wedel", "url": BASE + "/",
               "inLanguage": "de"}
    page("index.html", "Ferienwohnungen in Wedel bei Hamburg | stayHere",
         "Drei Ferienunterkünfte in Wedel bei Hamburg für 3, 4 und 6 Gäste: nahe S-Bahn S1, Elbe und "
         "Klövensteen, mit Küche und kostenlosem Parkplatz.",
         body, jsonld=[business, website])


# ---------------------------------------------------------------- Kapitel 1: Übersicht
COMPARE = """<div class="table-scroll">
<table>
<thead>
<tr><th scope="col"></th><th scope="col">stayHere 01</th><th scope="col">stayHere 02</th><th scope="col">stayHere 03</th></tr>
</thead>
<tbody class="num">
<tr><th scope="row" class="label">Art</th><td>Souterrainwohnung</td><td>2-Zimmer-Wohnung, 50 m²</td><td>Reihenhaus</td></tr>
<tr><th scope="row" class="label">Gäste</th><td>bis 4</td><td>bis 3</td><td>bis 6</td></tr>
<tr><th scope="row" class="label">Schlafzimmer</th><td>2</td><td>1</td><td>4</td></tr>
<tr><th scope="row" class="label">Betten</th><td>3 Einzelbetten, 1 kleines Doppelbett</td><td>1 Doppelbett, 1 Einzelbett im Wohnzimmer</td><td>2 Doppelbetten, 4 Einzelbetten</td></tr>
<tr><th scope="row" class="label">Bäder</th><td>1</td><td>1</td><td>1,5</td></tr>
<tr><th scope="row" class="label">Lage in Wedel</th><td>Waldrand am Klövensteen</td><td>Zentrum, nahe der Elbe</td><td>Ruhiges Wohngebiet</td></tr>
<tr><th scope="row" class="label">Zum S-Bahnhof</th><td>Weg ab der Adresse im HVV planen; Abholung bei später Ankunft möglich</td><td>ca. 5 Minuten zu Fuß</td><td>ca. 12 Minuten mit dem Bus</td></tr>
<tr><th scope="row" class="label">Parken</th><td>kostenlos auf dem Grundstück</td><td>kostenloser Stellplatz</td><td>1 reservierter Stellplatz am Haus</td></tr>
<tr><th scope="row" class="label">Draußen</th><td>Wald nebenan</td><td>Südbalkon, Gemeinschaftsgarten, Grillplatz</td><td>eigener Garten</td></tr>
<tr><th scope="row" class="label">Besonderheit</th><td>Großer Fernseher, Billard, Darts</td><td>Aufzug, weitgehend stufenlos</td><td>4 Schlafzimmer, Waschmaschine</td></tr>
<tr><th scope="row" class="label">Vermietung</th><td>ab einzelnen Nächten, Airbnb</td><td>nur ab einem Monat, Wunderflats</td><td>ab einzelnen Nächten, Airbnb</td></tr>
<tr><th scope="row" class="label">Airbnb-Bewertung</th><td>4,88 (191)</td><td>4,83 (90)</td><td>5,0 (11)</td></tr>
</tbody>
</table>
</div>
<p class="muted small">Alle Angaben laut den Inseraten auf Airbnb und Wunderflats, Stand """ + STAND + """.</p>"""


def build_haeuser():
    CUR[0] = "Unterkünfte"
    path = "haeuser.html"
    feats = [
        ("01", H1P, "haeuser-01", "stayHere 01: Wohnbereich mit Billardtisch", "stayHere 01 · bis 4 Gäste",
         "Kinoabend am Klövensteen",
         "Eine Souterrainwohnung mit eigenem Eingang am Waldrand. Zwei Schlafzimmer, ein 65-Zoll-Fernseher, "
         "Darts und ein Billardtisch.",
         ["2 Schlafzimmer, 4 Betten, 1 Bad", "Kostenloser Parkplatz auf dem Grundstück",
          "Airbnb: 4,88 von 5 bei 191 Bewertungen"], A1),
        ("02", H2P, "haeuser-02", "stayHere 02: Südbalkon", "stayHere 02 · bis 3 Gäste · ab einem Monat",
         "Südbalkon und Aufzug",
         "Eine helle Wohnung mit 50 m² im Zentrum, im 3. Stock mit Aufzug. Zum S-Bahnhof gehst du etwa "
         "5 Minuten. Vermietung nur ab einem Monat.",
         ["1 Schlafzimmer, 2 Betten, 1 Bad", "Kostenloser Stellplatz",
          "Airbnb: 4,83 von 5 bei 90 Bewertungen"], W2),
        ("03", H3P, "haeuser-03", "stayHere 03: Garten und Haus", "stayHere 03 · bis 6 Gäste",
         "Reihenhaus mit Garten",
         "Ein ruhiges Reihenhaus mit vier Schlafzimmern und eigenem Garten in einem Wohngebiet von Wedel.",
         ["4 Schlafzimmer, 6 Betten, 1,5 Bäder", "Reservierter Stellplatz am Haus",
          "Airbnb: 5,0 von 5 bei 11 Bewertungen"], A3),
    ]
    feat_html = "".join(
        feature(ph(slot, sdesc, "portrait"), tag, inn(hp, name), "<p>%s</p>" % text,
                '<ul class="num plain">%s</ul><p class="actions">%s%s</p>' % (
                    "".join("<li>%s</li>" % x for x in facts), inn(hp, "Unterkunft ansehen", "btn label"),
                    ext(air, "Auf Wunderflats prüfen" if num == "02" else "Auf Airbnb prüfen")))
        for num, hp, slot, sdesc, tag, name, text, facts, air in feats)
    which = acc([
        ("Familie oder Gruppe bis 6 Personen",
         "<p>%s hat 4 Schlafzimmer, 1,5 Bäder, eine Waschmaschine und einen eigenen Garten.</p>"
         % inn(H3P, "stayHere 03")),
        ("Ruhe am Wald und ein Abend mit Billard",
         "<p>%s liegt am Waldrand des Klövensteen und hat einen 65-Zoll-Fernseher, Darts und einen "
         "Billardtisch. Der Billardtisch steht im Winter nicht zur Verfügung.</p>" % inn(H1P, "stayHere 01")),
        ("Wohnen auf Zeit ab einem Monat",
         "<p>%s kannst du über Wunderflats für 1 bis 6 Monate mieten, zum Beispiel für ein Projekt, ein "
         "Praktikum oder die Zeit zwischen zwei Wohnungen. Zum S-Bahnhof Wedel gehst du etwa 5 Minuten, ein "
         "Auto brauchst du nicht.</p>" % inn(H2P + "#langzeit", "stayHere 02")),
        ("Alle drei Unterkünfte im Vergleich (Tabelle)", COMPARE, "vergleich"),
    ])
    body = intro("Kapitel 1 · Ankommen", "Die drei Unterkünfte in Wedel",
                 "Eine Wohnung im Zentrum, eine am Waldrand und ein Reihenhaus mit Garten. Die genaue Adresse "
                 "bekommst du nach der Buchung.", cur=1) + section(
        '<div class="stack">' + feat_html + "</div>") + section(
        head("Lage", "Wo die drei Unterkünfte liegen, und was in der Nähe ist.") + karte() + lines([
            ("stayHere 01", "Moorwegsiedlung, am Rand des Klövensteen"),
            ("stayHere 02", "Zentrum, etwa 5 Gehminuten zum S-Bahnhof"),
            ("stayHere 03", "Wohngebiet an der Feldstraße, Edeka in der Nähe"),
            ("S-Bahn", "Wedel ist die Endstation der Linie S1 nach Hamburg"),
            ("Supermärkte", "Aldi, Edeka, Penny und ein Bio-Markt im Zentrum, Edeka an der Feldstraße, "
                            "famila, Aldi und Lidl im Osten, Netto im Westen und im Süden"),
        ]), "rule") + section(
        head("Entscheiden", "Welche Unterkunft passt zu dir?") + which, "rule") + section(
        head("Weiterlesen", tight=True) + lines([
            ("Gastgeber", "Wer vermietet und was Gäste sagen. " + inn("gastgeber.html", "Gastgeber und Bewertungen")),
            ("Anreise", "Mit der S1, dem Flugzeug oder dem Auto. " + inn("anreise-faq.html", "Anreise und häufige Fragen")),
            ("Buchen", "Preise und freie Termine stehen im Inserat. " + inn("anreise-faq.html#buchen", "Alle Buchungswege")),
        ]), "rule") + nextchap("Nächstes Kapitel · Umsehen", "wedel-elbe.html", "Wedel, die Elbe und der Deich")
    item_list = {
        "@context": "https://schema.org", "@type": "ItemList", "name": "stayHere-Unterkünfte in Wedel",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen",
             "url": url_of(H1P)},
            {"@type": "ListItem", "position": 2, "name": "stayHere 02: Wohnung für 3 Gäste nahe der S-Bahn",
             "url": url_of(H2P)},
            {"@type": "ListItem", "position": 3, "name": "stayHere 03: Reihenhaus für 6 Gäste mit Garten",
             "url": url_of(H3P)},
        ],
    }
    page(path, "Drei Ferienunterkünfte in Wedel im Vergleich | stayHere",
         "Die drei stayHere-Unterkünfte in Wedel bei Hamburg im Überblick: Wohnung für 3 Gäste nahe der S-Bahn, "
         "Souterrainwohnung für 4 am Wald, Reihenhaus für 6 mit Garten.",
         body, jsonld=[item_list, crumbs_ld([("index.html", "Start"), (path, "Die Unterkünfte")])], active="haeuser")


# ---------------------------------------------------------------- Kapitel 1: Unterkünfte
OTHER = {"01": (H1P, "stayHere 01: Souterrainwohnung für 4"),
         "02": (H2P, "stayHere 02: Wohnung auf Zeit nahe der S-Bahn"),
         "03": (H3P, "stayHere 03: Reihenhaus für 6 mit Garten")}


def house(num, path, hero_slot, hero_desc, h1, statement, paras, facts, gallery, more, book_statement,
          book_body, related, rental, title, desc):
    CUR[0] = "stayHere " + num
    body = intro("Kapitel 1 · Ankommen", h1, with_rail=False) + hero(hero_slot, hero_desc) + railsec(1) + section(
        duo("Die Unterkunft", statement, paras)) + section(
        head("Auf einen Blick", tight=True) + lines(facts), "rule") + section(
        '<div class="pairs">' + "".join(ph(s, d, "tall") for s, d in gallery) + "</div>") + section(
        head("Mehr zur Unterkunft", tight=True) + acc(more), "rule") + section(
        duo("Buchen", book_statement, book_body + contact_small()), "rule", "buchen") + section(
        head("Passt dazu", tight=True) + lines(related), "rule") + nextchap(
        "Nächstes Kapitel · Umsehen", "wedel-elbe.html", "Wedel, die Elbe und der Deich",
        [v for k, v in OTHER.items() if k != num] + [("haeuser.html#vergleich", "Alle drei vergleichen")])
    page(path, title, desc, body,
         jsonld=[rental, crumbs_ld([("index.html", "Start"), ("haeuser.html", "Die Unterkünfte"),
                                    (path, "stayHere " + num)])], active="haeuser")


def build_01():
    name = "stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen in Wedel"
    desc = ("Souterrainwohnung mit eigenem Eingang in Wedel bei Hamburg für 4 Gäste: 2 Schlafzimmer, Küche, "
            "Billard, schnelles WLAN und Parkplatz am Waldrand.")
    house(
        "01", H1P, "01-hero", "Wohnbereich mit Fernseher und Billardtisch",
        "stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen",
        "Eine Wohnung mit eigenem Eingang in einer ruhigen Wohngegend. Der Wald beginnt direkt nebenan.",
        "<p>stayHere 01 liegt im Souterrain eines Einfamilienhauses in Wedel, am Waldrand des Klövensteen. "
        "Du kommst über einen separaten Eingang in die Wohnung und bist für dich.</p>"
        "<p>Zwei Schlafzimmer bieten Platz für bis zu vier Gäste. Dazu kommen ein eigenes Bad, eine voll "
        "ausgestattete Küche, ein 65-Zoll-Fernseher, Darts und ein Billardtisch.</p>",
        [("Gäste", "bis 4"), ("Schlafen", "2 Schlafzimmer, 4 Betten"), ("Bad", "1, mit Dusche und WC"),
         ("Lage", "Waldrand am Klövensteen"), ("Parken", "kostenlos auf dem Grundstück"),
         ("Preis", "je nach Reisedatum, siehe " + ext(A1, "Airbnb"))],
        [("01-schlafzimmer-einzelbetten", "Schlafzimmer mit drei Einzelbetten"),
         ("01-schlafzimmer-doppelbett", "Schlafzimmer mit Doppelbett"),
         ("01-kueche", "Küche"), ("01-billard", "Billardtisch und Dartscheibe")],
        [("Ausstattung im Detail", ul([
            "Eigener, separater Eingang",
            "Küche mit Herd, Kühlschrank mit Tiefkühlfächern, Mikrowelle, Geschirrspüler, Kaffeemaschine, "
            "Toaster und Wasserkocher",
            "Eigenes Bad mit Dusche und WC", "65-Zoll-Fernseher und Stereoanlage",
            "Billardtisch und Dartscheibe", "Glasfaser-WLAN mit ca. 83 Mbit/s", "Arbeitsplatz",
            "Kostenloser Parkplatz auf dem Grundstück"]), "ausstattung"),
         ("Schlafzimmer und Betten", ul(["Schlafzimmer 1: drei Einzelbetten",
                                         "Schlafzimmer 2: ein kleines Doppelbett"]) +
          "<p>Das passt für Familien, für drei oder vier Freunde und für Kolleginnen und Kollegen, die "
          "getrennte Betten brauchen.</p>", "schlafen"),
         ("Kinoabend, Billard und Arbeiten",
          "<p>Für den Abend gibt es einen 65-Zoll-Fernseher, eine Stereoanlage, eine Dartscheibe und einen "
          "Billardtisch. Wer tagsüber arbeiten muss, hat einen Arbeitsplatz und Glasfaser-WLAN mit rund "
          "83 Mbit/s.</p>"
          '<p class="note">Der Billardtisch steht im Winter nicht zur Verfügung. Für die übrige Zeit bestätigt '
          "dir der Gastgeber die Nutzung vor der Anreise.</p>", "billard"),
         ("Lage und Wege",
          "<p>Der Wald grenzt direkt an die Wohngegend. An der Elbe liegen das Schulauer Fährhaus mit dem "
          "Willkomm-Höft, das Strandbad und der Hamburger Yachthafen. Bäckereien, Supermärkte und der "
          "Wochenmarkt sind in Wedel.</p>" + lines([
              ("Klövensteen", "grenzt direkt an"), ("Badesee Holm", "ca. 8 Minuten mit dem Auto"),
              ("S-Bahnhof Wedel", "Weg ab der Adresse im " + ext(HVV, "HVV") + " planen"),
              ("Späte Ankunft", "Abholung am S-Bahnhof nach Absprache")]) +
          '<p class="muted small">Die genaue Adresse bekommst du nach der Buchung.</p>' +
          karte("01"), "lage"),
         ("Bewertungen im Detail", review_body("01"), "bewertungen")],
        "Preise und freie Termine siehst du auf Airbnb.",
        "<p>Dort stehen der Preis für deine Reisedaten, die freien Nächte und die Stornobedingungen.</p>"
        '<p class="actions">' + ext(A1, "stayHere 01 auf Airbnb ansehen", "btn label") + "</p>",
        [("Kapitel 2", "Der Klövensteen beginnt nebenan. " + inn("wedel-elbe.html#wald", "Wald, Deich und Elbe")),
         ("Kapitel 3", "Mit der S1 ohne Umsteigen in die Stadt. " + inn("hamburg-tipps.html", "Hamburg mit der S1")),
         ("Anreise", "Parken, Flughafen, späte Ankunft. " + inn("anreise-faq.html", "Anreise und häufige Fragen"))],
        rental_ld(H1P, name, desc, 4, 2, 1, [(3, "Einzelbett"), (1, "Kleines Doppelbett")],
                  ["Eigener Eingang", "Küche", "Geschirrspüler", "WLAN (Glasfaser)", "Arbeitsplatz",
                   "Fernseher (65 Zoll)", "Billardtisch", "Dartscheibe", "Kostenloser Parkplatz"], [A1]),
        "Ferienwohnung für 4 Gäste am Klövensteen in Wedel | stayHere 01", desc)


def build_02():
    name = "stayHere 02: Wohnung für 3 Gäste mit Südbalkon und Aufzug in Wedel"
    desc = ("Möblierte 2-Zimmer-Wohnung mit 50 m² in Wedel für bis zu 3 Personen, Vermietung ab einem Monat: "
            "Südbalkon, Aufzug, Stellplatz, ca. 5 Gehminuten zur S-Bahn S1.")
    house(
        "02", H2P, "02-hero", "Wohnzimmer mit Blick auf den Südbalkon",
        "stayHere 02: Wohnung auf Zeit für 3 Gäste, 5 Gehminuten zur S-Bahn",
        "Eine helle Wohnung im Zentrum von Wedel, im dritten Stock mit Aufzug und einem Balkon nach Süden.",
        "<p>stayHere 02 hat 50 m² und zwei Zimmer. Bis zu drei Gäste finden Platz. Die Einrichtung ist neu "
        "und vollständig, mit Küche, Waschmaschine, WLAN und Arbeitsplatz.</p>"
        "<p>Zum S-Bahnhof Wedel gehst du etwa 5 Minuten. Von dort fährt die S1 ohne Umsteigen nach "
        "Hamburg.</p><p>Die Wohnung wird nur noch ab einem Monat vermietet, möbliert über Wunderflats.</p>",
        [("Gäste", "bis 3"), ("Größe", "50 m², 2 Zimmer"), ("Schlafen", "1 Schlafzimmer, 2 Betten"),
         ("Etage", "3. Stock mit Aufzug"), ("Zur S1", "ca. 5 Minuten zu Fuß"),
         ("Parken", "kostenloser Stellplatz"), ("Mietdauer", "1 bis 6 Monate"),
         ("Miete", "siehe " + ext(W2, "Wunderflats"))],
        [("02-schlafzimmer", "Schlafzimmer mit Doppelbett"), ("02-balkon", "Südbalkon mit Sitzplatz"),
         ("02-kueche", "Küche"), ("02-bad", "Bad mit Dusche")],
        [("Ausstattung im Detail", ul([
            "Südbalkon mit Sitzplatz, laut Inserat mit Blick auf Wedeler Au und Elbe",
            "Voll ausgestattete Küche mit Herd, Backofen, Geschirrspüler, Mikrowelle, Kühlschrank und Gefrierfach",
            "Waschmaschine, Bügeleisen und Staubsauger", "WLAN, Fernseher und Arbeitsplatz",
            "Bettwäsche und Handtücher", "Gemeinschaftsgarten mit Grillplatz",
            "Kostenloser Stellplatz, laut Wunderflats in der Tiefgarage"]), "ausstattung"),
         ("Schlafzimmer und Betten", ul(["Schlafzimmer: ein Doppelbett (Queensize)",
                                         "Wohnzimmer: ein Einzelbett"]) +
          "<p>Das Wohnzimmer ist zugleich Durchgangszimmer zum Schlafzimmer.</p>", "schlafen"),
         ("Zugang ohne Treppen",
          "<p>Die Wohnung liegt im 3. Stock und ist mit dem Aufzug erreichbar. Der Weg zum Eingang ist "
          "beleuchtet. Innen ist sie weitgehend stufenlos, nur an der Dusche und am Balkon gibt es je eine "
          "kleine Stufe.</p>"
          '<p class="note">Die Wohnung ist barrierearm, aber nicht barrierefrei. Wenn du auf bestimmte Maße '
          "oder Hilfen angewiesen bist, kläre das bitte vor der Buchung mit dem Gastgeber.</p>", "zugang"),
         ("Lage und Wege",
          "<p>Du wohnst im Zentrum von Wedel, nahe der Elbe. Das Ernst-Barlach-Museum erreichst du zu Fuß. "
          "Das Haus ist an eine Seniorenresidenz angeschlossen. Entsprechend ruhig ist es.</p>" + lines([
              ("S-Bahnhof Wedel", "ca. 5 Minuten zu Fuß"), ("Ernst-Barlach-Museum", "kurzer Fußweg"),
              ("Geschäfte", "in der Nähe"), ("Späte Ankunft", "Abholung am S-Bahnhof nach Absprache")]) +
          '<p class="muted small">Die genaue Adresse bekommst du nach der Buchung.</p>' +
          karte("02"), "lage"),
         ("Miete und Bedingungen",
          '<p class="num">Für 1 bis 6 Monate mietest du die Wohnung möbliert über Wunderflats. Die aktuelle '
          "Miete und die Kaution stehen im Inserat. Haustiere und Rauchen sind nicht erlaubt, ab 22 Uhr gilt Ruhe.</p>"
          '<p class="links">' + ext(W2, "stayHere 02 auf Wunderflats ansehen") + "</p>", "langzeit"),
         ("Bewertungen im Detail", "<p>Die Bewertungen stammen aus der früheren Vermietung über Airbnb.</p>" +
          review_body("02"), "bewertungen")],
        "Vermietung nur ab einem Monat, über Wunderflats.",
        "<p>Auf Wunderflats siehst du die freien Zeiträume und stellst deine Anfrage.</p>"
        '<p class="actions">' + ext(W2, "stayHere 02 auf Wunderflats ansehen", "btn label") +
        '<a href="#langzeit">Miete und Bedingungen</a></p>',
        [("Kapitel 2", "Roland, Barlach-Museum und Bahnhofstraße liegen im Zentrum. " +
          inn("wedel-elbe.html#stadt", "Wedel und die Elbe")),
         ("Kapitel 3", "Was du entlang der S1 erreichst. " + inn("hamburg-tipps.html", "Hamburg mit der S1")),
         ("Termine", "Messen und Konzerte, zu denen du mit der S-Bahn fährst. " +
          inn("events.html", "Events und Messen 2027"))],
        rental_ld(H2P, name, desc, 3, 1, 1, [(1, "Doppelbett (Queensize)"), (1, "Einzelbett")],
                  ["Südbalkon", "Aufzug", "Küche", "Geschirrspüler", "Waschmaschine", "WLAN", "Arbeitsplatz",
                   "Fernseher", "Gemeinschaftsgarten mit Grillplatz", "Kostenloser Stellplatz"],
                  [W2], size=50, rooms=2),
        "Wohnung auf Zeit für 3 nahe S-Bahn Wedel | stayHere 02", desc)


def build_03():
    name = "stayHere 03: Reihenhaus für 6 Gäste mit Garten in Wedel"
    desc = ("Ruhiges Reihenhaus in Wedel bei Hamburg für bis zu 6 Gäste: 4 Schlafzimmer, 1,5 Bäder, Garten, "
            "Waschmaschine und Stellplatz am Haus.")
    house(
        "03", H3P, "03-hero", "Haus von außen mit Garten",
        "stayHere 03: Reihenhaus für 6 Gäste mit Garten",
        "Ein ganzes Haus mit vier Schlafzimmern, anderthalb Bädern und einem eigenen Garten.",
        "<p>stayHere 03 ist ein ruhiges Reihenmittelhaus in einem Wohngebiet von Wedel. Bis zu sechs Gäste "
        "schlafen in vier getrennten Zimmern.</p>"
        "<p>Das passt für Familien mit größeren Kindern, für zwei befreundete Paare mit Kindern oder für "
        "ein Projektteam.</p>",
        [("Gäste", "bis 6"), ("Schlafen", "4 Schlafzimmer, 6 Betten"), ("Bäder", "1,5"),
         ("Draußen", "eigener Garten"), ("Lage", "ruhiges Wohngebiet, ca. 12 Minuten mit dem Bus zur S-Bahn"),
         ("Parken", "1 reservierter, kostenloser Stellplatz am Haus"),
         ("Preis", "je nach Reisedatum, siehe " + ext(A3, "Airbnb"))],
        [("03-wohnzimmer", "Wohnzimmer"), ("03-garten", "Garten"),
         ("03-schlafzimmer-doppelbett", "Schlafzimmer mit Doppelbett"),
         ("03-schlafzimmer-einzelbetten", "Schlafzimmer mit zwei Einzelbetten")],
        [("Ausstattung im Detail", ul([
            "Eigener Garten", "Voll ausgestattete Küche mit Geschirrspüler, Kochgeschirr und Geschirr",
            "Waschmaschine im Haus", "WLAN und Arbeitsplatz",
            "Fernseher mit Amazon Fire TV Stick oder Satellitenempfang", "Neue, gut dämmende Fenster",
            "Ein reservierter, kostenloser Stellplatz direkt am Haus"]), "ausstattung"),
         ("Schlafzimmer und Betten", ul([
             "Schlafzimmer 1: ein Doppelbett", "Schlafzimmer 2: ein Doppelbett",
             "Schlafzimmer 3: zwei Einzelbetten", "Schlafzimmer 4: zwei Einzelbetten"]), "schlafen"),
         ("Ankunft und Schlüssel",
          "<p>Den Schlüssel übergibt dir der Gastgeber persönlich, oder du holst ihn aus einer Schlüsselbox. "
          "Wenn du spät ankommst, holt er dich nach Absprache am S-Bahnhof Wedel ab.</p>", "ankunft"),
         ("Lage und Wege",
          "<p>Das Haus liegt in einem ruhigen Wohngebiet von Wedel. Zum S-Bahnhof und an die Elbe "
          "fährst du mit dem Bus.</p>" + lines([
              ("Bushaltestelle, EDEKA", "ca. 5 Minuten zu Fuß"),
              ("Riedemanns Park", "ca. 10 Minuten zu Fuß"),
              ("S-Bahnhof Wedel, Bahnhofstraße", "ca. 12 Minuten mit dem Bus"),
              ("Elbe, Willkomm-Höft", "ca. 12 Minuten mit dem Bus")]) +
          '<p class="muted small">Die genaue Adresse bekommst du nach der Buchung.</p>' +
          karte("03"), "lage"),
         ("Bewertungen im Detail", review_body("03"), "bewertungen")],
        "Preise und freie Termine siehst du auf Airbnb.",
        "<p>Dort stehen der Preis für deine Reisedaten, die freien Nächte und die Stornobedingungen.</p>"
        '<p class="actions">' + ext(A3, "stayHere 03 auf Airbnb ansehen", "btn label") + "</p>",
        [("Kapitel 2", "In 12 Minuten mit dem Bus am Willkomm-Höft. " +
          inn("wedel-elbe.html#wasser", "Wedel und die Elbe")),
         ("Kapitel 3", "Mit Bus und S1 nach Hamburg. " + inn("hamburg-tipps.html", "Hamburg mit der S1")),
         ("Anreise", "Parken, Flughafen, späte Ankunft. " + inn("anreise-faq.html", "Anreise und häufige Fragen"))],
        rental_ld(H3P, name, desc, 6, 4, 1.5, [(2, "Doppelbett"), (4, "Einzelbett")],
                  ["Garten", "Küche", "Geschirrspüler", "Waschmaschine", "WLAN", "Arbeitsplatz",
                   "Fernseher mit Fire TV Stick", "Kostenloser Stellplatz am Haus"], [A3]),
        "Ferienhaus für 6 Gäste mit Garten in Wedel | stayHere 03", desc)


# ---------------------------------------------------------------- Gastgeber
def build_host():
    CUR[0] = "Gastgeber"
    path = "gastgeber.html"
    scores = "".join(
        '<div class="score"><p class="label">stayHere %s</p><p class="big num">%s</p>'
        '<p class="num">von 5 Sternen bei %d Bewertungen</p><p class="muted small">Am häufigsten gelobt: %s.</p>'
        '<p class="links small">%s</p></div>' % (
            n, REV[n]["score"], REV[n]["count"], REV[n]["praised"], inn(REV[n]["page"], "Zur Unterkunft"))
        for n in ("01", "02", "03"))
    body = intro("Hinter den Unterkünften", "Dein Gastgeber und was Gäste sagen", with_rail=False) + section(duo(
        "Dein Gastgeber",
        "Ruppert Gerhard Matzke vermietet seit zehn Jahren und ist auf Airbnb als Superhost ausgezeichnet.",
        "<p>Er führt die drei Unterkünfte privat, antwortet meist innerhalb einer Stunde und spricht Deutsch, "
        "Englisch und Spanisch.</p><p>Wenn du spät ankommst, holt er dich nach Absprache am S-Bahnhof Wedel ab.</p>"
        + lines([("Gastgeber seit", "10 Jahren"), ("Bewertungen", "318, Durchschnitt 4,86"),
                 ("Antwortrate", "100 %"), ("Sprachen", "Deutsch, Englisch, Spanisch"),
                 ("Quelle", "Airbnb-Profil, Stand " + STAND)]))) + section(
        head("Was Gäste sagen", "Zusammen fast 300 Bewertungen auf Airbnb. Alle drei Unterkünfte liegen bei "
             "4,8 Sternen oder mehr.") + '<div class="scores">' + scores + "</div>" +
        '<div style="margin-top:2.5rem">' + acc([
            ("Einzelnoten für stayHere %s" % n, review_body(n, link_host=False), "noten-" + n)
            for n in ("01", "02", "03")]) + "</div>", "rule") + nextchap(
        "Kapitel 1 · Ankommen", "haeuser.html", "Die drei Unterkünfte ansehen",
        [("anreise-faq.html", "Anreise und häufige Fragen"), ("anreise-faq.html#buchen", "Buchen")])
    person = {"@context": "https://schema.org", "@type": "Person", "name": "Ruppert Gerhard Matzke",
              "jobTitle": "Gastgeber", "knowsLanguage": ["de", "en", "es"],
              "worksFor": {"@id": BASE + "/#stayhere"}, "url": url_of(path)}
    page(path, "Gastgeber und Bewertungen | stayHere Wedel",
         "Wer stayHere in Wedel vermietet und wie Gäste die drei Unterkünfte auf Airbnb bewerten: Superhost seit "
         "10 Jahren, 4,8 bis 5,0 Sterne.",
         body, jsonld=[person, crumbs_ld([("index.html", "Start"), (path, "Gastgeber und Bewertungen")])],
         active="haeuser")


# ---------------------------------------------------------------- Kapitel 2
def spot(ident, label, title, text, links, slot=None, sdesc=None):
    link_html = '<p class="links">%s</p>' % "".join(links)
    if slot:
        return feature(ph(slot, sdesc, "portrait"), label, title, text, link_html, ident=ident)
    return ('<article class="duo" id="%s"><div class="duo-head"><p class="label">%s</p><h2 class="statement">%s</h2>'
            '</div><div class="prose">%s%s</div></article>' % (ident, label, title, text, link_html))


def build_wedel():
    CUR[0] = "Wedel & Elbe"
    path = "wedel-elbe.html"
    spots = [
        spot("wasser", "Am Wasser", "Willkomm-Höft am Schulauer Fährhaus",
             "<p>An der Schiffsbegrüßungsanlage werden die Schiffe begrüßt und verabschiedet, die auf der Elbe "
             "nach Hamburg fahren oder von dort kommen. Vom Ufer aus siehst du Containerschiffe und "
             "Kreuzfahrtschiffe aus der Nähe.</p>"
             "<p>Von %s fährst du etwa 12 Minuten mit dem Bus.</p>" % inn(H3P, "stayHere 03"),
             [ext("https://www.wedel.de/tourismus-freizeit/sehenswertes-ausfluege/schiffsbegruessungsanlage-willkomm-hoeft",
                  "Besucherinfos der Stadt Wedel")],
             "wedel-willkomm-hoeft", "Schiff vor dem Willkomm-Höft"),
        spot("yachthafen", "Am Wasser", "Strandbar 28° und Hamburger Yachthafen",
             "<p>Die Strandbar liegt am Wedeler Strandbad direkt an der Elbe. Die Öffnungszeiten hängen vom "
             "Wetter ab, Reservierungen bestätigt der Betreiber.</p>"
             "<p>Der Hamburger Yachthafen liegt trotz seines Namens in Wedel. Ein Spaziergang durch den "
             "Hafenbereich lohnt sich wegen der vielen Segel- und Motorboote. Bitte beachte die Zugangsregeln "
             "vor Ort.</p>",
             [ext("https://28grad.com/", "28grad.com"),
              ext("https://www.hamburger-yachthafen.de/infos/standort", "Yachthafen: Standort und Anreise")]),
        spot("deich", "Auf dem Deich", "Elbdeich und Wedeler Marsch",
             "<p>Westlich von Wedel beginnt die Deichlandschaft der Elbmarschen. Auf dem Deich gehst oder "
             "radelst du zwischen Elbe und Marschwiesen in Richtung Fährmannssand und Haseldorfer Marsch.</p>"
             "<p>In der Wedeler Marsch betreut der NABU eine Vogelstation mit Beobachtungsständen. Im Winter "
             "rasten dort Tausende Gänse. Die Station hat nur an einzelnen Wochentagen geöffnet.</p>",
             [ext("https://www.nabu.de/natur-und-landschaft/natur-erleben/nabu-zentren/hamburg/24059.html",
                  "NABU-Vogelstation Wedeler Marsch")],
             "wedel-deich", "Elbdeich mit Schafen oder weitem Blick über die Marsch"),
        spot("ufer", "Am Ufer entlang", "Elbwanderweg in Richtung Blankenese",
             "<p>Der Weg startet am Schulauer Fährhaus und führt am Wasser entlang nach Osten. Wie weit du "
             "gehst, entscheidest du unterwegs. Zurück kommst du zu Fuß oder ab Blankenese mit der S1.</p>"
             "<p>Was dich in Blankenese erwartet, steht in %s.</p>" % inn("hamburg-tipps.html#blankenese", "Kapitel 3"),
             [ext("https://www.wedel.de/tourismus-freizeit/elbe-maritimes/elbwanderweg",
                  "Elbwanderweg bei der Stadt Wedel")]),
        spot("wald", "Im Wald", "Klövensteen und Wildgehege",
             "<p>Der Wald Klövensteen grenzt an Wedel. %s liegt direkt am Waldrand. Das Wildgehege gehört zu "
             "Hamburg-Rissen. Prüfe vor dem Besuch die Öffnungszeiten und mögliche Sperrungen.</p>"
             % inn(H1P, "stayHere 01"),
             [ext("https://www.hamburg.de/politik-und-verwaltung/bezirke/altona/themen/umwelt-natur-klimaschutz/kloevensteen/wildgehege",
                  "Wildgehege Klövensteen")],
             "wedel-kloevensteen", "Waldweg im Klövensteen"),
        spot("stadt", "In der Stadt", "Roland, Barlach und die Bahnhofstraße",
             "<p>Auf dem Marktplatz steht der Roland, das Wahrzeichen der Stadt. Im Geburtshaus des Bildhauers "
             "Ernst Barlach in der Mühlenstraße 1 zeigt das Barlach Kunstmuseum wechselnde Ausstellungen.</p>"
             "<p>In der Bahnhofstraße findest du Cafés, Apotheken und Geschäfte. %s liegt im Zentrum, etwa "
             "5 Gehminuten vom S-Bahnhof.</p>" % inn(H2P, "stayHere 02"),
             [ext("https://www.ernst-barlach.de/", "Barlach Kunstmuseum Wedel")]),
    ]
    body = intro("Kapitel 2 · Umsehen", "Wedel und die Elbe: Tipps vor der Haustür", with_rail=False) + hero(
        "wedel-hero", "Elbe bei Wedel mit Containerschiff") + railsec(2) + section(duo(
            "Der Ort",
            "Vor der Tür liegen ein Fluss mit großen Schiffen, ein Deich mit weitem Blick und ein Wald.",
            "<p>Wedel liegt in Schleswig-Holstein, direkt hinter der Hamburger Stadtgrenze. Plane ruhig einen "
            "ganzen Tag ohne Hamburg ein.</p><p>Die Tipps sind nach Orten sortiert: erst ans Wasser, dann auf "
            "den Deich, am Ufer entlang, in den Wald und zum Schluss in die Stadt.</p>"
            '<p class="links"><a href="#wasser">Am Wasser</a><a href="#deich">Auf dem Deich</a>'
            '<a href="#ufer">Am Ufer</a><a href="#wald">Im Wald</a><a href="#stadt">In der Stadt</a></p>')) + section(
        '<div class="stack" id="ausfluege">' + "".join(spots) + "</div>", "rule") + section(
        head("Von den Unterkünften aus", tight=True) + lines([
            ("stayHere 01", "Direkt am Klövensteen. " + inn(H1P + "#lage", "Lage und Wege")),
            ("stayHere 02", "Im Zentrum, nahe Roland und Bahnhofstraße. " + inn(H2P + "#lage", "Lage und Wege")),
            ("stayHere 03", "Ca. 12 Minuten mit dem Bus zum Willkomm-Höft. " + inn(H3P + "#lage", "Lage und Wege")),
        ]), "rule") + nextchap(
        "Nächstes Kapitel · Losfahren", "hamburg-tipps.html", "Hamburg mit der S1",
        [("haeuser.html", "Zurück zu den Unterkünften")])
    places = places_ld("Ausflugsziele in Wedel an der Elbe", [
        ("Schiffsbegrüßungsanlage Willkomm-Höft",
         "https://www.wedel.de/tourismus-freizeit/sehenswertes-ausfluege/schiffsbegruessungsanlage-willkomm-hoeft", "Wedel"),
        ("Strandbar 28° am Strandbad Wedel", "https://28grad.com/", "Wedel"),
        ("Hamburger Yachthafen", "https://www.hamburger-yachthafen.de/infos/standort", "Wedel"),
        ("NABU-Vogelstation Wedeler Marsch",
         "https://www.nabu.de/natur-und-landschaft/natur-erleben/nabu-zentren/hamburg/24059.html", "Wedel"),
        ("Elbwanderweg", "https://www.wedel.de/tourismus-freizeit/elbe-maritimes/elbwanderweg", "Wedel"),
        ("Wildgehege Klövensteen",
         "https://www.hamburg.de/politik-und-verwaltung/bezirke/altona/themen/umwelt-natur-klimaschutz/kloevensteen/wildgehege",
         "Hamburg"),
        ("Barlach Kunstmuseum Wedel", "https://www.ernst-barlach.de/", "Wedel"),
    ])
    page(path, "Wedel &amp; Elbe: Willkomm-Höft, Elbdeich, Klövensteen | stayHere",
         "Tipps für Wedel: Willkomm-Höft, Elbdeich und Wedeler Marsch, Elbwanderweg, Yachthafen, Klövensteen, "
         "Roland und Barlach-Museum, mit offiziellen Links.",
         body, jsonld=[places, crumbs_ld([("index.html", "Start"), (path, "Wedel & Elbe")])], active="wedel")


# ---------------------------------------------------------------- Kapitel 3
def tip(title, meta, text, links):
    return (title + '<span class="sum-meta">%s</span>' % meta,
            text + '<p class="links small">%s</p>' % "".join(links))


def build_hamburg():
    CUR[0] = "Hamburg"
    path = "hamburg-tipps.html"
    stops = """<ol class="stops">
<li class="start" id="wedel"><p class="label">Wedel</p><h2 class="statement">Einsteigen an der Endstation</h2>
<p>Von """ + inn(H2P, "stayHere 02") + """ gehst du etwa 5 Minuten zum S-Bahnhof, von """ + inn(H3P, "stayHere 03") + """ fährst du etwa 12 Minuten mit dem Bus. Der Zug startet hier.</p></li>

<li id="blankenese"><p class="label">Blankenese</p><h2 class="statement">Treppenviertel und Elbstrand</h2>
<p>Schmale Treppen führen zwischen alten Kapitänshäusern hinunter zum Elbstrand. Hier endet auch der """ + inn("wedel-elbe.html#ufer", "Elbwanderweg aus Wedel") + """.</p></li>

<li id="landungsbruecken"><p class="label">Landungsbrücken</p><h2 class="statement">Hafen und Elbphilharmonie</h2>
<p>Hier legen die Hafenfähren ab. Zum Hafengeburtstag im Mai steigst du ebenfalls hier aus.</p>
""" + acc([tip("Elbphilharmonie Plaza", "HafenCity, Platz der Deutschen Einheit",
               "<p>Die Aussichtsplattform bietet einen Blick über Stadt und Hafen. Von den Landungsbrücken "
               "fährst du mit der U3 bis Baumwall und gehst dann zu Fuß. Das Plaza-Ticket ist kein "
               "Konzertticket und enthält keine HVV-Fahrt.</p>",
               [ext("https://plazashop.elbphilharmonie.de/", "Plaza-Tickets"),
                ext("https://www.elbphilharmonie.de/de/anfahrt", "Anfahrt")])]) + """</li>

<li id="stadthausbruecke"><p class="label">Stadthausbrücke</p><h2 class="statement">Speicherstadt</h2>
<p>Von hier gehst du zu Fuß in die Speicherstadt.</p>
""" + acc([tip("Miniatur Wunderland", "Speicherstadt, Kehrwieder 2",
               "<p>Modelleisenbahnen und Miniaturwelten auf mehreren Etagen. Reserviere deine Wunschzeit am "
               "besten vorab. Von der Stadthausbrücke gehst du laut Anbieter etwa 11 Minuten zu Fuß.</p>",
               [ext("https://www.miniatur-wunderland.de/tickets", "Tickets"),
                ext("https://www.miniatur-wunderland.de/besuchen/wunderland-vor-ort/anfahrt", "Anfahrt")]),
           tip("Hamburg Dungeon", "Speicherstadt, Kehrwieder 2",
               "<p>Schauspiel und Gruselgeschichten aus der Hamburger Geschichte. Buche ein Zeitfenster online "
               "und prüfe die Hinweise zu Alter und Sprache.</p>",
               [ext("https://www.thedungeons.com/hamburg/tickets/", "Tickets"),
                ext("https://www.thedungeons.com/hamburg/plane-deinen-besuch/plane-deinen-besuch/anreise/",
                    "Anreise")])]) + """</li>

<li id="jungfernstieg"><p class="label">Jungfernstieg</p><h2 class="statement">Alster und HafenCity</h2>
<p>Am Jungfernstieg liegt die Binnenalster. Von hier fährt die U4 in die HafenCity.</p>
""" + acc([tip("Westfield Hamburg-Überseequartier", "HafenCity, nahe der Speicherstadt",
               "<p>Einkaufen, Essen und Freizeit unter einem Dach. Vom Jungfernstieg fährst du mit der U4 "
               "Richtung Elbbrücken bis Überseequartier. Für den Einkauf brauchst du keine Reservierung.</p>",
               [ext("https://www.westfield.com/de/germany/hamburg", "Infos und Angebote"),
                ext("https://www.westfield.com/de/germany/hamburg/access", "Anfahrt")])]) + """</li>

<li id="hauptbahnhof"><p class="label">Hauptbahnhof</p><h2 class="statement">Fernzüge und weiter zum Flughafen</h2>
<p>Hier steigst du in die Fernzüge um. Die S1 fährt weiter bis zum Flughafen Hamburg. Mehr dazu steht unter """ + inn("anreise-faq.html", "Anreise") + """.</p></li>
</ol>"""
    body = intro("Kapitel 3 · Losfahren", "Hamburg mit der S1: Tipps ab Wedel", with_rail=False) + hero(
        "hamburg-hero", "Landungsbrücken oder Speicherstadt") + railsec(3) + section(duo(
            "Die Linie",
            "In Wedel steigst du an der Endstation ein. Die S1 fährt ohne Umsteigen an die Landungsbrücken, "
            "in die Innenstadt und zum Hauptbahnhof.",
            "<p>Du brauchst kein Auto und musst nicht umsteigen. Die Tipps stehen in der Reihenfolge, in der "
            "du die Halte erreichst. Klappe einen Tipp auf, um Details und Ticket-Links zu sehen.</p>"
            '<p class="muted small">Stand: 14.11.2026. Die Wege sind Vorschläge. Prüfe Fahrplan, Baustellen und '
            "Öffnungszeiten vor dem Besuch im " + ext(HVV, "HVV") + " und beim Anbieter.</p>")) + section(
        stops, "rule") + section(
        head("Passt dazu", tight=True) + lines([
            ("Termine", "Messen, Konzerte, Sport und der Hafengeburtstag. " +
             inn("events.html", "Events und Messen 2027")),
            ("Unterkünfte", "Am nächsten an der S-Bahn wohnst du in " + inn(H2P, "stayHere 02") + "."),
        ]), "rule") + nextchap("Weiter", "events.html", "Events und Messen 2027",
                               [("wedel-elbe.html", "Zurück zu Kapitel 2"), ("anreise-faq.html#buchen", "Buchen")])
    places = places_ld("Hamburg-Tipps ab Wedel", [
        ("Elbphilharmonie Plaza", "https://plazashop.elbphilharmonie.de/", "Hamburg"),
        ("Miniatur Wunderland", "https://www.miniatur-wunderland.de/tickets", "Hamburg"),
        ("Hamburg Dungeon", "https://www.thedungeons.com/hamburg/tickets/", "Hamburg"),
        ("Westfield Hamburg-Überseequartier", "https://www.westfield.com/de/germany/hamburg", "Hamburg"),
    ])
    page(path, "Hamburg-Tipps ab Wedel: Speicherstadt &amp; HafenCity | stayHere",
         "Hamburg mit der S1 ab Wedel: Blankenese, Landungsbrücken, Elbphilharmonie Plaza, Miniatur Wunderland, "
         "Hamburg Dungeon und Westfield, mit Links zu den Tickets.",
         body, jsonld=[places, crumbs_ld([("index.html", "Start"), (path, "Hamburg-Tipps")])], active="hamburg")


def build_events():
    CUR[0] = "Events"
    path = "events.html"
    ld_items = []
    for start, end, datetext, name, kind, place, accs, url, hint in EVENTS:
        ld_items.append({
            "@type": "Event", "name": name, "startDate": start, "endDate": end,
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "location": {"@type": "Place", "name": place,
                         "address": {"@type": "PostalAddress", "addressLocality": "Hamburg", "addressCountry": "DE"}},
            "url": url})
    body = intro("Kapitel 3 · Losfahren", "Hamburg-Events und Messen 2027", cur=3) + section(duo(
        "Der Kalender",
        "Messen, Konzerte, Sport und der Hafengeburtstag, alle mit der S-Bahn ab Wedel erreichbar.",
        "<p>Zu jedem Termin findest du den Link zum Veranstalter und die Unterkünfte, die dafür gut passen. "
        "Welche Halte die S1 anfährt, steht in den %s.</p>" % inn("hamburg-tipps.html", "Hamburg-Tipps") +
        acc([("Hinweise zu Terminen, Tickets und freien Nächten",
              "<p>Die Termine stammen von den Seiten der Veranstalter, Stand 14.11.2026. Änderungen sind "
              "möglich.</p><p>stayHere verkauft keine Tickets. Eine Empfehlung bedeutet nicht, dass die Unterkunft "
              "an dem Termin frei ist. Freie Nächte siehst du auf Airbnb und Wunderflats.</p>", "hinweise")]))) + """
<section id="events" class="rule">
<div class="wrap">
<div class="filter" role="group" aria-label="Nach Art filtern">
<button type="button" class="label" id="filter-alle" data-filter="alle" aria-pressed="true">Alle</button>
<button type="button" class="label" id="filter-messe" data-filter="Messe" aria-pressed="false">Messen</button>
<button type="button" class="label" id="filter-konzert" data-filter="Konzert" aria-pressed="false">Konzerte</button>
<button type="button" class="label" id="filter-sport" data-filter="Sport" aria-pressed="false">Sport</button>
<button type="button" class="label" id="filter-hafenfest" data-filter="Hafenfest" aria-pressed="false">Hafenfest</button>
</div>
<ol class="events">
""" + event_rows(EVENTS) + """
</ol>
</div>
</section>
""" + nextchap("Zum Schluss", "anreise-faq.html", "Anreise und Buchung",
               [("hamburg-tipps.html", "Zurück zu den Hamburg-Tipps"), ("haeuser.html", "Zu den Unterkünften")])
    events = {"@context": "https://schema.org", "@type": "ItemList", "name": "Hamburg-Events 2027",
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": e}
                                  for i, e in enumerate(ld_items)]}
    page(path, "Hamburg-Events 2027 mit Unterkunft in Wedel | stayHere",
         "Hamburg-Termine 2027 mit Unterkunft in Wedel: INTERNORGA, Hafengeburtstag, Haspa Marathon, ELBJAZZ und "
         "Konzerte, mit Link zum Veranstalter.",
         body, jsonld=[events, crumbs_ld([("index.html", "Start"), ("hamburg-tipps.html", "Hamburg-Tipps"),
                                          (path, "Events")])], active="hamburg", scripts=["js/events.js"])


FAQ_LINKS = {
    0: ("haeuser.html", "Die drei Unterkünfte"), 1: ("haeuser.html#vergleich", "Vergleich der Unterkünfte"),
    2: ("haeuser.html#vergleich", "Vergleich der Unterkünfte"), 3: ("hamburg-tipps.html", "Hamburg mit der S1"),
    6: ("haeuser.html", "Die drei Unterkünfte"), 7: (H2P + "#zugang", "stayHere 02: Zugang ohne Treppen"),
    8: (H1P + "#billard", "stayHere 01: Billard und Kinoabend"),
    9: ("wedel-elbe.html#deich", "Elbdeich und Wedeler Marsch"),
    10: (H2P + "#langzeit", "stayHere 02: Miete und Bedingungen"), 11: ("anreise-faq.html#buchen", "Alle Buchungswege"),
    12: ("gastgeber.html", "Gastgeber und Bewertungen"),
}


def build_faq():
    CUR[0] = "Anreise & FAQ"
    path = "anreise-faq.html"
    items = []
    for i, (q, a) in enumerate(FAQ):
        more = '<p class="links small">%s</p>' % inn(*FAQ_LINKS[i]) if i in FAQ_LINKS else ""
        items.append((q, "<p>%s</p>%s" % (a, more)))
    body = intro("Zum Schluss · Buchung und Anreise", "Buchen, Anreise und häufige Fragen", cur=0) + section(
        head("Buchen", "Preise und freie Termine siehst du direkt im Inserat.") + book_lines(),
        "", "buchen") + section(
        duo(
            "Mit der S1",
            "Wedel ist die Endstation der S1. Von dort fährst du ohne Umsteigen in die Hamburger Innenstadt "
            "und zum Flughafen.",
            "<p>Fahrzeiten, Takt und Baustellen prüfst du im " + ext(HVV, "HVV-Fahrplan") +
            ". Was an den Halten liegt, steht in den " + inn("hamburg-tipps.html", "Hamburg-Tipps") + ".</p>" + lines([
                ("Mit der Bahn", "Fernzüge halten am Hamburger Hauptbahnhof. Von dort fährt die S1 direkt nach Wedel."),
                ("Mit dem Flugzeug", "Vom Flughafen Hamburg fährt die S1 ohne Umsteigen bis Wedel. In der "
                 "Gegenrichtung wird der Zug in Ohlsdorf geteilt. Achte auf den Zugteil zum Flughafen."),
                ("Mit dem Auto", "Alle drei Unterkünfte haben einen kostenlosen Parkplatz. Die Adresse für dein "
                 "Navi bekommst du nach der Buchung."),
                ("Späte Ankunft", "Der Gastgeber holt dich nach Absprache am S-Bahnhof Wedel ab."),
            ])), "rule", "anreise") + section(
        head("Häufige Fragen", tight=True) + acc(items), "rule", "faq") + nextchap("Von vorn", "haeuser.html", "Zurück zu den Unterkünften")
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in FAQ]}
    page(path, "Anreise &amp; FAQ: S-Bahn S1, Parken, Buchung | stayHere Wedel",
         "Anreise nach Wedel mit S1, Flugzeug und Auto. Antworten zu Gästezahl, Weg zur S-Bahn, Parkplatz, "
         "Balkon, Garten und Buchung.",
         body, jsonld=[faq_ld, crumbs_ld([("index.html", "Start"), (path, "Anreise & FAQ")])], active="anreise")


def build_legal():
    CUR[0] = "Impressum"
    path = "impressum.html"
    body = intro("Rechtliches", "Impressum und Datenschutz", with_rail=False) + section(duo(
        "Impressum", "Ruppert Gerhard Matzke, stayHere Wedel",
        "<p>22880 Wedel<br>Deutschland</p>"
        '<p>E-Mail: <a href="mailto:%s">%s</a><br>Telefon: <a href="tel:%s">%s</a></p>' % (MAIL, MAIL, TEL, TEL_SHOW) +
        "<p>Veranstaltungen, die auf dieser Seite genannt werden, führen die verlinkten Veranstalter durch. "
        "stayHere verkauft keine Veranstaltungstickets.</p>"), "") + section(duo(
            "Datenschutz", "Diese Seite setzt keine Cookies und lädt nichts von fremden Servern.",
            "<p><strong>Verantwortlicher:</strong> Ruppert Gerhard Matzke, 22880 Wedel, " + MAIL + "</p>"
            "<p><strong>Eigener Seitencode:</strong> Schriften und Skripte liegen auf demselben Server wie die "
            "Seite. Es gibt keine Analyse- oder Werbedienste. Eingaben werden nicht gespeichert.</p>"
            "<p><strong>Karte:</strong> Die Karte von Wedel ist eine eigene Zeichnung und lädt nichts nach. "
            "Erst wenn du auf den Knopf für die Google-Karte klickst, wird eine Karte von Google geladen. Dabei "
            "werden deine IP-Adresse und Browserdaten an Google übertragen, auch in die USA. Rechtsgrundlage "
            "ist deine Einwilligung durch den Klick (Art. 6 Abs. 1 lit. a DSGVO). Weitere Informationen: "
            + ext("https://policies.google.com/privacy", "Datenschutzerklärung von Google") + ".</p>"
            "<p><strong>Externe Dienste:</strong> Airbnb, Wunderflats, die Seiten der Veranstalter und der HVV "
            "öffnen sich erst, wenn du einen Link anklickst. Für sie gelten die Datenschutzhinweise des "
            "jeweiligen Anbieters.</p>"
            "<p><strong>Kontaktanfragen:</strong> Wenn du per E-Mail (Postfach bei Google Gmail) oder Telefon "
            "Kontakt aufnimmst, werden deine Angaben zur Bearbeitung der Anfrage verarbeitet (Art. 6 Abs. 1 "
            "lit. b oder f DSGVO) und danach gelöscht, soweit keine Aufbewahrungspflicht besteht.</p>"
            "<p><strong>Deine Rechte:</strong> Du hast das Recht auf Auskunft, Berichtigung, Löschung, "
            "Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch sowie das Recht auf "
            "Beschwerde bei einer Aufsichtsbehörde, zum Beispiel beim "
            + ext("https://www.datenschutzzentrum.de/", "ULD Schleswig-Holstein") +
            ". Eine automatisierte Entscheidungsfindung oder Profilbildung findet nicht statt.</p>"), "rule")
    page(path, "Impressum und Datenschutz | stayHere Wedel",
         "Impressum und Datenschutzhinweise von stayHere Wedel, Ruppert Gerhard Matzke, 22880 Wedel.",
         body, robots="noindex,follow", in_sitemap=False)


SITE_JS = """(function () {
  var menus = Array.prototype.slice.call(document.querySelectorAll('details.menu'));
  menus.forEach(function (m) {
    m.addEventListener('toggle', function () {
      if (m.open) { menus.forEach(function (o) { if (o !== m) { o.open = false; } }); }
    });
  });
  document.addEventListener('click', function (e) {
    menus.forEach(function (m) { if (m.open && !m.contains(e.target)) { m.open = false; } });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') { return; }
    menus.forEach(function (m) { if (m.open) { m.open = false; m.querySelector('summary').focus(); } });
  });
  // Die Google-Karte wird erst geladen, wenn jemand darauf klickt.
  Array.prototype.forEach.call(document.querySelectorAll('[data-gmap]'), function (b) {
    b.addEventListener('click', function () {
      var fig = b.closest('.map');
      var svg = fig.querySelector('.mapsvg');
      var f = document.createElement('iframe');
      f.src = b.getAttribute('data-gmap');
      f.title = 'Google-Karte von Wedel';
      f.loading = 'lazy';
      f.setAttribute('referrerpolicy', 'no-referrer');
      if (svg) { fig.replaceChild(f, svg); }
      b.parentNode.parentNode.removeChild(b.parentNode);
    });
  });
  // Springt ein Link auf einen zugeklappten Bereich, wird er geöffnet.
  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) { return; }
    var el = document.getElementById(id);
    var first = el;
    while (el) { if (el.tagName === 'DETAILS') { el.open = true; } el = el.parentElement; }
    if (first && first.scrollIntoView) { first.scrollIntoView(); }
  }
  window.addEventListener('hashchange', openTarget);
  openTarget();
})();
"""



def not_found():
    """Seite für Adressen, die es nicht gibt. Dreisprachig, weil Cloudflare nur
    eine einzige 404-Seite für die ganze Website ausliefert."""
    body = section(
        '<p class="label">Fehler 404</p>'
        "<h1>Diese Seite gibt es nicht</h1>"
        '<div class="lines">'
        "<p>Die Adresse führt ins Leere. Vielleicht hat sich ein Tippfehler eingeschlichen, "
        "oder die Seite heißt inzwischen anders.</p>"
        '<p lang="en">This page does not exist. The address leads nowhere.</p>'
        '<p lang="es">Esta página no existe. La dirección no lleva a ninguna parte.</p>'
        "</div>"
        '<p class="links">%s · %s · %s</p>' % (
            inn("index.html", "Zur Startseite"),
            inn("haeuser.html", "Unterkünfte"),
            inn("anreise-faq.html", "Anreise und Fragen")), "rule")
    page("404.html", "Seite nicht gefunden | stayHere Wedel",
         "Diese Adresse führt ins Leere. Zurück zur Startseite von stayHere Wedel.",
         body, robots="noindex,follow", in_sitemap=False)


def build_meta_files():
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in PAGES:
        sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (url_of(p), LASTMOD))
    sm.append("</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm) + "\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE)
    # Ohne eigene 404-Seite liefert Cloudflare Pages für jede unbekannte Adresse
    # die Startseite mit Status 200 aus. Suchmaschinen nehmen das als echte Seite.
    not_found()
    # Schriften ändern sich nie, Stil und Skript selten.
    with open(os.path.join(OUT, "_headers"), "w", encoding="utf-8") as f:
        f.write("/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n"
                "/img/*\n  Cache-Control: public, max-age=2592000\n"
                "/css/*\n  Cache-Control: public, max-age=86400\n"
                "/js/*\n  Cache-Control: public, max-age=86400\n")
    llms = """# stayHere Wedel

> Drei privat geführte Ferienunterkünfte in 22880 Wedel (Schleswig-Holstein), an der Elbe westlich von Hamburg. Wedel ist die Endstation der S-Bahn-Linie S1, die ohne Umsteigen nach Altona, Landungsbrücken, Jungfernstieg, Hamburg Hauptbahnhof und zum Flughafen fährt. Gastgeber: Ruppert Gerhard Matzke, Airbnb-Superhost, spricht Deutsch, Englisch und Spanisch. Stand der Angaben: {stand}.

## Unterkünfte

- [stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen]({b}/unterkuenfte/stayhere-01.html): 2 Schlafzimmer (3 Einzelbetten, 1 kleines Doppelbett), 1 Bad, eigener Eingang, Küche, 65-Zoll-Fernseher, Billard (nicht im Winter), Darts, Glasfaser-WLAN ca. 83 Mbit/s, kostenloser Parkplatz, ruhige Lage am Waldrand. Airbnb 4,88 von 5 (191 Bewertungen). Buchung: {a1}
- [stayHere 02: Wohnung für 3 Gäste mit Südbalkon und Aufzug]({b}/unterkuenfte/stayhere-02.html): 50 m², 2 Zimmer, 1 Schlafzimmer (Doppelbett) plus Einzelbett im Wohnzimmer, 3. Stock mit Aufzug, weitgehend stufenlos, Küche, Waschmaschine, kostenloser Stellplatz, Zentrum von Wedel, ca. 5 Gehminuten zum S-Bahnhof Wedel (S1). Vermietung nur ab 1 Monat (bis 6 Monate) über Wunderflats: {w2} . Frühere Airbnb-Bewertung 4,83 von 5 (90 Bewertungen).
- [stayHere 03: Reihenhaus für 6 Gäste mit Garten]({b}/unterkuenfte/stayhere-03.html): 4 Schlafzimmer (2 Doppelbetten, 4 Einzelbetten), 1,5 Bäder, Garten, Küche, Waschmaschine, reservierter Stellplatz am Haus, ruhiges Wohngebiet, ca. 12 Minuten mit dem Bus zum S-Bahnhof Wedel und zur Elbe. Airbnb 5,0 von 5 (11 Bewertungen). Buchung: {a3}

## Weitere Seiten

- [Start]({b}/)
- [Die drei Unterkünfte im Überblick und Vergleich]({b}/haeuser.html)
- [Gastgeber und Bewertungen]({b}/gastgeber.html)
- [Wedel und Elbe]({b}/wedel-elbe.html): Willkomm-Höft, Elbdeich und Wedeler Marsch, Elbwanderweg, Yachthafen, Klövensteen, Roland, Barlach-Museum
- [Hamburg-Tipps]({b}/hamburg-tipps.html): Tipps entlang der S1 ab Wedel
- [Hamburg-Events 2027]({b}/events.html): Messen, Konzerte, Hafengeburtstag
- [Anreise und häufige Fragen]({b}/anreise-faq.html): S1, Flughafen, Auto, Buchung

## Kontakt

- E-Mail: {mail}
- Telefon: {tel}
""".format(stand=STAND, b=BASE, a1=A1, a3=A3, w2=W2, mail=MAIL, tel=TEL_SHOW)
    with open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(llms)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    for d in ("css", "js", "fonts"):
        os.makedirs(os.path.join(OUT, d))
    shutil.copy(os.path.join(HERE, "site3.css"), os.path.join(OUT, "css", "site.css"))
    for w in ("300", "400", "500"):
        shutil.copy(os.path.join(FONTS, "jost-latin-%s-normal.woff2" % w), os.path.join(OUT, "fonts"))
    with open(os.path.join(OUT, "js", "events.js"), "w", encoding="utf-8") as f:
        f.write(old.EVENTS_JS)
    with open(os.path.join(OUT, "js", "site.js"), "w", encoding="utf-8") as f:
        f.write(SITE_JS)
    for fn in (build_index, build_haeuser, build_01, build_02, build_03, build_host, build_wedel, build_hamburg,
               build_events, build_faq, build_legal):
        fn()
    build_meta_files()
    with open(os.path.join(HERE, "fotoliste.txt"), "w", encoding="utf-8") as f:
        seen = set()
        for pg, slot, desc, fmt in SHOTS:
            if slot not in seen:
                seen.add(slot)
                f.write("%-14s img/%-34s %-16s %s\n" % (pg, slot + ".jpg", fmt, desc))
    print("ok:", len(PAGES), "Seiten,", len(set(s[1] for s in SHOTS)), "Fotoplätze")


if __name__ == "__main__":
    main()
