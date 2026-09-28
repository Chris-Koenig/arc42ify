# Style Guide — Design-Tokens für arc42-Diagramme

Single Source of Truth für Farben und Schriften. Alles unten wird von
`scripts/render_diagram.py` als `DEFAULT_THEME` gelesen; ein Projekt kann
es pro Diagramm über das `"theme"`-Feld der Spec überschreiben, oder global,
indem diese Datei editiert wird (Managed Installs: Änderungen können bei
Updates überschrieben werden — bei einem projekt-lokalen Skill-Kopie ist das
kein Problem).

## Prinzipien (nicht verhandelbar — das hält die Diagramme vom
„KI-generiert"-Look fern)

1. **Ein Akzent.** Nur 1–2 fokale Elemente pro Diagramm bekommen die
   Akzentfarbe. Alles andere ist neutral (Ink auf Paper, Hairline-Rahmen).
2. **Keine Schatten.** `box-shadow`/`filter: drop-shadow` sind verboten.
   Tiefe entsteht durch Flächenkontrast (Paper vs. Paper-2), nicht durch
   Schatten.
3. **1px Hairline-Rahmen**, maximal 10px Eckradius.
4. **Alles im 4px-Raster.** Jede Koordinate, Breite, jeder Abstand ist
   durch 4 teilbar. `render_diagram.py` erzwingt das automatisch (`snap()`).
5. **Drei Schriftrollen, nicht mehr:**
   - **Titel** (kursiv, Serife) — nur für den Diagrammtitel.
   - **Label** (Sans, halbfett) — Knotennamen, Schicht-Namen.
   - **Sublabel/Technik** (Mono) — Ports, URLs, Versionsangaben, Kanten-
     Beschriftungen.
6. Mono ist für *technischen* Inhalt reserviert (Ports, Protokolle,
   Versionsnummern) — nicht als generisches „Dev-Look"-Signal für alles.

## Token-Tabelle (Default)

| Rolle | Token | Wert | Verwendung |
|---|---|---|---|
| Hintergrund | `paper` | `#f7f6f3` | Diagrammhintergrund |
| Text | `ink` | `#1a1a1a` | Primärtext |
| Sekundärtext | `muted` | `#6b6b6b` | Sublabels, Kantenbeschriftungen |
| Kartenfläche | `paper2` | `#ffffff` | Normale Knoten-Boxen |
| Akzent | `accent` | `#d9622b` | Fokale Knoten/Kanten (max. 1–2×) |
| Rahmen | `hairline` | `#d8d5cf` | 1px-Rahmen, Gruppen-Grenzen |
| Extern | `external` | `#e7e5e0` | Knoten außerhalb der eigenen Verantwortung |
| Titel-Font | `font_title` | System-Serife | Diagrammtitel |
| Label-Font | `font_label` | System-Sans | Knoten-/Schicht-Namen |
| Mono-Font | `font_mono` | System-Mono | Technische Sublabels |

Bewusst **System-Fonts statt Google-Fonts**: der Renderer läuft offline, ohne
Netzwerkzugriff, identisch in jeder Sandbox/CI. Wer eine Marken-Schrift
braucht, trägt sie projektspezifisch über `"theme": {"font_label": "..."}`
ein und stellt sicher, dass die Schrift dort verfügbar ist, wo das SVG
geöffnet wird (z. B. als eingebettete `@font-face` beim Export nach PNG).

## Eigene Marke einsetzen

1. Primärfarbe der Marke (CTA-Farbe, nicht die Hintergrundfarbe) → `accent`.
2. Body-Hintergrundfarbe der Website → `paper`.
3. Primärer Fließtext → `ink`.
4. Kontrast prüfen: `ink` auf `paper` muss WCAG AA bei 10–12px Textgröße
   bestehen. Bei Unsicherheit: Standardwerte behalten, sie sind geprüft.

## Kontrastprüfung (manuell, kein externes Tool nötig)

Für zwei Hex-Farben reicht die relative Luminanz nach WCAG:
`L = 0.2126·R + 0.7152·G + 0.0722·B` (R/G/B linearisiert). Kontrastverhältnis
`(L1+0.05)/(L2+0.05)` mit `L1 ≥ L2`. Ziel: ≥ 4.5 für Fließtext, ≥ 3 für
großen/fetten Text. Bei Unsicherheit lieber die Default-Werte behalten statt
ungeprüft eine Markenfarbe für Text zu verwenden.
