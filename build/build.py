#!/usr/bin/env python3
"""Baut die statische stayHere-Seite nach OUT. BASE ist die Adresse, unter der die Seite liegt."""
import html
import json
import os
import shutil
import sys

BASE = "https://stayhere-eventzentrale-wedel.rmo1303.chatgpt.site"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/site"
HERE = os.path.dirname(os.path.abspath(__file__))
STAND = "16.11.2026"
LASTMOD = "2026-11-16"
MAIL = "rmo1303@gmail.com"
TEL_SHOW = "+49 155 61665448"
TEL = "+4915561665448"

AIRBNB_01 = "https://www.airbnb.de/rooms/23304974"
AIRBNB_02 = "https://www.airbnb.de/rooms/1154128730889110702"
AIRBNB_03 = "https://www.airbnb.de/rooms/1586664998214834160"
WUNDERFLATS_02 = ("https://wunderflats.com/de/moebliertes-apartment/charmantes-studio-in-wedel-naehe-hamburg-"
                  "nur-wenige-schritte-vom-s1-bahnhof-wedel-entfernt/6787ebcc0d3ecd0c19938710")
HVV = "https://www.hvv.de/de/"

NAV = [
    ("index.html", "Unterkünfte"),
    ("wedel-elbe.html", "Wedel &amp; Elbe"),
    ("hamburg-tipps.html", "Hamburg-Tipps"),
    ("events.html", "Events"),
    ("anreise-faq.html", "Anreise &amp; FAQ"),
]

ADDRESS = {
    "@type": "PostalAddress",
    "postalCode": "22880",
    "addressLocality": "Wedel",
    "addressRegion": "Schleswig-Holstein",
    "addressCountry": "DE",
}

PAGES = []  # (path, lastmod) für die Sitemap


def url_of(path):
    return BASE + "/" if path == "index.html" else BASE + "/" + path


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def crumbs_ld(trail):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url_of(path)}
            for i, (path, name) in enumerate(trail)
        ],
    }


def page(path, title, desc, body, jsonld=(), active=None, robots="index,follow,max-image-preview:large",
         scripts=(), in_sitemap=True):
    root = "../" * path.count("/")
    nav = "".join(
        '<li><a href="{r}{p}"{cur}>{n}</a></li>'.format(
            r=root, p=p, n=n, cur=' aria-current="page"' if p == active else "")
        for p, n in NAV
    )
    head_ld = "\n".join(ld(o) for o in jsonld)
    script_tags = "\n".join('<script src="{}{}" defer></script>'.format(root, s) for s in scripts)
    doc = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="stayHere Wedel">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}/stayhere-hero.jpg">
<meta name="theme-color" content="#183a35">
<link rel="stylesheet" href="{root}css/site.css">
{head_ld}
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="{root}index.html">stayHere<span>Wedel bei Hamburg</span></a>
<nav aria-label="Hauptnavigation"><ul class="nav">{nav}</ul></nav>
</div>
</header>
<main id="inhalt">
{body}
</main>
<footer class="site-footer">
<div class="wrap">
<div>
<h2>stayHere Wedel</h2>
<p>Drei privat geführte Unterkünfte in 22880 Wedel, Schleswig-Holstein, an der Elbe westlich von Hamburg.</p>
</div>
<div>
<h2>Kontakt</h2>
<ul>
<li>Ruppert Gerhard Matzke</li>
<li>E-Mail: <a href="mailto:{mail}">{mail}</a></li>
<li>Telefon: <a href="tel:{tel}">{tel_show}</a></li>
<li>Sprachen: Deutsch, Englisch, Spanisch</li>
</ul>
</div>
<div>
<h2>Buchen</h2>
<ul>
<li><a href="{a1}" rel="noopener">stayHere 01 auf Airbnb</a></li>
<li><a href="{a2}" rel="noopener">stayHere 02 auf Airbnb</a></li>
<li><a href="{w2}" rel="noopener">stayHere 02 auf Wunderflats (ab 1 Monat)</a></li>
<li><a href="{a3}" rel="noopener">stayHere 03 auf Airbnb</a></li>
</ul>
</div>
<p class="fine">Angaben zu Ausstattung, Wegen und Bewertungen laut den Inseraten, Stand {stand}. Preise und freie Termine stehen auf der jeweiligen Buchungsplattform. <a href="{root}impressum.html">Impressum und Datenschutz</a></p>
</div>
</footer>
{script_tags}
</body>
</html>
""".format(title=title, desc=html.escape(desc, quote=True), robots=robots, url=url_of(path), base=BASE,
           root=root, head_ld=head_ld, nav=nav, body=body.replace("{R}", root), mail=MAIL, tel=TEL,
           tel_show=TEL_SHOW, a1=AIRBNB_01, a2=AIRBNB_02, a3=AIRBNB_03, w2=WUNDERFLATS_02, stand=STAND,
           script_tags=script_tags)
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(doc)
    if in_sitemap:
        PAGES.append(path)


S1_STOPS = """<ol class="s1" aria-label="Wichtige Halte der S1 ab Wedel">
<li class="start"><strong>Wedel</strong><span>Endstation, hier steigst du ein</span></li>
<li><strong>Blankenese</strong><span>Treppenviertel, Elbstrand</span></li>
<li><strong>Altona</strong><span>Ottensen, Umstieg zu anderen S-Bahnen</span></li>
<li><strong>Reeperbahn</strong><span>St. Pauli</span></li>
<li><strong>Landungsbrücken</strong><span>Hafen, Fähren, U3 zur Elbphilharmonie</span></li>
<li><strong>Stadthausbrücke</strong><span>Speicherstadt, Miniatur Wunderland</span></li>
<li><strong>Jungfernstieg</strong><span>Alster, Innenstadt, U4 zur HafenCity</span></li>
<li><strong>Hauptbahnhof</strong><span>Fernzüge; die S1 fährt weiter zum Flughafen</span></li>
</ol>"""


# ---------------------------------------------------------------- Startseite
def build_index():
    body = """
<section class="hero">
<div class="wrap">
<p class="eyebrow">22880 Wedel · Schleswig-Holstein · Endstation der S1</p>
<h1>Ferienwohnungen in Wedel bei Hamburg</h1>
<p class="lead">stayHere sind drei privat geführte Unterkünfte in Wedel, zwischen der Elbe und dem Wald Klövensteen: eine Wohnung für 3 Gäste nahe der S-Bahn, eine Souterrainwohnung für 4 Gäste am Waldrand und ein Reihenhaus für 6 Gäste mit Garten. Die S1 fährt ab Wedel ohne Umsteigen in die Hamburger Innenstadt.</p>
<div class="actions">
<a class="btn" href="#vergleich">Unterkünfte vergleichen</a>
<a class="btn btn-ghost" href="{R}anreise-faq.html">Anreise und häufige Fragen</a>
</div>
""" + S1_STOPS + """
</div>
</section>

<section>
<div class="wrap">
<dl class="facts">
<div><dt>Platz</dt><dd>3, 4 oder 6 Gäste<small>je nach Unterkunft, alle mit eigener Küche</small></dd></div>
<div><dt>Zur S-Bahn</dt><dd class="num">ca. 5 Gehminuten<small>von stayHere 02 zum S-Bahnhof Wedel (S1)</small></dd></div>
<div><dt>Parken</dt><dd>Kostenlos<small>bei allen drei Unterkünften</small></dd></div>
<div><dt>Gastgeber</dt><dd>Superhost auf Airbnb<small class="num">seit 10 Jahren Gastgeber, 318 Bewertungen, Durchschnitt 4,86 (Stand """ + STAND + """)</small></dd></div>
</dl>
</div>
</section>

<section id="unterkuenfte" class="alt">
<div class="wrap">
<div class="section-head">
<h2>Die drei Unterkünfte</h2>
<p>Alle drei liegen in Wedel, jede in einer anderen Ecke der Stadt. Die genaue Adresse bekommst du nach der Buchung.</p>
</div>
<div class="cards">

<article class="card">
<p class="tag">stayHere 01 · bis 4 Gäste</p>
<h3><a href="{R}unterkuenfte/stayhere-01.html">Kinoabend am Klövensteen</a></h3>
<p>Souterrainwohnung mit eigenem Eingang in einem Einfamilienhaus, in einer ruhigen Wohngegend am Waldrand.</p>
<ul>
<li>2 Schlafzimmer, 4 Betten, 1 Bad</li>
<li>65-Zoll-Fernseher, Billard, Darts</li>
<li>Glasfaser-WLAN mit ca. 83 Mbit/s, Arbeitsplatz</li>
<li>Kostenloser Parkplatz auf dem Grundstück</li>
</ul>
<p class="rating num">Airbnb: 4,88 von 5 bei 191 Bewertungen</p>
<div class="actions">
<a class="btn" href="{R}unterkuenfte/stayhere-01.html">Details zu stayHere 01</a>
<a class="btn btn-ghost" href=\"""" + AIRBNB_01 + """\" rel="noopener">Auf Airbnb prüfen</a>
</div>
</article>

