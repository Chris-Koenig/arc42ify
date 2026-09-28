# Contributing

Danke für Interesse an `arc42ify`. Der Umfang ist bewusst klein gehalten
(fünf Diagrammtypen, zwei Scripts) — Beiträge, die diese Einfachheit
erhalten, sind am willkommensten.

## Einen neuen Diagrammtyp ergänzen

1. In `skills/arc42ify/scripts/render_diagram.py` eine neue
   `render_<kind>(spec, theme)`-Funktion nach dem Muster der bestehenden
   drei (`render_boxes`, `render_layers`, `render_sequence`) hinzufügen und
   in `RENDERERS` registrieren. Sie zeichnet ihren Inhalt ab `(0, 0)` und
   gibt `(breite, höhe, svg)` zurück — Titel und gleichmäßige Ränder setzt
   `render_svg()`. Geometrie, die `self_check.py` prüfen soll, in eine
   eigene `layout_<kind>(spec)`-Funktion legen (wie `layout_boxes`,
   `layout_sequence`), damit Renderer und Check dieselben Zahlen sehen.
2. Design-Tokens (`theme[...]`) verwenden, keine hartkodierten Farben —
   sonst bricht das Corporate-Design-Override.
3. Alle Koordinaten durch `snap()` schicken (4px-Raster ist nicht
   verhandelbar, siehe `references/style-guide.md`).
4. Eine Beispiel-Spec unter `skills/arc42ify/assets/templates/` ablegen,
   das SVG daneben rendern und mit einchecken — die Tests vergleichen es
   Byte für Byte mit einem frischen Render.
5. Jede neue Prüfregel in `self_check.py` bekommt eine kaputte Fixture unter
   `tests/fixtures/fail/`, die sie auslösen muss, plus die erwartete Meldung
   in `CheckerCatchesDefects.EXPECTED`. Eine Regel, die nur im Text steht,
   liefert irgendwann kaputte Diagramme aus.
6. Den neuen `kind` in `references/diagram-spec.md` dokumentieren
   (Feldreferenz + Beispiel-JSON).
7. Falls der Typ einem arc42-Kapitel zugeordnet ist: Eintrag in
   `references/arc42-sections.md` ergänzen.

## Ein arc42-Kapitel anpassen (Reihenfolge, Wortlaut, Quelle)

Nur `skills/arc42ify/references/arc42-sections.md` und ggf.
`scripts/scaffold.py` (Dateinamen/Titel) anfassen. Keine Kapitel entfernen —
arc42 definiert alle 12 verbindlich; ein Kapitel darf leer/TODO bleiben,
aber nicht fehlen.

## Vor jedem PR

```bash
python3 -m unittest discover -s tests -v
```

Nur Standardbibliothek, keine Installation nötig. Die Tests prüfen:

- alle Beispiel-Diagramme (Vorlagen und `docs-example/`) bestehen den
  Selbstcheck, und jedes eingecheckte SVG ist identisch mit einem frischen
  Render — ein veraltetes SVG nennt den Befehl zum Neu-Rendern;
- der Router: Kanten rechtwinklig, mit Abstand zu fremden Boxen, jedes
  Kantenende an einem eigenen Anschlusspunkt, alle Formen im 4px-Raster;
- der Selbstcheck in beide Richtungen: `tests/fixtures/fail/` muss jeweils
  die erwartete Meldung liefern, `tests/fixtures/pass/` muss sauber sein;
- `scaffold.py`, die Scripts als Kommandozeilen-Tools (auch auf einer
  Windows-Konsole, die nicht jedes Zeichen darstellen kann);
- die `description` in `SKILL.md` (Längengrenze, gültiges YAML, die
  Trigger-Wörter, an denen Agenten den Skill erkennen), die Plugin-Manifeste
  (Claude Code, Codex) auf gleichen Namen und gleiche Version, und alle
  relativen Links in den Markdown-Dateien.

Dasselbe läuft in CI (`.github/workflows/ci.yml`) bei jedem Push und Pull
Request — auf Python 3.8 (der zugesagten Mindestversion), 3.13 und unter
Windows.

## Stil

- Kein Fremdabhängigkeiten in den Scripts (nur Python-Stdlib) — das ist
  der Grund, warum der Renderer in jeder Sandbox identisch läuft. Neue
  Abhängigkeiten (z. B. für PNG-Export) gehören in ein optionales,
  klar als solches gekennzeichnetes Zusatz-Script, nie in
  `render_diagram.py` selbst.
- Deutsch für Kapitel-/Anleitungstext (Zielgruppe: deutschsprachige
  arc42-Nutzer:innen), Englisch für Code-Kommentare und Variablennamen.
- Ein Diagramm, ein Zweck — keine Sammel-Diagramme, die mehrere arc42-
  Kapitel gleichzeitig abdecken sollen.

## Fragen / Vorschläge ohne Code-Änderung

Ein Issue reicht — insbesondere für: fehlende arc42-Kapitel-Zuordnungen,
falsch platzierte Labels bei ungewöhnlichen Diagrammgrößen, oder Wünsche
für weitere Agent-Host-Integrationen (`references/multi-agent-usage.md`).
