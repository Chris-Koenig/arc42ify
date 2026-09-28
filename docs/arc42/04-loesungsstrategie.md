# 4. Lösungsstrategie

<!-- status: vollständig -->

Die Architektur von `arc42ify` lässt sich in einem Satz sagen: **Das
Sprachmodell liefert die Fachlichkeit, deterministische Python-Scripts
liefern Form und Prüfung.** Alles andere folgt daraus.

## 4.1 Grundentscheidungen

| Entscheidung | Was das konkret heißt | Details |
|---|---|---|
| **Agent schreibt JSON, nie SVG** | Der Agent beschreibt Knoten, Kanten und Rasterpositionen in einer `*.diagram.json`. Layout, Kantenführung, Stil und SVG-Ausgabe übernimmt `render_diagram.py`. | [ADR-004](09-architekturentscheidungen.md#adr-004-der-agent-schreibt-eine-json-spec-nie-svg) |
| **Eigener Renderer statt Mermaid/Graphviz** | ~700 Zeilen stdlib-Python, drei Diagrammarten, ein festes Design-System. | [ADR-001](09-architekturentscheidungen.md#adr-001-eigener-svg-renderer-statt-mermaid-oder-graphviz), [ADR-003](09-architekturentscheidungen.md#adr-003-nur-python-standardbibliothek) |
| **Knoten fest im Raster, nur Kanten automatisch** | Knoten stehen dort, wo `col`/`row` es sagen. Nur die Kanten führt ein Router rechtwinklig um alle Boxen herum. | [ADR-002](09-architekturentscheidungen.md#adr-002-explizites-rasterlayout-statt-auto-layout) |
| **Der Selbstcheck rechnet mit derselben Geometrie** | `self_check.py` importiert `render_diagram.py` und prüft das Layout, das tatsächlich gezeichnet wird — keine zweite, abweichende Berechnung. | [ADR-005](09-architekturentscheidungen.md#adr-005-selbstcheck-nutzt-die-layout-funktionen-des-renderers), [8.2](08-querschnittliche-konzepte.md#82-eine-geometrie-für-renderer-und-selbstcheck) |
| **Kurze Anleitung, Wissen zum Nachladen** | `SKILL.md` enthält nur Ablauf und Regeln (< 500 Zeilen). Kapitel-Zuordnung, Spec-Format und Stil stehen in `references/` und werden erst gelesen, wenn sie gebraucht werden. | [8.6](08-querschnittliche-konzepte.md#86-progressive-disclosure-in-der-agent-anleitung) |
| **Ein Skill-Ordner, drei Manifeste** | `skills/arc42ify/` ist der einzige Code; Claude Code, Copilot und Codex installieren ihn über eigene Manifeste. | [ADR-006](09-architekturentscheidungen.md#adr-006-ein-name-und-ein-skill-ordner-für-alle-hosts) |
| **Ausgabe sind normale Dateien im Ziel-Repo** | Markdown + SVG + JSON unter `docs/arc42/`. Kein Build-Schritt, kein Server, keine Datenbank. | [Kapitel 3](03-kontextabgrenzung.md) |

## 4.2 Wie die Strategie die Qualitätsziele trägt

| Qualitätsziel ([1.2](01-einfuehrung-und-ziele.md#12-qualitätsziele)) | Lösungsansatz |
|---|---|
| 1 · Läuft überall | Nur Standardbibliothek; Systemschriften statt Webfonts; stdout toleriert Konsolen, die nicht jedes Zeichen darstellen können; CI auf Python 3.8 und Windows. |
| 2 · Reproduzierbar | Keine Zufallswerte; alle Sortierungen mit festem Tiebreaker; Koordinaten auf das 4px-Raster gerundet; SVG immer mit LF geschrieben; Tests vergleichen eingecheckte SVGs Byte für Byte. |
| 3 · Lesbare Diagramme | Router mit Kostenfunktion (Knicke, Kreuzungen, gemeinsame Strecken teuer); eigener Anschlusspunkt je Kante; Labels nur auf freien Kantenstücken; `self_check.py` als Gate mit Hinweis, was zu ändern ist. |
| 4 · Ehrlich über Lücken | Reihenfolge „erst Fakten, dann Text, dann Bild“ und die Regel „offen markieren statt erfinden“ in `SKILL.md`. Keine technische Absicherung möglich — das Modell schreibt den Text. |

## 4.3 Was bewusst fehlt

- **Kein Auto-Layout für Knoten.** Wer ein Diagramm umbauen will, ändert
  `col`/`row` in der Spec.
- **Keine weiteren Diagrammarten** (ER, Zustandsautomat) — erst bei echtem
  Bedarf, siehe [vision.md](../vision.md) „Roadmap“.
- **Kein PNG/PDF-Export** — der Browser druckt SVG nach PDF.
- **Keine Agent-spezifische Logik.** Es gibt keinen Code, der nur für
  Claude, Copilot oder Codex läuft; alle Unterschiede stecken in Pfaden und
  Manifesten.