<article class="card">
<p class="tag">stayHere 02 · bis 3 Gäste</p>
<h3><a href="{R}unterkuenfte/stayhere-02.html">Südbalkon und Aufzug</a></h3>
<p>Helle 2-Zimmer-Wohnung mit 50 m² im Zentrum von Wedel, im 3. Stock mit Aufzug, ca. 5 Gehminuten vom S-Bahnhof.</p>
<ul>
<li>1 Schlafzimmer, 2 Betten, 1 Bad</li>
<li>Sonniger Südbalkon, weitgehend stufenlos</li>
<li>Küche, Waschmaschine, WLAN, Arbeitsplatz</li>
<li>Kostenloser Stellplatz</li>
</ul>
<p class="rating num">Airbnb: 4,83 von 5 bei 90 Bewertungen</p>
<div class="actions">
<a class="btn" href="{R}unterkuenfte/stayhere-02.html">Details zu stayHere 02</a>
<a class="btn btn-ghost" href=\"""" + AIRBNB_02 + """\" rel="noopener">Auf Airbnb prüfen</a>
</div>
</article>

<article class="card">
<p class="tag">stayHere 03 · bis 6 Gäste</p>
<h3><a href="{R}unterkuenfte/stayhere-03.html">Reihenhaus mit Garten</a></h3>
<p>Ruhiges Reihenmittelhaus mit Garten für Familien und Gruppen, ca. 5 Gehminuten von der FH Wedel.</p>
<ul>
<li>4 Schlafzimmer, 6 Betten, 1,5 Bäder</li>
<li>Garten, Küche mit Geschirrspüler, Waschmaschine</li>
<li>WLAN, Arbeitsplatz, Fernseher mit Fire TV Stick</li>
<li>Reservierter kostenloser Stellplatz am Haus</li>
</ul>
<p class="rating num">Airbnb: 5,0 von 5 bei 11 Bewertungen</p>
<div class="actions">
<a class="btn" href="{R}unterkuenfte/stayhere-03.html">Details zu stayHere 03</a>
<a class="btn btn-ghost" href=\"""" + AIRBNB_03 + """\" rel="noopener">Auf Airbnb prüfen</a>
</div>
</article>

</div>
</div>
</section>

<section id="vergleich">
<div class="wrap">
<div class="section-head">
<h2>Vergleich auf einen Blick</h2>
<p class="muted small">Alle Angaben laut den Inseraten auf Airbnb und Wunderflats, Stand """ + STAND + """.</p>
</div>
<div class="table-scroll">
<table>
<thead>
<tr><th scope="col"></th><th scope="col">stayHere 01</th><th scope="col">stayHere 02</th><th scope="col">stayHere 03</th></tr>
</thead>
<tbody class="num">
<tr><th scope="row">Art</th><td>Souterrainwohnung</td><td>2-Zimmer-Wohnung, 50 m²</td><td>Reihenhaus</td></tr>
<tr><th scope="row">Gäste</th><td>bis 4</td><td>bis 3</td><td>bis 6</td></tr>
<tr><th scope="row">Schlafzimmer</th><td>2</td><td>1</td><td>4</td></tr>
<tr><th scope="row">Betten</th><td>3 Einzelbetten, 1 kleines Doppelbett</td><td>1 Doppelbett, 1 Einzelbett im Wohnzimmer</td><td>2 Doppelbetten, 4 Einzelbetten</td></tr>
<tr><th scope="row">Bäder</th><td>1</td><td>1</td><td>1,5</td></tr>
<tr><th scope="row">Lage in Wedel</th><td>Waldrand am Klövensteen</td><td>Zentrum, nahe der Elbe</td><td>Nähe FH Wedel</td></tr>
<tr><th scope="row">Zum S-Bahnhof Wedel</th><td>Weg ab der Adresse im HVV planen; Abholung bei später Ankunft möglich</td><td>ca. 5 Minuten zu Fuß</td><td>ca. 12 Minuten mit dem Bus</td></tr>
<tr><th scope="row">Parken</th><td>kostenlos auf dem Grundstück</td><td>kostenloser Stellplatz</td><td>1 reservierter Stellplatz am Haus</td></tr>
<tr><th scope="row">Draußen</th><td>Wald vor der Tür</td><td>Südbalkon, Gemeinschaftsgarten, Grillplatz</td><td>eigener Garten</td></tr>
<tr><th scope="row">Besonderheit</th><td>Großer Fernseher, Billard, Darts</td><td>Aufzug, weitgehend stufenlos</td><td>4 Schlafzimmer, Waschmaschine</td></tr>
<tr><th scope="row">Buchung</th><td><a href=\"""" + AIRBNB_01 + """\" rel="noopener">Airbnb</a></td><td><a href=\"""" + AIRBNB_02 + """\" rel="noopener">Airbnb</a>, ab 1 Monat <a href=\"""" + WUNDERFLATS_02 + """\" rel="noopener">Wunderflats</a></td><td><a href=\"""" + AIRBNB_03 + """\" rel="noopener">Airbnb</a></td></tr>
<tr><th scope="row">Airbnb-Bewertung</th><td>4,88 (191)</td><td>4,83 (90)</td><td>5,0 (11)</td></tr>
</tbody>
</table>
</div>
</div>
</section>

<section class="alt">
<div class="wrap">
<div class="section-head">
<h2>Welche Unterkunft passt zu dir?</h2>
</div>
<div class="faq">
<div><h3>Zu zweit oder zu dritt, ohne Auto</h3><p>Nimm <a href="{R}unterkuenfte/stayhere-02.html">stayHere 02</a>. Zum S-Bahnhof Wedel gehst du etwa 5 Minuten, und die S1 fährt von dort ohne Umsteigen nach Altona, zu den Landungsbrücken und zum Hauptbahnhof.</p></div>
<div><h3>Familie oder Gruppe bis 6 Personen</h3><p><a href="{R}unterkuenfte/stayhere-03.html">stayHere 03</a> hat 4 Schlafzimmer, 1,5 Bäder, eine Waschmaschine und einen eigenen Garten.</p></div>
<div><h3>Ruhe am Wald und ein Abend mit Billard</h3><p><a href="{R}unterkuenfte/stayhere-01.html">stayHere 01</a> liegt am Waldrand des Klövensteen und hat einen 65-Zoll-Fernseher, Darts und einen Billardtisch. Der Billardtisch steht im Winter nicht zur Verfügung.</p></div>
<div><h3>Besuch an der FH Wedel</h3><p>Von <a href="{R}unterkuenfte/stayhere-03.html">stayHere 03</a> gehst du etwa 5 Minuten zur Fachhochschule Wedel.</p></div>
<div><h3>Wohnen auf Zeit ab einem Monat</h3><p><a href="{R}unterkuenfte/stayhere-02.html">stayHere 02</a> kannst du über Wunderflats für 1 bis 6 Monate mieten, zum Beispiel für ein Projekt, ein Praktikum oder die Zeit zwischen zwei Wohnungen.</p></div>
</div>
</div>
</section>

<section id="lage">
<div class="wrap">
<div class="section-head">
<h2>Von der Elbe bis zum Wald</h2>
<p>Wedel liegt in Schleswig-Holstein direkt an der Hamburger Stadtgrenze. Im Süden fließt die Elbe mit Deich und Marsch, im Norden beginnt der Wald Klövensteen. Dazwischen liegen die drei Unterkünfte.</p>
</div>
<ol class="zones">
<li><h3>Elbe und Deich</h3><p>Schulauer Fährhaus mit der Schiffsbegrüßungsanlage Willkomm-Höft, Strandbad, Hamburger Yachthafen und der Elbdeich in Richtung Wedeler Marsch.</p><p class="where">Von stayHere 03 ca. 12 Minuten mit dem Bus</p></li>
<li><h3>Zentrum und S-Bahnhof</h3><p>Bahnhofstraße mit Cafés, Apotheken und Geschäften. Das Ernst-Barlach-Museum liegt um die Ecke.</p><p class="where">stayHere 02, ca. 5 Gehminuten zur S1</p></li>
<li><h3>Rund um die FH Wedel</h3><p>Wohngebiet mit Supermarkt und Bushaltestelle in etwa 5 Gehminuten. Riedemanns Park erreichst du in etwa 10 Minuten zu Fuß.</p><p class="where">stayHere 03</p></li>
<li><h3>Waldrand am Klövensteen</h3><p>Ruhige Wohngegend, der Wald beginnt direkt nebenan. Der Badesee Holm liegt etwa 8 Autominuten entfernt.</p><p class="where">stayHere 01</p></li>
</ol>
</div>
</section>

<section class="alt">
<div class="wrap split">
<div class="stack">
<h2>Dein Gastgeber</h2>
<p>Ruppert Gerhard Matzke vermietet die drei Unterkünfte privat und ist auf Airbnb als Superhost ausgezeichnet. Er antwortet meist innerhalb einer Stunde und spricht Deutsch, Englisch und Spanisch.</p>
<p>Wenn du spät ankommst, holt er dich nach Absprache am S-Bahnhof Wedel ab.</p>
</div>
<dl class="ways num">
<div><dt>Gastgeber seit</dt><dd>10 Jahren</dd></div>
<div><dt>Bewertungen als Gastgeber</dt><dd>318, Durchschnitt 4,86</dd></div>
<div><dt>Antwortrate</dt><dd>100 %</dd></div>
<div><dt>Quelle</dt><dd>Airbnb-Profil, Stand """ + STAND + """</dd></div>
</dl>
</div>
</section>

<section>
<div class="wrap">
<div class="section-head"><h2>Aufenthalt planen</h2></div>
<div class="linkcards">
<a href="{R}wedel-elbe.html"><strong>Wedel und Elbe</strong><span>Willkomm-Höft, Elbdeich, Wedeler Marsch, Yachthafen und Klövensteen</span></a>
<a href="{R}hamburg-tipps.html"><strong>Hamburg-Tipps</strong><span>Speicherstadt und HafenCity mit der S1 ab Wedel</span></a>
<a href="{R}events.html"><strong>Hamburg-Events</strong><span>Messen, Konzerte und Hafengeburtstag 2027</span></a>
<a href="{R}anreise-faq.html"><strong>Anreise und FAQ</strong><span>S1, Flughafen, Auto, FH Wedel und Buchung</span></a>
</div>
</div>
</section>
"""
    business = {
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "@id": BASE + "/#stayhere",
        "name": "stayHere Wedel",
        "description": "Drei privat geführte Ferienunterkünfte in Wedel bei Hamburg für 3, 4 und 6 Gäste, "
                       "nahe S-Bahn S1, Elbe und Klövensteen.",
        "url": BASE + "/",
        "image": BASE + "/stayhere-hero.jpg",
        "telephone": TEL_SHOW,
        "email": MAIL,
        "address": ADDRESS,
        "knowsLanguage": ["de", "en", "es"],
        "founder": {"@type": "Person", "name": "Ruppert Gerhard Matzke"},
        "sameAs": [AIRBNB_01, AIRBNB_02, AIRBNB_03, WUNDERFLATS_02],
    }
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "stayHere-Unterkünfte in Wedel",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen",
             "url": url_of("unterkuenfte/stayhere-01.html")},
            {"@type": "ListItem", "position": 2, "name": "stayHere 02: Wohnung für 3 Gäste nahe der S-Bahn",
             "url": url_of("unterkuenfte/stayhere-02.html")},
            {"@type": "ListItem", "position": 3, "name": "stayHere 03: Reihenhaus für 6 Gäste mit Garten",
             "url": url_of("unterkuenfte/stayhere-03.html")},
        ],
    }
    website = {"@context": "https://schema.org", "@type": "WebSite", "name": "stayHere Wedel", "url": BASE + "/",
               "inLanguage": "de"}
    page("index.html",
         "Ferienwohnungen in Wedel bei Hamburg | stayHere",
         "Drei Ferienunterkünfte in Wedel bei Hamburg für 3, 4 und 6 Gäste: nahe S-Bahn S1, Elbe und Klövensteen, "
         "mit Küche und kostenlosem Parkplatz.",
         body, jsonld=[business, item_list, website], active="index.html")


