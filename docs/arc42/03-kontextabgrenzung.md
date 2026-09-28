# 3. Kontextabgrenzung

<!-- status: vollständig -->

## 3.1 Fachlicher Kontext

`arc42ify` hat keine eigene Oberfläche und keinen eigenen Prozess. Es wird
immer von einem **Agent-Host** geladen und ausgeführt: Die Nutzer:in gibt
dem Agenten einen Auftrag, der Agent erkennt an der `description` in
`SKILL.md`, dass der Skill passt, folgt dessen Ablauf und ruft die Scripts
auf. Das Ergebnis landet als Dateien im **Ziel-Repo** — dem Repo, das
dokumentiert wird, nicht diesem hier.

![Fachlicher Kontext: Die Nutzer:in beauftragt den Agent-Host; der Host installiert arc42ify aus dem GitHub-Marketplace und lädt den Skill; arc42ify liest Code aus dem Ziel-Repo und schreibt Markdown und SVG nach docs/arc42/; Leser:innen lesen die Doku dort](assets/diagrams/03-kontext.svg)

| Partner | Was fließt | Warum |
|---|---|---|
| Nutzer:in | Auftrag in natürlicher Sprache → Agent-Host; Zusammenfassung ← Host | Hauptnutzung. Optional ruft sie die Scripts auch ohne Agent auf (CI, Handbetrieb). |
| Agent-Host (Claude Code, Copilot, Codex) | lädt `SKILL.md` und bei Bedarf `references/*.md`; startet die Scripts im Terminal | Der Host ist die Laufzeitumgebung des Skills. Er entscheidet, *ob* der Skill geladen wird — nur anhand der `description`. |
| GitHub-Marketplace (`Chris-Koenig/arc42ify`) | Plugin-Manifeste und der Ordner `skills/arc42ify/` → Host | Verteilweg für die Plugin-Installation. Alternativ wird der Ordner von Hand kopiert. |
| Ziel-Repo | Code, Konfiguration, README → Agent; Markdown, JSON-Specs, SVGs → `docs/arc42/` | Quelle und Ablage. Der Skill schreibt nur unter `docs/arc42/`. |
| Leser:innen | lesen `docs/arc42/` auf GitHub oder offline im Browser | Das eigentliche Publikum der erzeugten Doku. |

**Wichtig für neue Entwickler:innen:** Den größten Teil der Arbeit — Code
lesen, Kapiteltext schreiben, JSON-Specs formulieren — macht das Sprachmodell
des Hosts. `arc42ify` steuert das nur über Text (`SKILL.md`, `references/`).
Deterministisch und testbar sind allein die drei Scripts. Das prägt, was
sich prüfen lässt und was nicht ([Kapitel 11](11-risiken-und-technische-schulden.md)).

## 3.2 Technischer Kontext

| Schnittstelle | Richtung | Format / Protokoll | Details |
|---|---|---|---|
| Skill-Erkennung | Host → Skill | YAML-Frontmatter in `SKILL.md` (`name`, `description`, `license`, `compatibility`) | Regeln in [TR3/TR4](02-randbedingungen.md#21-technische-randbedingungen) |
| Nachladen von Wissen | Host → Skill | Markdown-Dateien unter `references/`, per Pfad aus `SKILL.md` | Tabelle „Referenzen in diesem Skill“ in `SKILL.md` |
| Script-Aufrufe | Host → Scripts | Kommandozeile im Root des Ziel-Repos; Exit-Code 0 = OK, 1 = Fehler; Meldungen auf stdout | `scaffold.py <repo> [--lang de\|en]`, `render_diagram.py <spec> <svg>`, `self_check.py <spec> [<svg>]` |
| Diagramm-Spec | Agent → Renderer | JSON, UTF-8, `kind` = `boxes` \| `layers` \| `sequence` | [`diagram-spec.md`](../../skills/arc42ify/references/diagram-spec.md) |
| Ausgabe | Scripts → Ziel-Repo | Markdown (UTF-8, LF), SVG 1.1 mit `<title>`/`<desc>`, ohne externe URLs | `docs/arc42/*.md`, `docs/arc42/assets/diagrams/*.svg` |
| Plugin-Installation | Marketplace → Host | JSON-Manifeste: `.claude-plugin/` (Claude Code, Copilot CLI), `.codex-plugin/` + `.agents/plugins/` (Codex) | [docs/installation.md](../installation.md) |
| Laufzeit | Scripts → Python | CPython ≥ 3.8, `python3`, `python` oder `py -3` | keine Pakete, kein Netz |

Der Skill-Pfad unterscheidet sich je Host (`${CLAUDE_SKILL_DIR}` in Claude
Code, `.agents/skills/arc42ify` in Codex …). `SKILL.md` löst das mit einer
Variablen `SKILL_DIR`, die der Agent vor dem ersten Script-Aufruf klärt —
die Scripts liegen im Skill-Ordner, nie im Ziel-Repo.
