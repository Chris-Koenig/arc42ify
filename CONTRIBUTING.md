# Contributing

Danke für Interesse an `arc42ify`. Der Umfang ist bewusst klein gehalten
(fünf Diagrammtypen, zwei Scripts) — Beiträge, die diese Einfachheit
erhalten, sind am willkommensten.

## Einen neuen Diagrammtyp ergänzen

1. In `skills/arc42-docs/scripts/render_diagram.py` eine neue
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
4. Eine Beispiel-Spec unter `skills/arc42-docs/assets/templates/` ablegen
   und mit `scripts/self_check.py` prüfen.
5. Den neuen `kind` in `references/diagram-spec.md` dokumentieren
   (Feldreferenz + Beispiel-JSON).
6. Falls der Typ einem arc42-Kapitel zugeordnet ist: Eintrag in
   `references/arc42-sections.md` ergänzen.

## Ein arc42-Kapitel anpassen (Reihenfolge, Wortlaut, Quelle)

Nur `skills/arc42-docs/references/arc42-sections.md` und ggf.
`scripts/scaffold.py` (Dateinamen/Titel) anfassen. Keine Kapitel entfernen —
arc42 definiert alle 12 verbindlich; ein Kapitel darf leer/TODO bleiben,
aber nicht fehlen.

## Vor jedem PR

```bash
# Alle Beispiel-Specs müssen weiterhin sauber rendern und den Selbstcheck bestehen
for f in skills/arc42-docs/assets/templates/*.json; do
  out=$(mktemp --suffix=.svg)
  python3 skills/arc42-docs/scripts/render_diagram.py "$f" "$out" || exit 1
  python3 skills/arc42-docs/scripts/self_check.py "$f" "$out" || exit 1
done
```

Dasselbe läuft automatisch in CI (`.github/workflows/ci.yml`) — ein
fehlschlagender Check blockiert den Merge.

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