# ---------------------------------------------------------------- Unterkünfte
def rental_ld(path, name, desc, guests, bedrooms, baths, beds, amenities, same_as, size=None, rooms=None):
    acc = {
        "@type": "Accommodation",
        "additionalType": "EntirePlace",
        "occupancy": {"@type": "QuantitativeValue", "value": guests},
        "numberOfBedrooms": bedrooms,
        "numberOfBathroomsTotal": baths,
        "bed": [{"@type": "BedDetails", "numberOfBeds": n, "typeOfBed": t} for n, t in beds],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": a, "value": True} for a in amenities],
    }
    if size:
        acc["floorSize"] = {"@type": "QuantitativeValue", "value": size, "unitCode": "MTK"}
    if rooms:
        acc["numberOfRooms"] = rooms
    return {
        "@context": "https://schema.org",
        "@type": "VacationRental",
        "@id": url_of(path) + "#unterkunft",
        "name": name,
        "description": desc,
        "url": url_of(path),
        "image": BASE + "/stayhere-hero.jpg",
        "address": ADDRESS,
        "telephone": TEL_SHOW,
        "knowsLanguage": ["de", "en", "es"],
        "containsPlace": acc,
        "sameAs": same_as,
        "brand": {"@type": "Brand", "name": "stayHere Wedel"},
    }


OTHERS = {
    "01": ('<a href="{R}unterkuenfte/stayhere-01.html"><strong>stayHere 01</strong>'
           '<span>Souterrainwohnung für 4 Gäste am Klövensteen</span></a>'),
    "02": ('<a href="{R}unterkuenfte/stayhere-02.html"><strong>stayHere 02</strong>'
           '<span>Wohnung für 3 Gäste, 5 Gehminuten zur S-Bahn</span></a>'),
    "03": ('<a href="{R}unterkuenfte/stayhere-03.html"><strong>stayHere 03</strong>'
           '<span>Reihenhaus für 6 Gäste mit Garten</span></a>'),
}


def detail_tail(me):
    others = "".join(v for k, v in OTHERS.items() if k != me)
    return """
<section>
<div class="wrap">
<div class="section-head"><h2>Die anderen Unterkünfte</h2></div>
<div class="linkcards">""" + others + """
<a href="{R}index.html#vergleich"><strong>Alle drei vergleichen</strong><span>Gäste, Betten, Wege und Parken in einer Tabelle</span></a>
</div>
</div>
</section>
"""


def head(crumb, h1, lead):
    return """
<div class="page-head">
<div class="wrap">
<ol class="crumbs"><li><a href="{R}index.html">Unterkünfte</a></li><li>""" + crumb + """</li></ol>
<h1>""" + h1 + """</h1>
<p class="lead">""" + lead + """</p>
</div>
</div>
"""


def build_01():
    path = "unterkuenfte/stayhere-01.html"
    body = head("stayHere 01",
                "stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen",
                "Die Wohnung liegt im Souterrain eines Einfamilienhauses in einer ruhigen Wohngegend von Wedel, "
                "direkt am Waldrand des Klövensteen. Sie hat einen eigenen Eingang, zwei Schlafzimmer, eine voll "
                "ausgestattete Küche und einen kostenlosen Parkplatz auf dem Grundstück.") + """
<section>
<div class="wrap stack">
<dl class="facts">
<div><dt>Gäste</dt><dd class="num">bis 4</dd></div>
<div><dt>Schlafzimmer</dt><dd class="num">2<small>3 Einzelbetten und 1 kleines Doppelbett</small></dd></div>
<div><dt>Bad</dt><dd class="num">1<small>eigenes Bad mit Dusche und WC</small></dd></div>
<div><dt>Airbnb-Bewertung</dt><dd class="num">4,88 von 5<small>191 Bewertungen, 92 % mit 5 Sternen (Stand """ + STAND + """)</small></dd></div>
</dl>
</div>
</section>

<section class="alt">
<div class="wrap split">
<div class="stack">
<h2>Ausstattung</h2>
<ul class="checks">
<li>Eigener, separater Eingang</li>
<li>Küche mit Herd, Kühlschrank mit Tiefkühlfächern, Mikrowelle, Geschirrspüler, Kaffeemaschine, Toaster und Wasserkocher</li>
<li>65-Zoll-Fernseher und Stereoanlage für den Kinoabend</li>
<li>Billardtisch und Dartscheibe</li>
<li>Glasfaser-WLAN mit ca. 83 Mbit/s</li>
<li>Arbeitsplatz</li>
<li>Kostenloser Parkplatz auf dem Grundstück</li>
</ul>
<p class="note">Der Billardtisch steht im Winter nicht zur Verfügung. Für die übrige Zeit bestätigt dir der Gastgeber die Nutzung vor der Anreise.</p>
</div>
<div class="stack">
<h2>Schlafen</h2>
<ul class="checks">
<li>Schlafzimmer 1: drei Einzelbetten</li>
<li>Schlafzimmer 2: ein kleines Doppelbett</li>
</ul>
<p>Damit passt die Wohnung für Familien, für drei oder vier Freunde und für Kolleginnen und Kollegen, die getrennte Betten brauchen.</p>
</div>
</div>
</section>

<section>
<div class="wrap split">
<div class="stack">
<h2>Lage und Wege</h2>
<p>Der Wald Klövensteen grenzt direkt an die Wohngegend. An der Elbe liegen das Schulauer Fährhaus mit dem Willkomm-Höft, das Strandbad und der Hamburger Yachthafen. Bäckereien, Supermärkte und der Wochenmarkt sind in Wedel.</p>
<dl class="ways num">
<div><dt>Klövensteen</dt><dd>grenzt direkt an</dd></div>
<div><dt>Badesee Holm</dt><dd>ca. 8 Minuten mit dem Auto</dd></div>
<div><dt>S-Bahnhof Wedel (S1)</dt><dd>Weg ab der Adresse im <a href=\"""" + HVV + """\" rel="noopener">HVV</a> planen</dd></div>
<div><dt>Späte Ankunft</dt><dd>Abholung am S-Bahnhof nach Absprache</dd></div>
</dl>
<p class="muted small">Die genaue Adresse bekommst du nach der Buchung.</p>
</div>
<div class="book">
<h2>Preise und freie Termine</h2>
<p>stayHere 01 buchst du über Airbnb. Dort siehst du den Preis für deine Reisedaten, die freien Nächte und die Stornobedingungen.</p>
<div class="actions"><a class="btn" href=\"""" + AIRBNB_01 + """\" rel="noopener">stayHere 01 auf Airbnb ansehen</a></div>
<p class="muted small">Fragen vorab: <a href="mailto:""" + MAIL + """\">""" + MAIL + """</a> oder <a href="tel:""" + TEL + """\">""" + TEL_SHOW + """</a></p>
</div>
</div>
</section>
""" + detail_tail("01")
    name = "stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen in Wedel"
    desc = ("Souterrainwohnung mit eigenem Eingang in Wedel bei Hamburg für 4 Gäste: 2 Schlafzimmer, Küche, Billard, "
            "schnelles WLAN und Parkplatz am Waldrand.")
    rental = rental_ld(path, name, desc, 4, 2, 1, [(3, "Einzelbett"), (1, "Kleines Doppelbett")],
                       ["Eigener Eingang", "Küche", "Geschirrspüler", "WLAN (Glasfaser)", "Arbeitsplatz",
                        "Fernseher (65 Zoll)", "Billardtisch", "Dartscheibe", "Kostenloser Parkplatz"],
                       [AIRBNB_01])
    page(path, "Ferienwohnung für 4 Gäste am Klövensteen in Wedel | stayHere 01", desc, body,
         jsonld=[rental, crumbs_ld([("index.html", "Unterkünfte"), (path, "stayHere 01")])], active="index.html")


