# Diagramm-Spec-Format (Input für `scripts/render_diagram.py`)

Ein Diagramm ist eine JSON-Datei, die der Agent selbst schreibt (aus dem, was
er im Code gefunden hat), plus ein Aufruf des Render-Scripts. Kein LLM
schreibt SVG von Hand — das Script übernimmt Layout, Grid-Snapping und den
Stil, das LLM liefert nur die Fachlichkeit (Knoten, Kanten, Beschriftungen).

```bash
python3 scripts/render_diagram.py <spec>.json <ziel>.svg
```

## Gemeinsame Felder

| Feld | Pflicht | Beschreibung |
|---|---|---|
| `kind` | ja | `"boxes"` \| `"layers"` \| `"sequence"` |
| `title` | nein | Kursiver Titel oben links |
| `subtitle` | nein | Kleine Mono-Zeile unter dem Titel (z. B. „arc42 · Kapitel 3") |
| `theme` | nein | Überschreibt einzelne Tokens aus `references/style-guide.md` |

## `kind: "boxes"` — Kontext-, Bausteinsicht, Verteilungssicht

```json
{
  "kind": "boxes",
  "nodes": [
    {"id": "sys", "label": "Unser System", "sublabel": "core-service",
     "kind": "focal", "col": 1, "row": 0}
  ],
  "edges": [
    {"from": "sys", "to": "db", "label": "SQL", "style": "solid|dashed",
     "kind": "focal", "dir": "forward|none"}
  ],
  "groups": [
    {"id": "g1", "label": "Systemgrenze", "nodes": ["sys", "db"]},
    {"id": "g2", "kind": "box", "label": "Bestellungen",
     "sublabel": "Ebene 1 · orders/", "nodes": ["a", "b"]}
  ]
}
```

- `col`/`row` sind ganzzahlige Rasterkoordinaten, keine Pixel — das Script
  übernimmt Abstand und Ausrichtung. Plane das Raster auf Papier/im Kopf:
  eine Spalte pro „Tiefe" (Client → System → externe Systeme), eine Zeile
  pro parallelem Element auf derselben Tiefe.
- `kind: "focal"` genau 1–2 Mal pro Diagramm verwenden — das ist der
  Coral-Akzent, der das Auge lenkt. Alles andere bleibt neutral.
- `kind: "external"` für Systeme/Akteure außerhalb der eigenen
  Verantwortung (grau gefüllt, kein Akzent möglich).
- `groups` zeichnet eine gestrichelte Grenze um eine Teilmenge der Knoten
  (z. B. „das ist unser Deploy", „das ist die Systemgrenze"). Optional.
  Die Grenze umschließt das Rechteck aller Mitglieder — ein Nicht-Mitglied
  darf nicht in diesen Zeilen/Spalten dazwischen liegen.
- `"kind": "box"` an einer Gruppe zeichnet statt der gestrichelten Grenze
  einen **Baustein, der mit seinen Teilen gefüllt ist**: gefüllte Fläche,
  durchgezogener Rahmen, `label` (und optional `sublabel`) zentriert oben.
  Das ist die Whitebox-Sicht der Bausteinsicht — der Baustein aus Ebene 1
  als Box, darin die Bausteine aus Ebene 2, außen die Nachbarn als
  `external`. Kanten, die den Rahmen überqueren, zeigen die Verbindungen
  zur Außenwelt. Beispiel: `assets/templates/whitebox-diagram.json`.
  `label`/`sublabel` müssen in die Breite der Gruppe passen (bei einer
  Spalte ca. 25 Zeichen); Kanten-Labels landen nie auf dem Rahmen.
- Kanten führt das Script selbst: rechtwinklig, **um alle Boxen herum**
  (nie hindurch), mit möglichst wenigen Knicken. Jede Kante bekommt einen
  eigenen Anschlusspunkt an der Box, auch wenn mehrere Kanten dieselbe Seite
  nutzen; das Label landet auf einem freien Stück der Kante. Kanten
  überspringen dürfen also auch Knoten dazwischen (z. B. `row 0` → `row 2`
  in derselben Spalte) — sie werden außen herum geführt.
- Kanten-Labels kurz halten: Zwischen zwei Nachbarn in derselben Zeile ist
  Platz für etwa 20 Zeichen. Längeres gehört in die Tabelle unter dem
  Diagramm; `self_check.py` meldet Labels, die nicht passen.
- In der Bausteinsicht (Komponentenebene) beginnt das Label mit der
  Schnittstellen-ID, z. B. `IF-02 Webhook-Event`; Details stehen im
  Steckbrief (siehe `references/building-block-view.md`).

## `kind: "layers"` — Schichtenmodell (Kapitel 8, ggf. 4)

```json
{
  "kind": "layers",
  "layers": [
    {"label": "API / Gateway", "items": ["Auth", "Rate-Limiting"], "kind": "focal"}
  ]
}
```

Reihenfolge im Array = Reihenfolge von oben nach unten. `items` sind
Stichworte, keine Sätze (werden mono, klein, durch „·" getrennt gesetzt).

## `kind: "sequence"` — Laufzeitsicht (Kapitel 6)

```json
{
  "kind": "sequence",
  "numbered": true,
  "lanes": [{"id": "client", "label": "Client"}],
  "messages": [
    {"from": "client", "to": "api", "label": "POST /login",
     "dashed": false, "kind": "focal"}
  ]
}
```

`messages` sind chronologisch von oben nach unten. `dashed: true` für
Antworten/Rückgaben (Konvention: durchgezogen = Aufruf, gestrichelt =
Antwort — wie in UML-Sequenzdiagrammen).

- `from` = `to` ist ein Selbstaufruf und wird als kleine Schleife rechts
  der Lebenslinie gezeichnet, das Label daneben.
- Das Label einer Nachricht steht über dem Pfeil in der Lücke neben dem
  Absender — auch bei Pfeilen über mehrere Lanes, damit es keine
  Lebenslinie verdeckt. Es muss daher in eine Lücke zwischen zwei Lanes
  passen (ca. 28 Zeichen).
- `"numbered": true` (optional) stellt jedem Label seine Schrittnummer
  voran („3 · Session anlegen"), damit der Fließtext darauf verweisen kann.

## Nach dem Rendern: Selbstcheck

```bash
python3 scripts/self_check.py <spec>.json <ziel>.svg
```

Das Skript prüft die Spec und rechnet dann dasselbe Layout nach, das der
Renderer zeichnet. Es meldet mit Exit-Code 1:

- Kanten/Nachrichten mit unbekannter `id`, mehr als zwei `focal`-Elemente
  (verletzt „ein Akzent, 1–2 Fokuspunkte"), zu kleine Diagramme;
- Kanten, die durch eine Box laufen oder auf einer anderen Kante liegen;
- Kanten-Labels, die eine Box, ein anderes Label, eine andere Kante oder
  eine Pfeilspitze überdecken oder auf dem Rahmen einer `box`-Gruppe sitzen;
- Text, der nicht in seine Box, Schicht oder Lane passt;
- Gruppen, deren Grenze einen Knoten einschließt, der nicht dazugehört,
  und `box`-Gruppen, deren Titel nicht in die Gruppe passt;
- im SVG: fehlender `<title>`, Schatten, externe URLs.

Bei `FAIL`: Label kürzen oder `col`/`row` umstellen, neu rendern, erneut
prüfen.

## Wann KEIN Diagramm

Wenn `nodes` (oder `layers`/`lanes`) weniger als 3 Elemente hätte, oder das
Diagramm nur das wiederholen würde, was der Fließtext in einem Satz sagt:
kein Diagramm rendern, sondern den Satz schreiben.
