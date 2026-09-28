# 12. Glossar

<!-- status: vollständig -->

| Begriff | Bedeutung |
|---|---|
| **Agent-Host** | Programm, das ein Sprachmodell mit Datei- und Terminalzugriff ausführt und Skills lädt: Claude Code, GitHub Copilot (CLI, VS Code, Cloud-Agent), OpenAI Codex. |
| **Agent Skill** | Ordner mit einer `SKILL.md` (YAML-Frontmatter + Anleitung) und optionalen Referenzen, Scripts und Assets, nach der offenen [Agent-Skills-Spezifikation](https://agentskills.io/specification). |
| **ADR** | Architecture Decision Record — eine Entscheidung mit Kontext, Entscheidung und Konsequenzen; siehe [Kapitel 9](09-architekturentscheidungen.md). |
| **Akzent** | Die eine Hervorhebungsfarbe (`accent`, Standard `#d9622b`). Nur für fokale Elemente. |
| **Bohnenwerk-Shop** | Fiktives Beispielprojekt in `docs-example/`, dessen vollständige arc42-Doku zeigt, was der Skill erzeugt. |
| **`boxes` / `layers` / `sequence`** | Die drei Diagrammarten (`kind`) des Renderers: Knoten und Kanten auf einem Raster (Kapitel 3, 5, 7); gestapelte Schichten (Kapitel 8, ggf. 4); Sequenzdiagramm (Kapitel 6). |
| **`col` / `row`** | Ganzzahlige Rasterposition eines Knotens in einer `boxes`-Spec. Eine Zelle ist `CELL_W` × `CELL_H` Pixel groß. |
| **`description`** | Feld im Frontmatter von `SKILL.md`. Das Einzige, was ein Agent-Host vor dem Laden sieht — entscheidet, ob der Skill genutzt wird. |
| **external** | `kind` eines Knotens außerhalb der eigenen Verantwortung; grau gefüllt, nie hervorgehoben. |
| **Fixture** | Test-Spec unter `tests/fixtures/`. `fail/` enthält absichtlich kaputte Specs, die eine bestimmte Meldung auslösen müssen; `pass/` enthält gute Specs, die sauber bleiben müssen. |
| **focal / fokal** | `kind` eines Knotens, einer Kante, Schicht oder Nachricht, die den Akzent bekommt. Höchstens zwei pro Diagramm. |
| **Gerüst** | Die von `scaffold.py` angelegten 13 Markdown-Dateien plus `assets/diagrams/`. |
| **Gitter** | Das 12px-Raster (`STEP`), auf dem der Router Kanten führt. Nicht zu verwechseln mit dem 4px-Raster (`GRID`) für alle Koordinaten. |
| **Gruppe** | Gestrichelter Rahmen um mehrere Knoten einer `boxes`-Spec, z. B. System- oder Netzwerkgrenze. |
| **Hairline** | 1px-Rahmenlinie in der Farbe `hairline`. |
| **Lane** | Teilnehmer eines Sequenzdiagramms mit Kopfbox und senkrechter Lebenslinie. |
| **Marketplace** | Katalog von Plugins in einem Git-Repo. Dieses Repo ist zugleich Marketplace und Plugin (`.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`). |
| **Plugin-Manifest** | `plugin.json`, mit der ein Host ein Plugin erkennt: `.claude-plugin/plugin.json` (Claude Code, Copilot CLI), `.codex-plugin/plugin.json` (Codex). |
| **Port** | Anschlusspunkt einer Kante auf einer Boxseite. Jedes Kantenende bekommt einen eigenen. |
| **Referenz** | Markdown-Datei unter `skills/arc42ify/references/`, die der Agent nur bei Bedarf nachlädt. |
| **Router** | Klasse in `render_diagram.py`, die Kanten rechtwinklig um alle Boxen herum führt (Dijkstra mit Kosten für Knicke, Kreuzungen, gemeinsame Strecken). |
| **Selbstcheck** | `self_check.py`: prüft Spec und Geometrie eines Diagramms, meldet `OK` oder `FAIL`. |
| **`SKILL_DIR`** | Der Ordner, in dem `SKILL.md` liegt; je nach Host unterschiedlich (z. B. `${CLAUDE_SKILL_DIR}`, `.agents/skills/arc42ify`). Die Scripts werden immer von dort aufgerufen. |
| **`snap()`** | Rundet einen Wert auf das 4px-Raster. |
| **Spec** | JSON-Beschreibung eines Diagramms (`*.diagram.json`). Quelle der Wahrheit — das SVG wird daraus erzeugt und nie von Hand bearbeitet. |
| **Theme / Design-Token** | Benannte Farbe oder Schrift (`paper`, `ink`, `accent` …) in `DEFAULT_THEME`; pro Spec über `"theme"` überschreibbar. |
| **Trigger-Wörter** | Begriffe in der `description`, an denen Agenten erkennen, dass der Skill passt („arc42“, „Bausteinsicht“, „document the architecture“ …). Durch Tests geschützt. |
| **Ziel-Repo** | Das Repo, das dokumentiert wird und `docs/arc42/` bekommt — im Normalfall nicht dieses Repo. |