def build_02():
    path = "unterkuenfte/stayhere-02.html"
    body = head("stayHere 02",
                "stayHere 02: Wohnung für 3 Gäste, 5 Gehminuten zur S-Bahn",
                "Die helle 2-Zimmer-Wohnung mit 50 m² liegt im Zentrum von Wedel, nahe der Elbe. Sie ist im "
                "3. Stock, mit dem Aufzug erreichbar und hat einen sonnigen Südbalkon. Zum S-Bahnhof Wedel gehst "
                "du etwa 5 Minuten, von dort fährt die S1 ohne Umsteigen nach Hamburg.") + """
<section>
<div class="wrap stack">
<dl class="facts">
<div><dt>Gäste</dt><dd class="num">bis 3</dd></div>
<div><dt>Größe</dt><dd class="num">50 m², 2 Zimmer<small>1 Schlafzimmer, Wohnzimmer als Durchgangszimmer</small></dd></div>
<div><dt>Zur S1</dt><dd class="num">ca. 5 Gehminuten<small>S-Bahnhof Wedel</small></dd></div>
<div><dt>Airbnb-Bewertung</dt><dd class="num">4,83 von 5<small>90 Bewertungen (Stand """ + STAND + """)</small></dd></div>
</dl>
</div>
</section>

<section class="alt">
<div class="wrap split">
<div class="stack">
<h2>Ausstattung</h2>
<ul class="checks">
<li>Südbalkon mit Sitzplatz, laut Inserat mit Blick auf Wedeler Au und Elbe</li>
<li>Voll ausgestattete Küche mit Herd, Backofen, Geschirrspüler, Mikrowelle, Kühlschrank und Gefrierfach</li>
<li>Waschmaschine, Bügeleisen und Staubsauger</li>
<li>WLAN, Fernseher und Arbeitsplatz</li>
<li>Bettwäsche und Handtücher</li>
<li>Gemeinschaftsgarten mit Grillplatz</li>
<li>Kostenloser Stellplatz, laut Wunderflats in der Tiefgarage</li>
</ul>
</div>
<div class="stack">
<h2>Schlafen</h2>
<ul class="checks">
<li>Schlafzimmer: ein Doppelbett (Queensize)</li>
<li>Wohnzimmer: ein Einzelbett</li>
</ul>
<h2>Zugang ohne Treppen</h2>
<p>Die Wohnung liegt im 3. Stock und ist mit dem Aufzug erreichbar. Der Weg zum Eingang ist beleuchtet. Innen ist sie weitgehend stufenlos, nur an der Dusche und am Balkon gibt es je eine kleine Stufe.</p>
<p class="note">Die Wohnung ist barrierearm, aber nicht barrierefrei. Wenn du auf bestimmte Maße oder Hilfen angewiesen bist, kläre das bitte vor der Buchung mit dem Gastgeber.</p>
<p>Das Haus ist an eine Seniorenresidenz angeschlossen. Entsprechend ruhig ist es im Haus.</p>
</div>
</div>
</section>

<section>
<div class="wrap split">
<div class="stack">
<h2>Lage und Wege</h2>
<p>Du wohnst im Zentrum von Wedel. Geschäfte sind in der Nähe, das Ernst-Barlach-Museum erreichst du zu Fuß. Die S1 fährt vom S-Bahnhof Wedel direkt nach Altona, zur Reeperbahn, zu den Landungsbrücken und zum Hauptbahnhof und weiter zum Flughafen.</p>
<dl class="ways num">
<div><dt>S-Bahnhof Wedel (S1)</dt><dd>ca. 5 Minuten zu Fuß</dd></div>
<div><dt>Ernst-Barlach-Museum</dt><dd>kurzer Fußweg</dd></div>
<div><dt>Geschäfte</dt><dd>in der Nähe</dd></div>
<div><dt>Späte Ankunft</dt><dd>Abholung am S-Bahnhof nach Absprache</dd></div>
</dl>
<p class="muted small">Die genaue Adresse bekommst du nach der Buchung.</p>
</div>
<div class="book">
<h2>Preise und freie Termine</h2>
<h3>Für einige Nächte: Airbnb</h3>
<p>Auf Airbnb siehst du den Preis für deine Reisedaten und die freien Nächte.</p>
<div class="actions"><a class="btn" href=\"""" + AIRBNB_02 + """\" rel="noopener">stayHere 02 auf Airbnb ansehen</a></div>
<h3>Ab einem Monat: Wunderflats</h3>
<p class="num">Für 1 bis 6 Monate mietest du die Wohnung möbliert über Wunderflats. Die Monatsmiete beträgt dort 1.680 € einschließlich Nebenkosten, Heizung, Strom und Internet, die Kaution 500 € (Stand """ + STAND + """). Haustiere und Rauchen sind nicht erlaubt, ab 22 Uhr gilt Ruhe.</p>
<div class="actions"><a class="btn btn-ghost" href=\"""" + WUNDERFLATS_02 + """\" rel="noopener">stayHere 02 auf Wunderflats ansehen</a></div>
<p class="muted small">Fragen vorab: <a href="mailto:""" + MAIL + """\">""" + MAIL + """</a> oder <a href="tel:""" + TEL + """\">""" + TEL_SHOW + """</a></p>
</div>
</div>
</section>
""" + detail_tail("02")
    name = "stayHere 02: Wohnung für 3 Gäste mit Südbalkon und Aufzug in Wedel"
    desc = ("2-Zimmer-Wohnung mit 50 m² im Zentrum von Wedel für bis zu 3 Gäste: Südbalkon, Aufzug, Küche, "
            "kostenloser Stellplatz, ca. 5 Gehminuten zur S-Bahn S1 nach Hamburg.")
    rental = rental_ld(path, name, desc, 3, 1, 1, [(1, "Doppelbett (Queensize)"), (1, "Einzelbett")],
                       ["Südbalkon", "Aufzug", "Küche", "Geschirrspüler", "Waschmaschine", "WLAN", "Arbeitsplatz",
                        "Fernseher", "Gemeinschaftsgarten mit Grillplatz", "Kostenloser Stellplatz"],
                       [AIRBNB_02, WUNDERFLATS_02], size=50, rooms=2)
    page(path, "Ferienwohnung für 3 Gäste nahe S-Bahn Wedel | stayHere 02", desc, body,
         jsonld=[rental, crumbs_ld([("index.html", "Unterkünfte"), (path, "stayHere 02")])], active="index.html")


