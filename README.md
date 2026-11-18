# stayHere Wedel

Website der drei Ferienunterkünfte stayHere in Wedel bei Hamburg, auf Deutsch,
Englisch und Spanisch. Statische Seiten, kein Framework, keine Verbindungen zu
fremden Servern außer der Google-Karte, die erst auf Klick lädt.

## Ordner

| Ordner | Inhalt |
|---|---|
| `public/` | die fertige Website. Das ist, was Cloudflare Pages ausliefert. |
| `build/` | der Generator, der `public/` erzeugt |
| `assets/img/` | die Fotos. Hier kommen die Originaldateien hinein. |

## Neu bauen

```bash
cd build
python3 build3.py ../public   # erzeugt alle deutschen Seiten
python3 i18n_build.py         # ergänzt Englisch und Spanisch
python3 cleanurls.py ../public # entfernt .html aus allen Verweisen
```

`i18n_build.py` muss immer direkt nach `build3.py` laufen, sonst stimmen die
Sprachlinks nicht. `cleanurls.py` läuft als Letztes.

Cloudflare Pages liefert `haeuser.html` unter `/haeuser` aus und leitet die
Adresse mit Endung dorthin um. Deshalb entfernt `cleanurls.py` die Endung aus
allen Links, Canonical-Angaben, hreflang, der Sitemap, dem JSON-LD und der
llms.txt. Bei einem Umzug auf einen gewöhnlichen Webserver muss der entweder
dasselbe tun oder dieser Schritt entfällt.

## Veröffentlichen

Cloudflare Pages hängt an diesem Repository. Build-Befehl: keiner.
Ausgabeordner: `public`. Jeder Push auf `main` geht nach etwa einer Minute live.

## Fotos nachlegen

Die Dateien unter den Namen ablegen, die auf den Platzhaltern der Seite stehen
(zum Beispiel `img/start-hero.jpg`), in `assets/img/` legen und neu bauen.

## Offen

- Impressum: vollständige Anschrift fehlt
- Datenschutzerklärung: Abschnitt zum Hosting fehlt
- Fotos: alle 27 Plätze sind Platzhalter
- Die drei Umkreise auf der Karte sind ungeprüft
