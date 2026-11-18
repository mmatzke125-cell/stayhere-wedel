# -*- coding: utf-8 -*-
"""Zeichnet die Karte von Wedel als SVG. Daten: map_data.py (OpenStreetMap, ODbL)."""
import map_data as D

ACCENT = "#14284b"
SHOP = "#b0542c"   # Supermärkte, warmer Ton als Gegenfarbe zum Marineblau
LABELS = {"01": "Moorwegsiedlung", "02": "S-Bahnhof Wedel", "03": "Feldstraße"}


def _circle(num, x, y, r, active):
    on = active is None or active == num
    op = "" if on else ' opacity=".35"'
    out = ['<g class="c"%s>' % op,
           '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="%s" stroke="%s" '
           'stroke-opacity="%s" stroke-width="2.5" stroke-dasharray="9 7"/>'
           % (x, y, r, ACCENT, ".08" if on else ".05", ACCENT, ".65" if on else ".4")]
    # 03 steht unter dem Mittelpunkt, sonst verdeckt die Schrift den Edeka daneben.
    top = y + 30 if num == "03" else y - 32
    sub = {"02": y + 32, "03": y + 52}.get(num, y - 12)
    out.append('<text class="cl" x="%.1f" y="%.1f" text-anchor="middle">stayHere %s</text>'
               % (x, top, num))
    out.append('<text class="cs" x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (x, sub, LABELS[num]))
    if num != "02":
        out.append('<circle cx="%.1f" cy="%.1f" r="7" fill="%s" stroke="#fff" stroke-width="2"/>'
                   % (x, y, ACCENT))
    out.append("</g>")
    return "".join(out)


def map_svg(active=None):
    w, h, r = D.W, D.H, D.RADIUS_M / D.M_PER_PX
    p = ['<svg class="mapsvg" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-labelledby="mt md">' % (w, h),
         '<title id="mt">Karte von Wedel bei Hamburg mit den drei stayHere-Unterkünften</title>',
         '<desc id="md">Die Karte zeigt Wedel zwischen Elbe und Klövensteen: den S-Bahnhof Wedel als '
         'Endstation der Linie S1, zwölf Supermärkte und drei Kreise mit einem Umkreis von etwa 500 Metern '
         'um die Moorwegsiedlung (stayHere 01), den S-Bahnhof (stayHere 02) und die Feldstraße '
         '(stayHere 03).</desc>',
         '<defs><clipPath id="mc"><rect width="%d" height="%d"/></clipPath></defs>' % (w, h),
         '<g clip-path="url(#mc)">',
         '<rect width="%d" height="%d" fill="#faf8f6"/>' % (w, h),
         '<path d="%s" fill="#efebe6"/>' % D.BUILT,
         '<path d="%s" fill="#e4eadd"/>' % D.FOREST,
         '<path d="%s" fill="#dbe4ea"/>' % D.ELBE,
         '<path d="%s" fill="#dbe4ea"/>' % D.WATER,
         '<g fill="none" stroke="#fff" stroke-linecap="round" stroke-linejoin="round">',
         '<path d="%s" stroke-width="3"/>' % D.TERTIARY,
         '<path d="%s" stroke-width="4.5"/>' % D.SECONDARY,
         '<path d="%s" stroke-width="6"/>' % D.PRIMARY,
         "</g>",
         '<path d="%s" fill="none" stroke="#a79f98" stroke-width="2" stroke-dasharray="9 7"/>' % D.RAIL]
    # Orientierung
    p.append('<text class="ml" x="250" y="752">Elbe</text>')
    p.append('<text class="ml" x="978" y="96">Klövensteen</text>')
    p.append('<text class="mt" x="286" y="516">Wedel</text>')
    p.append('<text class="ms" x="1012" y="408">Richtung Hamburg →</text>')
    # Willkomm-Höft
    p.append('<circle cx="428" cy="696" r="4" fill="#37312f"/>')
    p.append('<text class="ms" x="440" y="701">Willkomm-Höft</text>')
    # Supermärkte
    for _, x, y in D.SUPERMARKETS:
        p.append('<circle cx="%.1f" cy="%.1f" r="5.5" fill="%s" stroke="#fff" stroke-width="1.8"/>'
                 % (x, y, SHOP))
    # Kreise
    for num, x, y in D.CIRCLES:
        p.append(_circle(num, x, y, r, active))
    # S-Bahnhof
    sx, sy = D.STATION
    p.append('<rect x="%.1f" y="%.1f" width="16" height="16" rx="4" fill="%s" stroke="#fff" '
             'stroke-width="2"/>' % (sx - 8, sy - 8, ACCENT))
    # Maßstab
    km = 1000 / D.M_PER_PX
    p.append('<g stroke="#37312f" stroke-width="2"><path d="M44 62h%.1f" /><path d="M44 56v12"/>'
             '<path d="M%.1f 56v12"/></g>' % (km, 44 + km))
    p.append('<text class="ms" x="44" y="46">1 Kilometer</text>')
    p.append("</g></svg>")
    return "".join(p)


KEY = ('<ul class="map-key">'
       '<li><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="6.5" fill="%s" '
       'stroke="#fff" stroke-width="2"/></svg>Supermarkt</li>'
       '<li><svg viewBox="0 0 20 20" aria-hidden="true"><rect x="3" y="3" width="14" height="14" rx="3.5" '
       'fill="%s"/></svg>S-Bahnhof Wedel, Linie S1</li>'
       '<li><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="6.5" fill="%s"/></svg>'
       'Mittelpunkt des Umkreises</li>'
       '<li><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8.5" fill="%s" '
       'fill-opacity=".08" stroke="%s" stroke-opacity=".65" stroke-width="1.6" stroke-dasharray="3 2.4"/>'
       '</svg>Umkreis von etwa 500 Metern</li></ul>') % (SHOP, ACCENT, ACCENT, ACCENT, ACCENT)


def map_figure(active=None, gmap="https://www.google.com/maps/place/Wedel/@53.5822,9.7054,13z"):
    return ('<figure class="map">%s' + KEY +
            '<div class="map-load"><button type="button" class="btn label" data-gmap="%s">'
            'Google-Karte laden</button>'
            '<p class="muted small">Beim Laden wird eine Verbindung zu Google hergestellt. '
            'Dabei werden deine IP-Adresse und Browserdaten an Google übertragen.</p></div>'
            '<figcaption class="muted small">Eigene Zeichnung, Kartendaten von '
            '<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>-Mitwirkenden '
            '(ODbL). Die Kreise zeigen einen Umkreis von etwa 500 Metern, nicht die genaue Adresse.'
            '</figcaption></figure>') % (map_svg(active), gmap)