def build_03():
    path = "unterkuenfte/stayhere-03.html"
    body = head("stayHere 03",
                "stayHere 03: Reihenhaus für 6 Gäste mit Garten",
                "Das ruhige Reihenmittelhaus in Wedel hat vier Schlafzimmer, anderthalb Bäder, eine voll "
                "ausgestattete Küche und einen eigenen Garten. Die FH Wedel, ein Supermarkt und die Bushaltestelle "
                "liegen jeweils etwa 5 Gehminuten entfernt.") + """
<section>
<div class="wrap stack">
<dl class="facts">
<div><dt>Gäste</dt><dd class="num">bis 6</dd></div>
<div><dt>Schlafzimmer</dt><dd class="num">4<small>2 Doppelbetten und 4 Einzelbetten</small></dd></div>
<div><dt>Bäder</dt><dd class="num">1,5</dd></div>
<div><dt>Airbnb-Bewertung</dt><dd class="num">5,0 von 5<small>11 Bewertungen (Stand """ + STAND + """)</small></dd></div>
</dl>
</div>
</section>

<section class="alt">
<div class="wrap split">
<div class="stack">
<h2>Ausstattung</h2>
<ul class="checks">
<li>Eigener Garten</li>
<li>Voll ausgestattete Küche mit Geschirrspüler, Kochgeschirr und Geschirr</li>
<li>Waschmaschine im Haus</li>
<li>WLAN und Arbeitsplatz</li>
<li>Fernseher mit Amazon Fire TV Stick oder Satellitenempfang</li>
<li>Neue, gut dämmende Fenster</li>
<li>Ein reservierter, kostenloser Stellplatz direkt am Haus</li>
</ul>
</div>
<div class="stack">
<h2>Schlafen</h2>
<ul class="checks">
<li>Schlafzimmer 1: ein Doppelbett</li>
<li>Schlafzimmer 2: ein Doppelbett</li>
<li>Schlafzimmer 3: zwei Einzelbetten</li>
<li>Schlafzimmer 4: zwei Einzelbetten</li>
</ul>
<p>Vier getrennte Schlafzimmer machen das Haus passend für Familien mit größeren Kindern, zwei befreundete Paare mit Kindern oder ein Projektteam.</p>
<h2>Ankunft</h2>
<p>Den Schlüssel übergibt dir der Gastgeber persönlich, oder du holst ihn aus einer Schlüsselbox.</p>
</div>
</div>
</section>

<section>
<div class="wrap split">
<div class="stack">
<h2>Lage und Wege</h2>
<p>Das Haus liegt in einem Wohngebiet nahe der Fachhochschule Wedel. Zum S-Bahnhof und an die Elbe fährst du mit dem Bus.</p>
<dl class="ways num">
<div><dt>FH Wedel</dt><dd>ca. 5 Minuten zu Fuß</dd></div>
<div><dt>Bushaltestelle und EDEKA</dt><dd>ca. 5 Minuten zu Fuß</dd></div>
<div><dt>Riedemanns Park</dt><dd>ca. 10 Minuten zu Fuß</dd></div>
<div><dt>S-Bahnhof Wedel (S1) und Bahnhofstraße</dt><dd>ca. 12 Minuten mit dem Bus</dd></div>
<div><dt>Elbe, Schulauer Fährhaus, Willkomm-Höft</dt><dd>ca. 12 Minuten mit dem Bus</dd></div>
<div><dt>Späte Ankunft</dt><dd>Abholung am S-Bahnhof nach Absprache</dd></div>
</dl>
<p class="muted small">Die genaue Adresse bekommst du nach der Buchung.</p>
</div>
<div class="book">
<h2>Preise und freie Termine</h2>
<p>stayHere 03 buchst du über Airbnb. Dort siehst du den Preis für deine Reisedaten, die freien Nächte und die Stornobedingungen.</p>
<div class="actions"><a class="btn" href=\"""" + AIRBNB_03 + """\" rel="noopener">stayHere 03 auf Airbnb ansehen</a></div>
<p class="muted small">Fragen vorab: <a href="mailto:""" + MAIL + """\">""" + MAIL + """</a> oder <a href="tel:""" + TEL + """\">""" + TEL_SHOW + """</a></p>
</div>
</div>
</section>
""" + detail_tail("03")
    name = "stayHere 03: Reihenhaus für 6 Gäste mit Garten in Wedel"
    desc = ("Ruhiges Reihenhaus in Wedel bei Hamburg für bis zu 6 Gäste: 4 Schlafzimmer, 1,5 Bäder, Garten, "
            "Waschmaschine und Stellplatz am Haus, ca. 5 Gehminuten zur FH Wedel.")
    rental = rental_ld(path, name, desc, 6, 4, 1.5, [(2, "Doppelbett"), (4, "Einzelbett")],
                       ["Garten", "Küche", "Geschirrspüler", "Waschmaschine", "WLAN", "Arbeitsplatz",
                        "Fernseher mit Fire TV Stick", "Kostenloser Stellplatz am Haus"],
                       [AIRBNB_03])
    page(path, "Ferienhaus für 6 Gäste mit Garten in Wedel | stayHere 03", desc, body,
         jsonld=[rental, crumbs_ld([("index.html", "Unterkünfte"), (path, "stayHere 03")])], active="index.html")


# ---------------------------------------------------------------- Themenseiten
def simple_head(h1, lead):
    return """
<div class="page-head">
<div class="wrap">
<h1>""" + h1 + """</h1>
<p class="lead">""" + lead + """</p>
</div>
</div>
"""


def places_ld(name, places):
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "item": {"@type": "TouristAttraction", "name": n, "url": u,
                      "address": {"@type": "PostalAddress", "addressLocality": loc, "addressCountry": "DE"}}}
            for i, (n, u, loc) in enumerate(places)
        ],
    }


def build_wedel():
    path = "wedel-elbe.html"
    body = simple_head("Wedel und die Elbe: Ausflugsziele vor der Tür",
                       "Große Schiffe am Willkomm-Höft, der Elbdeich mit der weiten Wedeler Marsch, der Yachthafen "
                       "und der Wald Klövensteen liegen alle in oder direkt bei Wedel. Plane dafür ruhig einen "
                       "ganzen Tag ohne Hamburg ein.") + """
<section id="ausfluege">
<div class="wrap">
<ol class="items">
<li class="item"><h2>Willkomm-Höft am Schulauer Fährhaus</h2>
<p>An der Schiffsbegrüßungsanlage werden die Schiffe verabschiedet und begrüßt, die auf der Elbe nach Hamburg fahren oder von dort kommen. Vom Ufer aus siehst du Containerschiffe und Kreuzfahrtschiffe aus der Nähe.</p>
<p class="meta">Von stayHere 03 ca. 12 Minuten mit dem Bus.</p>
<p class="links"><a href="https://www.wedel.de/tourismus-freizeit/sehenswertes-ausfluege/schiffsbegruessungsanlage-willkomm-hoeft" rel="noopener">Besucherinfos der Stadt Wedel</a></p></li>

<li class="item"><h2>Elbdeich und Wedeler Marsch</h2>
<p>Westlich von Wedel beginnt die Deichlandschaft der Elbmarschen. Auf dem Deich gehst oder radelst du zwischen Elbe und Marschwiesen in Richtung Fährmannssand und Haseldorfer Marsch. In der Wedeler Marsch betreut der NABU eine Vogelstation mit Beobachtungsständen. Im Winter rasten dort Tausende Gänse.</p>
<p class="meta">Die Vogelstation hat nur an einzelnen Wochentagen geöffnet. Die Zeiten stehen beim NABU.</p>
<p class="links"><a href="https://www.nabu.de/natur-und-landschaft/natur-erleben/nabu-zentren/hamburg/24059.html" rel="noopener">NABU-Vogelstation Wedeler Marsch</a></p></li>

<li class="item"><h2>Elbwanderweg</h2>
<p>Der Weg startet am Schulauer Fährhaus und führt am Wasser entlang nach Osten in Richtung Blankenese. Wie weit du gehst, entscheidest du unterwegs. Zurück kommst du zu Fuß oder ab Blankenese mit der S1.</p>
<p class="links"><a href="https://www.wedel.de/tourismus-freizeit/elbe-maritimes/elbwanderweg" rel="noopener">Elbwanderweg bei der Stadt Wedel</a></p></li>

<li class="item"><h2>Hamburger Yachthafen</h2>
<p>Der Hamburger Yachthafen liegt trotz seines Namens in Wedel. Ein Spaziergang durch den Hafenbereich lohnt sich wegen der vielen Segel- und Motorboote. Bitte beachte die Zugangsregeln vor Ort.</p>
<p class="links"><a href="https://www.hamburger-yachthafen.de/infos/standort" rel="noopener">Standort und Anreise</a></p></li>

<li class="item"><h2>Klövensteen und Wildgehege</h2>
<p>Der Wald Klövensteen grenzt an Wedel. stayHere 01 liegt direkt am Waldrand. Das Wildgehege gehört zu Hamburg-Rissen. Prüfe vor dem Besuch die Öffnungszeiten und mögliche Sperrungen.</p>
<p class="links"><a href="https://www.hamburg.de/politik-und-verwaltung/bezirke/altona/themen/umwelt-natur-klimaschutz/kloevensteen/wildgehege" rel="noopener">Wildgehege Klövensteen</a></p></li>

<li class="item"><h2>Strandbar 28° am Strandbad Wedel</h2>
<p>Die Strandbar liegt am Wedeler Strandbad direkt an der Elbe. Die Öffnungszeiten hängen vom Wetter ab. Reservierungen bestätigt der Betreiber.</p>
<p class="links"><a href="https://28grad.com/" rel="noopener">28grad.com</a><a href="https://28grad.com/kontakt-faq/" rel="noopener">Reservierung anfragen</a></p></li>
</ol>
</div>
</section>

<section class="alt">
<div class="wrap">
<div class="section-head"><h2>Passende Unterkunft finden</h2></div>
<div class="linkcards">""" + "".join(OTHERS.values()) + """</div>
</div>
</section>
"""
    places = places_ld("Ausflugsziele in Wedel an der Elbe", [
        ("Schiffsbegrüßungsanlage Willkomm-Höft",
         "https://www.wedel.de/tourismus-freizeit/sehenswertes-ausfluege/schiffsbegruessungsanlage-willkomm-hoeft", "Wedel"),
        ("NABU-Vogelstation Wedeler Marsch",
         "https://www.nabu.de/natur-und-landschaft/natur-erleben/nabu-zentren/hamburg/24059.html", "Wedel"),
        ("Elbwanderweg", "https://www.wedel.de/tourismus-freizeit/elbe-maritimes/elbwanderweg", "Wedel"),
        ("Hamburger Yachthafen", "https://www.hamburger-yachthafen.de/infos/standort", "Wedel"),
        ("Wildgehege Klövensteen",
         "https://www.hamburg.de/politik-und-verwaltung/bezirke/altona/themen/umwelt-natur-klimaschutz/kloevensteen/wildgehege",
         "Hamburg"),
        ("Strandbar 28° am Strandbad Wedel", "https://28grad.com/", "Wedel"),
    ])
    page(path, "Wedel &amp; Elbe: Willkomm-Höft, Elbdeich, Klövensteen | stayHere",
         "Ausflugsziele in Wedel: Willkomm-Höft, Elbdeich und Wedeler Marsch, Elbwanderweg, Yachthafen, Klövensteen "
         "und Strandbar 28°, mit offiziellen Links.",
         body, jsonld=[places, crumbs_ld([("index.html", "Unterkünfte"), (path, "Wedel & Elbe")])], active=path)


