# Vision

## Warum dieses Repo existiert

arc42 ist als Dokumentationsstandard etabliert — aber in der Praxis scheitert
er meistens an zwei Dingen: Text wird nicht aktuell gehalten, sobald Code
sich ändert, und Diagramme sehen entweder aus wie ein handgezeichnetes
UML-Whiteboard oder wie generisches Mermaid mit runden grauen Kästen.

`arc42ify` macht arc42 zu etwas, das ein AI-Agent (Claude, Copilot, oder
jeder andere Agent mit Datei- und Terminalzugriff) routinemäßig pflegen kann
— nicht als einmaliges Dokumentationsprojekt, sondern als Nebenprodukt jeder
relevanten Code-Änderung.

## Was es ist

- Ein **Agent Skill** (`skills/arc42ify/`): eine Anleitung + zwei
  Python-Scripts, die aus Code/Ideen/Texten arc42-konforme Markdown-Kapitel
  plus editoriale SVG-Diagramme erzeugen — direkt im Repo unter `docs/arc42/`.
- Ein **Renderer** ohne Fremdabhängigkeiten (`render_diagram.py`): fünf
  Diagrammtypen, ein Design-System (ein Akzent, keine Schatten,
  Hairline-Rahmen, 4px-Raster), lauffähig in jeder Sandbox, jedem CI-Runner,
  offline.
- Ein **installierbares Claude-Code-Plugin** (`.claude-plugin/`), damit die
  Installation ein Einzeiler ist statt manuellem Symlinken.

## Was es nicht ist

- Kein Ersatz für API-Referenzdokumentation (OpenAPI/Docstrings).
- Kein generischer Diagramm-Editor — die fünf Typen sind bewusst auf das
  beschränkt, was arc42 tatsächlich braucht (Kontext, Bausteine, Verteilung,
  Laufzeit, Querschnittskonzepte).
- Kein Ersatz für menschliches Architektur-Review — der Skill sammelt und
  strukturiert, was im Code/in der Idee steckt; er erfindet keine
  Qualitätsziele oder Architekturentscheidungen, die niemand getroffen hat.

## Prinzipien

1. **Text vor Diagramm.** Ein Diagramm ohne erklärenden Text ist Dekoration,
   kein Dokument. Der Skill sammelt Fakten, schreibt den Text, erzeugt dann
   erst das Bild.
2. **Kein Diagramm ohne Grund.** Wenn ein Satz reicht, wird kein Diagramm
   gebaut (siehe `references/diagram-spec.md`, Abschnitt „Wann KEIN
   Diagramm").
3. **Reproduzierbar statt hübsch-zufällig.** Fixes 4px-Raster, explizite
   `col`/`row`-Platzierung statt Auto-Layout — zwei Läufe mit derselben
   Spec erzeugen dasselbe Ergebnis.
4. **Ehrlich über Lücken.** Ein arc42-Kapitel ohne verfügbare Information
   wird als offen markiert, nicht mit plausibel klingendem Text gefüllt.
5. **Agent-agnostisch.** Reine Dateien (Markdown, JSON, stdlib-Python) —
   kein Framework-Lock-in. Was für Claude funktioniert, funktioniert
   identisch für Copilot, Cursor oder ein CI-Script.

## Roadmap (offen, keine Zusagen)

- Weitere Diagrammtypen bei Bedarf (ER-Diagramm für Kapitel 5 Ebene 2,
  Zustandsautomat) — nach demselben `kind`-Muster in `render_diagram.py`.
- PNG-Export für Präsentationen (aktuell: Browser-Druckfunktion als
  Workaround).
- Optionales automatisches Marken-Onboarding (Farbe/Schrift aus einer
  Website extrahieren) — angelehnt an, aber unabhängig von,
  [diagram-design](https://github.com/cathrynlavery/diagram-design).

Änderungen an dieser Vision sind willkommen — siehe `CONTRIBUTING.md`.
