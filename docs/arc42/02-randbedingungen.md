# 2. Randbedingungen

<!-- status: vollständig -->

Alles hier ist entweder in Tests und CI festgeschrieben oder steht
ausdrücklich in [CONTRIBUTING.md](../../CONTRIBUTING.md). Wer eine dieser
Regeln bricht, merkt es spätestens am roten CI-Lauf.

## 2.1 Technische Randbedingungen

| ID | Randbedingung | Hintergrund | Wo festgeschrieben |
|---|---|---|---|
| TR1 | **Python 3.8 oder neuer, nur Standardbibliothek.** Kein `pip install`, kein `requirements.txt`. | Muss in jeder Agent-Sandbox laufen. Neue Abhängigkeiten (z. B. für PNG-Export) nur als optionales, getrenntes Script, nie in `render_diagram.py`. | `compatibility` in [`SKILL.md`](../../skills/arc42ify/SKILL.md), CI auf 3.8, Test `test_scripts_parse_as_python_3_8` |
| TR2 | **Kein Netzwerk, keine externen Programme** (kein Graphviz, kein Browser, keine Webfonts). | Sandboxes haben oft kein Netz. SVGs dürfen keine externen URLs enthalten. | README „Warum kein Mermaid“, `check_svg()` in `self_check.py` |
| TR3 | **Agent-Skills-Format.** `name` im Frontmatter = Ordnername, nur `a-z0-9-`, ≤ 64 Zeichen; `description` ≤ 1024 Zeichen und gültiges einfaches YAML (kein `": "`, kein `" #"`); `compatibility` ≤ 500 Zeichen; `SKILL.md` unter 500 Zeilen. | Sonst lädt der Host den Skill nicht oder schneidet die Beschreibung ab. | Klasse `SkillMetadata` in [`tests/test_arc42ify.py`](../../tests/test_arc42ify.py) |
| TR4 | **Trigger-Wörter in der `description`** (z. B. „arc42“, „Bausteinsicht“, „document the architecture“) dürfen nicht verschwinden. | Die `description` ist das Einzige, was ein Agent sieht, bevor er entscheidet, den Skill zu laden. | `SkillMetadata.TRIGGERS` |
| TR5 | **Ein Name, eine Version in allen Manifesten.** `name`, `version`, `description`, `author` … sind in `.claude-plugin/plugin.json` und `.codex-plugin/plugin.json` identisch; beide Marketplaces zeigen auf das Repo-Root. | Drei Hosts installieren denselben Ordner `skills/arc42ify/`. | Klasse `PluginManifests` |
| TR6 | **SVGs mit LF-Zeilenenden**, auch unter Windows. | Tests vergleichen jedes eingecheckte SVG Byte für Byte mit einem frischen Render. | [`.gitattributes`](../../.gitattributes), `newline="\n"` in `render()` |
| TR7 | **Alle Koordinaten im 4px-Raster**, ein Akzent, keine Schatten, 1px-Rahmen. | Das Design-System ist Teil des Produkts, nicht Geschmackssache. | [`style-guide.md`](../../skills/arc42ify/references/style-guide.md), `snap()`, Test `test_shapes_sit_on_the_4px_grid` |
| TR8 | **Relative Links in allen Markdown-Dateien müssen auflösen** — auch in dieser Doku. | Kaputte Links fallen sonst erst Leser:innen auf. | Test `test_relative_markdown_links_resolve` |

## 2.2 Organisatorische Randbedingungen

| ID | Randbedingung | Hintergrund |
|---|---|---|
| OR1 | **MIT-Lizenz** ([LICENSE](../../LICENSE)). | Nutzung in Firmenprojekten ohne Rückfrage. |
| OR2 | **Deutsch für Kapitel- und Anleitungstext, Englisch für Code-Kommentare und Bezeichner.** | Zielgruppe sind deutschsprachige arc42-Nutzer:innen; Code bleibt international lesbar ([CONTRIBUTING.md](../../CONTRIBUTING.md), „Stil“). |
| OR3 | **Alle 12 arc42-Kapitel bleiben.** Ein Kapitel darf leer oder offen sein, aber nicht fehlen. | arc42 definiert sie verbindlich. |
| OR4 | **Bewusst kleiner Umfang.** Drei Diagrammarten, drei Scripts. Neue Diagrammtypen nur mit Template, Tests und Doku. | Einfachheit ist das Verkaufsargument; jede Erweiterung kostet an fünf Stellen Pflege ([5.3](05-bausteinsicht.md#53-whitebox-render_diagrampy-ebene-3)). |
| OR5 | **Tests vor jedem PR:** `python3 -m unittest discover -s tests -v`. Dasselbe läuft in CI bei jedem Push und Pull Request. | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) |
| OR6 | **Der Skill committet nicht selbst.** Die erzeugte Doku liegt im Arbeitsverzeichnis, bis die Nutzer:in sie prüft. | Doku wird wie Code im Pull Request reviewt. |

## 2.3 Konventionen

- Diagramme werden **nur über ihre `.diagram.json`** geändert und dann neu
  gerendert — nie das SVG von Hand bearbeiten.
- Neue Prüfregel im Selbstcheck = neue kaputte Fixture unter
  `tests/fixtures/fail/` plus erwartete Meldung in
  `CheckerCatchesDefects.EXPECTED`. Eine Regel ohne Fixture gilt als nicht
  vorhanden.
- Geometrie, die der Selbstcheck prüfen soll, gehört in eine
  `layout_<kind>()`-Funktion im Renderer, nicht in den Check
  ([8.2](08-querschnittliche-konzepte.md#82-eine-geometrie-für-renderer-und-selbstcheck)).