def build_hamburg():
    path = "hamburg-tipps.html"
    body = simple_head("Hamburg-Tipps: Speicherstadt und HafenCity ab Wedel",
                       "Vier Ziele, die du von Wedel aus mit der S1 erreichst, jeweils mit dem Weg ab dem "
                       "S-Bahnhof Wedel und dem Link zu den offiziellen Tickets.") + """
<section>
<div class="wrap">
<ol class="items">
<li class="item"><h2>Miniatur Wunderland</h2>
<p class="meta">Speicherstadt, Kehrwieder 2</p>
<p>Modelleisenbahnen und Miniaturwelten auf mehreren Etagen. Reserviere deine Wunschzeit am besten vorab.</p>
<p><strong>Ab Wedel:</strong> S1 bis Stadthausbrücke, danach laut Anbieter etwa 11 Minuten zu Fuß.</p>
<p class="links"><a href="https://www.miniatur-wunderland.de/tickets" rel="noopener">Tickets</a><a href="https://www.miniatur-wunderland.de/besuchen/wunderland-vor-ort/anfahrt" rel="noopener">Anfahrt</a></p></li>

<li class="item"><h2>Hamburg Dungeon</h2>
<p class="meta">Speicherstadt, Kehrwieder 2</p>
<p>Schauspiel und Gruselgeschichten aus der Hamburger Geschichte. Buche ein Zeitfenster online und prüfe die Hinweise zu Alter und Sprache.</p>
<p><strong>Ab Wedel:</strong> S1 bis Stadthausbrücke, dann zu Fuß zum Kehrwieder.</p>
<p class="links"><a href="https://www.thedungeons.com/hamburg/tickets/" rel="noopener">Tickets</a><a href="https://www.thedungeons.com/hamburg/plane-deinen-besuch/plane-deinen-besuch/anreise/" rel="noopener">Anreise</a></p></li>

<li class="item"><h2>Elbphilharmonie Plaza</h2>
<p class="meta">HafenCity, Platz der Deutschen Einheit</p>
<p>Die Aussichtsplattform bietet einen Blick über Stadt und Hafen. Das Plaza-Ticket ist kein Konzertticket und enthält keine HVV-Fahrt.</p>
<p><strong>Ab Wedel:</strong> S1 bis Landungsbrücken, U3 bis Baumwall, dann zu Fuß.</p>
<p class="links"><a href="https://plazashop.elbphilharmonie.de/" rel="noopener">Plaza-Tickets</a><a href="https://www.elbphilharmonie.de/de/anfahrt" rel="noopener">Anfahrt</a></p></li>

<li class="item"><h2>Westfield Hamburg-Überseequartier</h2>
<p class="meta">HafenCity, nahe der Speicherstadt</p>
<p>Einkaufen, Essen und Freizeit unter einem Dach. Für den Einkauf brauchst du keine Reservierung.</p>
<p><strong>Ab Wedel:</strong> S1 bis Jungfernstieg, dann U4 Richtung Elbbrücken bis Überseequartier.</p>
<p class="links"><a href="https://www.westfield.com/de/germany/hamburg" rel="noopener">Infos und Angebote</a><a href="https://www.westfield.com/de/germany/hamburg/access" rel="noopener">Anfahrt</a></p></li>
</ol>
<p class="muted small" style="margin-top:1.5rem">Stand: 14.11.2026. Die Wege sind Vorschläge. Prüfe Fahrplan, Baustellen und Öffnungszeiten vor dem Besuch im <a href=\"""" + HVV + """\" rel="noopener">HVV</a> und beim Anbieter.</p>
</div>
</section>

<section class="alt">
<div class="wrap">
<div class="section-head"><h2>Die S1 ab Wedel</h2><p>Wedel ist die Endstation. Du steigst also immer in einen Zug, der dort startet.</p></div>
""" + S1_STOPS + """
</div>
</section>
"""
    places = places_ld("Hamburg-Tipps ab Wedel", [
        ("Miniatur Wunderland", "https://www.miniatur-wunderland.de/tickets", "Hamburg"),
        ("Hamburg Dungeon", "https://www.thedungeons.com/hamburg/tickets/", "Hamburg"),
        ("Elbphilharmonie Plaza", "https://plazashop.elbphilharmonie.de/", "Hamburg"),
        ("Westfield Hamburg-Überseequartier", "https://www.westfield.com/de/germany/hamburg", "Hamburg"),
    ])
    page(path, "Hamburg-Tipps ab Wedel: Speicherstadt &amp; HafenCity | stayHere",
         "Miniatur Wunderland, Hamburg Dungeon, Elbphilharmonie Plaza und Westfield Überseequartier: der Weg mit "
         "der S1 ab Wedel und die Links zu den offiziellen Tickets.",
         body, jsonld=[places, crumbs_ld([("index.html", "Unterkünfte"), (path, "Hamburg-Tipps")])], active=path)


EVENTS = [
    # (ISO-Start, ISO-Ende, Datumstext, Name, Art, Ort, Unterkünfte, URL, Hinweis)
    ("2027-01-20", "2027-01-21", "20.–21. Januar 2027", "HAMBURG OPEN (Medienmesse)", "Messe", "Hamburg Messe, Halle B6",
     ["01", "02"], "https://www.hamburg-open.de/", ""),
    ("2027-02-04", "2027-02-07", "4.–7. Februar 2027", "Reisen & Caravaning Hamburg", "Messe", "Hamburg Messe",
     ["02", "03"],
     "https://www.hamburg-messe.de/veranstaltungen/termine/veranstaltungsdetails/reisen-caravaning-hamburg-2027", ""),
    ("2027-03-12", "2027-03-16", "12.–16. März 2027", "INTERNORGA", "Messe", "Hamburg Messe",
     ["01", "02", "03"], "https://www.internorga.com/", ""),
    ("2027-04-25", "2027-04-25", "25. April 2027", "Haspa Marathon Hamburg", "Sport", "Messe und Innenstadt",
     ["02", "03"], "https://haspa-marathon-hamburg.de/", ""),
    ("2027-05-06", "2027-05-09", "6.–9. Mai 2027", "Hafengeburtstag Hamburg", "Hafenfest",
     "Landungsbrücken und Hafen", ["01", "02", "03"], "https://www.hamburg.de/freizeit/hafengeburtstag-hamburg",
     "Mit der S1 ab Wedel fährst du direkt bis Landungsbrücken. Rechne mit vollen Zügen und prüfe die letzte Rückfahrt."),
    ("2027-05-15", "2027-05-22", "15.–22. Mai 2027", "Hamburg Open (ATP-Tennis)", "Sport", "Rothenbaum",
     ["02", "03"], "https://hamburgopenatp500.com/", "Spielerfeld und Tagesprogramm stehen noch nicht fest."),
    ("2027-06-18", "2027-06-18", "18. Juni 2027", "Kings of Leon", "Konzert", "Barclays Arena",
     ["01", "02", "03"], "https://www.barclays-arena.de/events/kings-of-leon", ""),
    ("2027-07-09", "2027-07-10", "9.–10. Juli 2027", "ELBJAZZ", "Konzert", "Hamburger Hafen",
     ["02", "03"], "https://elbjazz.de/", "Das vollständige Programm steht noch aus."),
    ("2027-11-07", "2027-11-07", "7. November 2027", "POWERWOLF", "Konzert", "Arena am Volkspark",
     ["01", "03"], "https://www.barclays-arena.de/events/powerwolf", ""),
]


