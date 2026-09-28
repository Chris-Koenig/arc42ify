# 9. Architekturentscheidungen

<!-- status: vollständig — ADRs aus README, Vision, CONTRIBUTING und Git-History rekonstruiert -->

Im Repo gibt es keine eigenen ADR-Dateien. Die folgenden Entscheidungen sind
aus [README](../../README.md), [vision.md](../vision.md),
[CONTRIBUTING.md](../../CONTRIBUTING.md), den Referenzen des Skills und der
Git-History rekonstruiert. Sie standen alle schon im ersten Commit
(`02778c9`, 2026-09-28), außer ADR-006.

| ADR | Titel | Status |
|---|---|---|
| [ADR-001](#adr-001-eigener-svg-renderer-statt-mermaid-oder-graphviz) | Eigener SVG-Renderer statt Mermaid oder Graphviz | angenommen |
| [ADR-002](#adr-002-explizites-rasterlayout-statt-auto-layout) | Explizites Rasterlayout statt Auto-Layout | angenommen |
| [ADR-003](#adr-003-nur-python-standardbibliothek) | Nur Python-Standardbibliothek | angenommen |
| [ADR-004](#adr-004-der-agent-schreibt-eine-json-spec-nie-svg) | Der Agent schreibt eine JSON-Spec, nie SVG | angenommen |
| [ADR-005](#adr-005-selbstcheck-nutzt-die-layout-funktionen-des-renderers) | Selbstcheck nutzt die Layout-Funktionen des Renderers | angenommen |
| [ADR-006](#adr-006-ein-name-und-ein-skill-ordner-für-alle-hosts) | Ein Name und ein Skill-Ordner für alle Hosts | angenommen |

---

## ADR-001: Eigener SVG-Renderer statt Mermaid oder Graphviz

**Status:** angenommen · im ersten Commit

**Kontext.** Architekturdiagramme sollen nach etwas aussehen, das man ohne
Nacharbeit zeigen kann. Mermaid sieht in jedem Tool gleich generisch aus,
kennt kein Fokus-Element und erzeugt bei Auto-Layout oft verschachtelte
Pfeile. Graphviz (`dot`) ist ein Binary, das in vielen Agent-Sandboxes und
CI-Runnern fehlt und sich dort ohne Netz und Root-Rechte nicht nachinstallieren
lässt.

**Entscheidung.** Ein eigener Renderer (`render_diagram.py`) in reinem
Python, mit festem Design-System (ein Akzent, keine Schatten,
1px-Hairlines, 4px-Raster), inspiriert von
[diagram-design](https://github.com/cathrynlavery/diagram-design).

**Konsequenzen.**
- \+ Einheitlicher, ruhiger Stil; ein Theme-Override reicht für Corporate
  Design.
- \+ Läuft überall, wo Python läuft.
- − Jede neue Diagrammart ist eigener Code mit Template, Tests und Doku
  (siehe [CONTRIBUTING.md](../../CONTRIBUTING.md)).
- − Kein Ökosystem: Viewer, Editoren und Plugins für Mermaid helfen hier nicht.

## ADR-002: Explizites Rasterlayout statt Auto-Layout

**Status:** angenommen · im ersten Commit

**Kontext.** Auto-Layout macht Diagramme unvorhersehbar: Eine kleine
Änderung kann das ganze Bild umwerfen, und ein Agent kann das Ergebnis nicht
sehen.

**Entscheidung.** Knoten stehen dort, wo `col`/`row` in der Spec es sagen.
Automatisch sind nur die Kanten: Ein Router führt sie rechtwinklig um alle
Boxen herum ([5.3](05-bausteinsicht.md#53-whitebox-render_diagrampy-ebene-3)).

**Konsequenzen.**
- \+ Reproduzierbar; ein Diff in der Spec zeigt genau, was sich im Bild ändert.
- \+ Der Agent (oder Mensch) behält die Kontrolle über die Anordnung, z. B.
  „eine Spalte pro Tiefe“.
- − Wer die Spec schreibt, muss das Raster planen. Schlechte Platzierung
  meldet der Selbstcheck, korrigieren muss sie der Agent.

## ADR-003: Nur Python-Standardbibliothek

**Status:** angenommen · im ersten Commit

**Kontext.** Der Skill läuft in fremden Umgebungen: Sandboxes von Claude
Code, Copilot und Codex, CI-Runner, Windows-Laptops. Dort gibt es oft kein
Netz, kein `pip` und keine Admin-Rechte.

**Entscheidung.** Alle Scripts nutzen nur die Standardbibliothek und laufen
ab Python 3.8. Optionale Erweiterungen mit Abhängigkeiten (etwa PNG-Export)
kämen in ein getrenntes Script, nie in `render_diagram.py`.

**Konsequenzen.**
- \+ Keine Installation; `python3 script.py` reicht.
- − Keine echte Textmessung (keine Schriftbibliothek) — Textbreiten werden
  geschätzt ([8.4](08-querschnittliche-konzepte.md#84-geschätzte-textbreiten)).
- − Kein Syntax-Komfort neuerer Python-Versionen (`match`, `X | Y`-Typen
  usw.); der Test `test_scripts_parse_as_python_3_8` und der CI-Job auf 3.8
  fangen das ab.

## ADR-004: Der Agent schreibt eine JSON-Spec, nie SVG

**Status:** angenommen · im ersten Commit

**Kontext.** Sprachmodelle können SVG schreiben, aber nicht zuverlässig:
Koordinaten stimmen nicht, Texte laufen aus Boxen, der Stil driftet von
Diagramm zu Diagramm.

**Entscheidung.** Der Agent liefert nur die Fachlichkeit — Knoten, Kanten,
Beschriftungen, Rasterpositionen — als JSON
([`diagram-spec.md`](../../skills/arc42ify/references/diagram-spec.md)). Das
Script übernimmt Layout, Stil und Ausgabe. SVGs werden nie von Hand
bearbeitet; Änderungen laufen über die Spec.

**Konsequenzen.**
- \+ Gleicher Stil in allen Diagrammen, egal welches Modell sie beschreibt.
- \+ Die Spec ist klein, lesbar und im Pull Request gut reviewbar.
- − Was das Spec-Format nicht ausdrücken kann, geht nicht (z. B. freie
  Positionen, Farben je Knoten außer `focal`/`external`).

## ADR-005: Selbstcheck nutzt die Layout-Funktionen des Renderers

**Status:** angenommen · im ersten Commit

**Kontext.** Der Agent sieht das gerenderte Bild nicht. Ein Check, der
Kollisionen selbst nachrechnet, würde früher oder später vom Renderer
abweichen und dann Fehler übersehen oder falschen Alarm geben.

**Entscheidung.** `self_check.py` importiert `render_diagram.py` und prüft
das Ergebnis von `layout_boxes()` bzw. `layout_sequence()` — dieselben Zahlen,
die gezeichnet werden. Neue prüfbare Geometrie gehört in eine
`layout_<kind>()`-Funktion.

**Konsequenzen.**
- \+ Check und Bild können nicht auseinanderlaufen.
- \+ Der Check kann konkrete Hinweise geben („label … overlaps node …“).
- − Enge Kopplung: Eine Umbenennung in `render_diagram.py` bricht
  `self_check.py`; beide müssen immer gemeinsam geändert werden.

## ADR-006: Ein Name und ein Skill-Ordner für alle Hosts

**Status:** angenommen · 2026-09-28 (Commit `f5677ed`)

**Kontext.** Der Skill hieß anfangs `arc42-docs`, das Repo und die
Marketplaces `arc42ify`. Das führte zu Installationsbefehlen wie
`/plugin install arc42-docs@arc42ify` und zu der Frage, wie das Ding
eigentlich heißt. Außerdem verlangt das Agent-Skills-Format, dass `name` im
Frontmatter gleich dem Ordnernamen ist, und drei Hosts lesen drei
verschiedene Manifeste.

**Entscheidung.** Überall `arc42ify`: Repo, Skill-Ordner
`skills/arc42ify/`, `name` in `SKILL.md`, Plugin-Name in allen Manifesten.
Es gibt genau einen Skill-Ordner; Claude Code, Copilot und Codex zeigen mit
eigenen Manifesten darauf. Die Klasse `PluginManifests` in den Tests prüft,
dass Name, Version, Beschreibung, Autor usw. in den Manifesten
übereinstimmen.

**Konsequenzen.**
- \+ Ein Befehl pro Host, `arc42ify@arc42ify`, kein Raten.
- \+ Kein doppelter Code für unterschiedliche Hosts.
- − Bestehende Installationen unter dem alten Namen bleiben bestehen und
  müssen entfernt und neu installiert werden.
- − Version und Beschreibung stehen in mehreren Dateien und werden von Hand
  gepflegt ([R5](11-risiken-und-technische-schulden.md#111-risiken)).