def build_events():
    path = "events.html"
    items = []
    ld_items = []
    for start, end, datetext, name, kind, place, accs, url, hint in EVENTS:
        acc_links = ", ".join(
            '<a href="{{R}}unterkuenfte/stayhere-{0}.html">stayHere {0}</a>'.format(a) for a in accs)
        items.append(
            '<li class="item event" data-kind="{kind}">'
            '<p class="date num"><time datetime="{start}">{datetext}</time><small>{kind}</small></p>'
            '<div class="body"><h2>{name}</h2><p class="meta">{place}</p>{hint}'
            '<p class="small">Passende Unterkünfte: {accs}</p>'
            '<p class="links"><a href="{url}" rel="noopener">Zur Seite des Veranstalters</a></p></div></li>'.format(
                kind=kind, start=start, datetext=datetext, name=html.escape(name), place=place,
                hint="<p>" + hint + "</p>" if hint else "", accs=acc_links, url=url))
        ld_items.append({
            "@type": "Event", "name": name, "startDate": start, "endDate": end,
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "location": {"@type": "Place", "name": place,
                         "address": {"@type": "PostalAddress", "addressLocality": "Hamburg", "addressCountry": "DE"}},
            "url": url,
        })
    body = simple_head("Hamburg-Events 2027: Messen, Konzerte und Hafengeburtstag",
                       "Diese Termine in Hamburg erreichst du von Wedel aus mit der S1. Zu jedem Termin findest du "
                       "den Link zum Veranstalter und die Unterkünfte, die dafür gut passen.") + """
<section id="events">
<div class="wrap">
<div class="filter" role="group" aria-label="Nach Art filtern">
<button type="button" id="filter-alle" data-filter="alle" aria-pressed="true">Alle</button>
<button type="button" id="filter-messe" data-filter="Messe" aria-pressed="false">Messen</button>
<button type="button" id="filter-konzert" data-filter="Konzert" aria-pressed="false">Konzerte</button>
<button type="button" id="filter-sport" data-filter="Sport" aria-pressed="false">Sport</button>
<button type="button" id="filter-hafenfest" data-filter="Hafenfest" aria-pressed="false">Hafenfest</button>
</div>
<ol class="items">
""" + "\n".join(items) + """
</ol>
<div class="note" style="margin-top:1.5rem">
<p>Die Termine stammen von den Seiten der Veranstalter, Stand 14.11.2026. Änderungen sind möglich.</p>
<p>stayHere verkauft keine Tickets. Eine Empfehlung bedeutet nicht, dass die Unterkunft an dem Termin frei ist. Freie Nächte siehst du auf Airbnb und Wunderflats.</p>
</div>
</div>
</section>
"""
    events = {"@context": "https://schema.org", "@type": "ItemList", "name": "Hamburg-Events 2027",
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": e}
                                  for i, e in enumerate(ld_items)]}
    page(path, "Hamburg-Events 2027 mit Unterkunft in Wedel | stayHere",
         "Hamburg-Termine 2027 mit Unterkunft in Wedel: INTERNORGA, Hafengeburtstag, Haspa Marathon, ELBJAZZ und "
         "Konzerte, mit Link zum Veranstalter.",
         body, jsonld=[events, crumbs_ld([("index.html", "Unterkünfte"), (path, "Events")])], active=path,
         scripts=["js/events.js"])


FAQ = [
    ("Wo liegen die stayHere-Unterkünfte?",
     "Alle drei Unterkünfte liegen in 22880 Wedel in Schleswig-Holstein, direkt an der westlichen Stadtgrenze von "
     "Hamburg und an der Elbe. stayHere 02 liegt im Zentrum, stayHere 03 nahe der FH Wedel und stayHere 01 am "
     "Waldrand des Klövensteen. Die genaue Adresse bekommst du nach der Buchung."),
    ("Welche Unterkunft passt für wie viele Gäste?",
     "stayHere 01 ist für bis zu 4 Gäste (2 Schlafzimmer), stayHere 02 für bis zu 3 Gäste (1 Schlafzimmer und ein "
     "Einzelbett im Wohnzimmer) und stayHere 03 für bis zu 6 Gäste (4 Schlafzimmer)."),
    ("Wie weit ist es zur S-Bahn?",
     "Von stayHere 02 gehst du etwa 5 Minuten zum S-Bahnhof Wedel. Von stayHere 03 fährst du etwa 12 Minuten mit "
     "dem Bus. Für stayHere 01 planst du den Weg ab der Adresse im HVV. Wenn du spät ankommst, holt dich der "
     "Gastgeber nach Absprache am S-Bahnhof ab."),
    ("Wie komme ich von Wedel nach Hamburg?",
     "Mit der S1 ab dem S-Bahnhof Wedel. Sie fährt ohne Umsteigen über Blankenese und Altona zur Reeperbahn, zu "
     "den Landungsbrücken, zum Jungfernstieg und zum Hauptbahnhof. Wedel ist die Endstation der Linie. Aktuelle "
     "Abfahrten und Baustellen zeigt der HVV."),
    ("Wie komme ich vom Flughafen Hamburg nach Wedel?",
     "Die S1 verbindet den Flughafen Hamburg und Wedel ohne Umsteigen. Auf dem Weg zum Flughafen wird der Zug in "
     "Ohlsdorf geteilt: Ein Zugteil fährt zum Flughafen, der andere nach Poppenbüttel. Achte deshalb auf die "
     "Anzeige am Zug."),
    ("Gibt es einen Parkplatz?",
     "Ja, bei allen drei Unterkünften kostenlos. stayHere 01 hat einen Parkplatz auf dem Grundstück, stayHere 02 "
     "einen Stellplatz am Haus und stayHere 03 einen reservierten Stellplatz direkt am Haus."),
    ("Welche Unterkunft hat einen Balkon oder Garten?",
     "stayHere 02 hat einen sonnigen Südbalkon und einen Gemeinschaftsgarten mit Grillplatz. stayHere 03 hat einen "
     "eigenen Garten. stayHere 01 liegt am Waldrand."),
    ("Ist eine Unterkunft barrierearm?",
     "stayHere 02 liegt im 3. Stock, ist mit dem Aufzug erreichbar und weitgehend stufenlos. An der Dusche und am "
     "Balkon gibt es je eine kleine Stufe. Die Wohnung ist damit barrierearm, aber nicht barrierefrei."),
    ("Kann ich den Billardtisch nutzen?",
     "Der Billardtisch gehört zu stayHere 01. Im Winter steht er nicht zur Verfügung. Für die übrige Zeit "
     "bestätigt dir der Gastgeber die Nutzung vor der Anreise."),
    ("Wie komme ich zur FH Wedel?",
     "Der Campus liegt in der Feldstraße 143. Von stayHere 03 gehst du etwa 5 Minuten zu Fuß. Vom S-Bahnhof Wedel "
     "oder von S-Blankenese fährt laut Hochschule der Bus 189 bis zur Haltestelle Fachhochschule."),
    ("Wie weit sind Elbe und Deich?",
     "Von stayHere 03 fährst du etwa 12 Minuten mit dem Bus zum Schulauer Fährhaus an der Elbe. stayHere 02 liegt "
     "im Zentrum nahe der Elbe. Der Elbdeich führt von Wedel nach Westen in die Wedeler und die Haseldorfer Marsch."),
    ("Kann ich länger als einen Monat bleiben?",
     "Ja. stayHere 02 mietest du über Wunderflats möbliert für 1 bis 6 Monate. Die Monatsmiete beträgt dort "
     "1.680 € einschließlich Nebenkosten, Strom und Internet (Stand " + STAND + ")."),
    ("Wie buche ich und wo sehe ich die Preise?",
     "Alle drei Unterkünfte buchst du über Airbnb, stayHere 02 ab einem Monat zusätzlich über Wunderflats. Dort "
     "siehst du die Preise für deine Reisedaten, die freien Termine und die Stornobedingungen."),
    ("In welchen Sprachen erreiche ich den Gastgeber?",
     "Auf Deutsch, Englisch und Spanisch. Er antwortet auf Airbnb meist innerhalb einer Stunde."),
]


def build_faq():
    path = "anreise-faq.html"
    faq_html = "\n".join("<div><h3>{}</h3><p>{}</p></div>".format(q, a) for q, a in FAQ)
    body = simple_head("Anreise und häufige Fragen",
                       "Wedel ist die Endstation der S-Bahn-Linie S1. Von dort fährst du ohne Umsteigen in die "
                       "Hamburger Innenstadt und zum Flughafen. Hier steht, wie du zu den Unterkünften kommst und "
                       "was Gäste am häufigsten fragen.") + """
<section id="anreise">
<div class="wrap">
<div class="section-head"><h2>Mit der S1 nach Hamburg</h2><p>Die wichtigsten Halte ab Wedel. Fahrzeiten, Takt und Baustellen prüfst du im <a href=\"""" + HVV + """\" rel="noopener">HVV-Fahrplan</a>.</p></div>
""" + S1_STOPS + """
</div>
</section>

<section class="alt">
<div class="wrap">
<div class="cards">
<div class="card"><h3>Mit der Bahn</h3><p>Fernzüge halten am Hamburger Hauptbahnhof. Von dort fährt die S1 direkt nach Wedel.</p></div>
<div class="card"><h3>Mit dem Flugzeug</h3><p>Vom Flughafen Hamburg fährt die S1 ohne Umsteigen bis Wedel. In der Gegenrichtung wird der Zug in Ohlsdorf geteilt. Achte auf den Zugteil zum Flughafen.</p></div>
<div class="card"><h3>Mit dem Auto</h3><p>Alle drei Unterkünfte haben einen kostenlosen Parkplatz. Die Adresse für dein Navi bekommst du nach der Buchung.</p></div>
<div class="card"><h3>Späte Ankunft</h3><p>Wenn du spät ankommst, holt dich der Gastgeber nach Absprache am S-Bahnhof Wedel ab.</p></div>
</div>
</div>
</section>

<section id="faq">
<div class="wrap">
<div class="section-head"><h2>Häufige Fragen</h2></div>
<div class="faq">
""" + faq_html + """
</div>
</div>
</section>
"""
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in FAQ],
    }
    page(path, "Anreise &amp; FAQ: S-Bahn S1, Parken, Buchung | stayHere Wedel",
         "Anreise nach Wedel mit S1, Flugzeug und Auto. Antworten zu Gästezahl, Weg zur S-Bahn, Parkplatz, Balkon, "
         "Garten, FH Wedel und Buchung.",
         body, jsonld=[faq_ld, crumbs_ld([("index.html", "Unterkünfte"), (path, "Anreise & FAQ")])], active=path)


def build_legal():
    path = "impressum.html"
    body = simple_head("Impressum und Datenschutz", "Angaben zum Anbieter und zum Umgang mit Daten auf dieser Seite.") + """
<section id="impressum">
<div class="wrap prose">
<h2>Impressum</h2>
<p>Ruppert Gerhard Matzke<br>stayHere Wedel<br>22880 Wedel<br>Deutschland</p>
<p>E-Mail: <a href="mailto:""" + MAIL + """\">""" + MAIL + """</a><br>Telefon: <a href="tel:""" + TEL + """\">""" + TEL_SHOW + """</a></p>
<p>Veranstaltungen, die auf dieser Seite genannt werden, führen die verlinkten Veranstalter durch. stayHere verkauft keine Veranstaltungstickets.</p>
</div>
</section>
<section id="datenschutz" class="alt">
<div class="wrap prose">
<h2>Datenschutz</h2>
<p><strong>Verantwortlicher:</strong> Ruppert Gerhard Matzke, 22880 Wedel, """ + MAIL + """</p>
<p><strong>Hosting:</strong> Diese Seite wird über ChatGPT Sites (OpenAI) mit Cloudflare bereitgestellt. Dabei können IP-Adresse, Zeitpunkt, angeforderte Adresse und Geräteinformationen verarbeitet werden. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Weitere Informationen: <a href="https://openai.com/policies/eu-privacy-policy/" rel="noopener">Datenschutzhinweise von OpenAI</a>.</p>
<p><strong>Eigener Seitencode:</strong> Die Seite setzt keine Cookies, lädt keine Schriften oder Skripte von Dritten und nutzt keine Analyse- oder Werbedienste. Eingaben werden nicht gespeichert.</p>
<p><strong>Externe Dienste:</strong> Airbnb, Wunderflats, die Seiten der Veranstalter und der HVV öffnen sich erst, wenn du einen Link anklickst. Für sie gelten die Datenschutzhinweise des jeweiligen Anbieters.</p>
<p><strong>Kontaktanfragen:</strong> Wenn du per E-Mail (Postfach bei Google Gmail) oder Telefon Kontakt aufnimmst, werden deine Angaben zur Bearbeitung der Anfrage verarbeitet (Art. 6 Abs. 1 lit. b oder f DSGVO) und danach gelöscht, soweit keine Aufbewahrungspflicht besteht.</p>
<p><strong>Deine Rechte:</strong> Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch sowie das Recht auf Beschwerde bei einer Aufsichtsbehörde, zum Beispiel beim <a href="https://www.datenschutzzentrum.de/" rel="noopener">ULD Schleswig-Holstein</a>. Eine automatisierte Entscheidungsfindung oder Profilbildung findet nicht statt.</p>
</div>
</section>
"""
    page(path, "Impressum und Datenschutz | stayHere Wedel",
         "Impressum und Datenschutzhinweise von stayHere Wedel, Ruppert Gerhard Matzke, 22880 Wedel.",
         body, robots="noindex,follow", in_sitemap=False)


def build_meta_files():
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in PAGES:
        sm.append("  <url><loc>{}</loc><lastmod>{}</lastmod></url>".format(url_of(p), LASTMOD))
    sm.append("</urlset>")
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm) + "\n")
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: {}/sitemap.xml\n".format(BASE))
    llms = """# stayHere Wedel

> Drei privat geführte Ferienunterkünfte in 22880 Wedel (Schleswig-Holstein), an der Elbe westlich von Hamburg. Wedel ist die Endstation der S-Bahn-Linie S1, die ohne Umsteigen nach Altona, Landungsbrücken, Jungfernstieg, Hamburg Hauptbahnhof und zum Flughafen fährt. Gastgeber: Ruppert Gerhard Matzke, Airbnb-Superhost, spricht Deutsch, Englisch und Spanisch. Stand der Angaben: {stand}.

## Unterkünfte

- [stayHere 01: Souterrainwohnung für 4 Gäste am Klövensteen]({b}/unterkuenfte/stayhere-01.html): 2 Schlafzimmer (3 Einzelbetten, 1 kleines Doppelbett), 1 Bad, eigener Eingang, Küche, 65-Zoll-Fernseher, Billard (nicht im Winter), Darts, Glasfaser-WLAN ca. 83 Mbit/s, kostenloser Parkplatz, ruhige Lage am Waldrand. Airbnb 4,88 von 5 (191 Bewertungen). Buchung: {a1}
- [stayHere 02: Wohnung für 3 Gäste mit Südbalkon und Aufzug]({b}/unterkuenfte/stayhere-02.html): 50 m², 2 Zimmer, 1 Schlafzimmer (Doppelbett) plus Einzelbett im Wohnzimmer, 3. Stock mit Aufzug, weitgehend stufenlos, Küche, Waschmaschine, kostenloser Stellplatz, Zentrum von Wedel, ca. 5 Gehminuten zum S-Bahnhof Wedel (S1). Airbnb 4,83 von 5 (90 Bewertungen). Buchung: {a2} ; ab 1 Monat (bis 6 Monate, 1.680 € pro Monat warm) über Wunderflats: {w2}
- [stayHere 03: Reihenhaus für 6 Gäste mit Garten]({b}/unterkuenfte/stayhere-03.html): 4 Schlafzimmer (2 Doppelbetten, 4 Einzelbetten), 1,5 Bäder, Garten, Küche, Waschmaschine, reservierter Stellplatz am Haus, ca. 5 Gehminuten zur FH Wedel, ca. 12 Minuten mit dem Bus zum S-Bahnhof Wedel und zur Elbe. Airbnb 5,0 von 5 (11 Bewertungen). Buchung: {a3}

## Weitere Seiten

- [Vergleich und Überblick]({b}/)
- [Anreise und häufige Fragen]({b}/anreise-faq.html): S1, Flughafen, Auto, FH Wedel, Buchung
- [Wedel und Elbe]({b}/wedel-elbe.html): Willkomm-Höft, Elbdeich und Wedeler Marsch, Elbwanderweg, Yachthafen, Klövensteen
- [Hamburg-Tipps]({b}/hamburg-tipps.html): Speicherstadt und HafenCity mit der S1 ab Wedel
- [Hamburg-Events 2027]({b}/events.html): Messen, Konzerte, Hafengeburtstag

## Kontakt

- E-Mail: {mail}
- Telefon: {tel}
""".format(stand=STAND, b=BASE, a1=AIRBNB_01, a2=AIRBNB_02, a3=AIRBNB_03, w2=WUNDERFLATS_02, mail=MAIL,
           tel=TEL_SHOW)
    with open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(llms)


EVENTS_JS = """(function () {
  var buttons = document.querySelectorAll('.filter button');
  var events = document.querySelectorAll('.event');
  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var kind = btn.getAttribute('data-filter');
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      events.forEach(function (ev) {
        ev.hidden = kind !== 'alle' && ev.getAttribute('data-kind') !== kind;
      });
    });
  });
})();
"""


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "css"))
    os.makedirs(os.path.join(OUT, "js"))
    shutil.copy(os.path.join(HERE, "site.css"), os.path.join(OUT, "css", "site.css"))
    with open(os.path.join(OUT, "js", "events.js"), "w", encoding="utf-8") as f:
        f.write(EVENTS_JS)
    build_index()
    build_01()
    build_02()
    build_03()
    build_wedel()
    build_hamburg()
    build_events()
    build_faq()
    build_legal()
    build_meta_files()
    print("ok", len(PAGES), "Seiten in der Sitemap")


if __name__ == "__main__":
    main()
