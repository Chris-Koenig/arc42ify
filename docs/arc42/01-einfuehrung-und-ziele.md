# 1. Einführung und Ziele

<!-- status: Entwurf — Priorisierung der Qualitätsziele bestätigen -->

## 1.1 Aufgabenstellung

`arc42ify` ist ein **Agent-Skill**: eine Anleitung plus drei kleine
Python-Scripts, die ein KI-Agent (Claude Code, GitHub Copilot, OpenAI Codex)
lädt, wenn jemand ihn um Architekturdoku bittet. Der Agent liest ein Repo,
eine Produktidee oder lose Notizen und legt daraus im Ziel-Repo unter
`docs/arc42/` eine vollständige [arc42](https://arc42.de/)-Dokumentation an:
12 Kapitel als Markdown, dazu Diagramme als SVG.

Das Besondere sind die Diagramme. Der Agent zeichnet sie nicht selbst,
sondern beschreibt nur *was* zu sehen ist (Knoten, Kanten, Nachrichten) in
einer kleinen JSON-Spec. Ein Renderer ohne Fremdabhängigkeiten macht daraus
ein SVG in einem festen, ruhigen Stil, und ein Selbstcheck prüft das Ergebnis,
bevor der Agent „fertig“ meldet.

Warum es das Projekt gibt, steht in [docs/vision.md](../vision.md): arc42
scheitert in der Praxis an veraltetem Text und an Diagrammen, die entweder
nach Whiteboard oder nach generischem Mermaid aussehen. `arc42ify` soll
Architekturdoku zu etwas machen, das ein Agent bei jeder relevanten
Code-Änderung nebenbei mitpflegt.

**Wesentliche Anforderungen**

| ID | Anforderung | Wo umgesetzt |
|---|---|---|
| F1 | Aus Repo, Idee oder Notizen alle 12 arc42-Kapitel als Markdown unter `docs/arc42/` erzeugen. | [`SKILL.md`](../../skills/arc42ify/SKILL.md), [`scaffold.py`](../../skills/arc42ify/scripts/scaffold.py) |
| F2 | Bestehende Doku nach einer Code-Änderung aktualisieren — nur die betroffenen Kapitel. | `SKILL.md`, Abschnitt „Aktualisieren statt neu erzeugen“ |
| F3 | Diagramme für Kontext, Bausteine, Verteilung (`boxes`), Abläufe (`sequence`) und Schichten (`layers`) aus einer JSON-Spec rendern. | [`render_diagram.py`](../../skills/arc42ify/scripts/render_diagram.py) |
| F4 | Jede Spec und jedes SVG automatisch auf Fehler prüfen (Kanten durch Boxen, zu lange Labels, zu viele Akzente …). | [`self_check.py`](../../skills/arc42ify/scripts/self_check.py) |
| F5 | Ohne Anpassung in Claude Code, GitHub Copilot und OpenAI Codex laufen, als Plugin oder als kopierter Ordner. | Manifeste in `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/` |
| F6 | Fehlende Information als offen markieren statt sie zu erfinden. | `SKILL.md`, Schritt 1 und „Es funktioniert, wenn …“ |

## 1.2 Qualitätsziele

Die Ziele stehen nicht als Liste im Repo. Sie sind aus
[vision.md](../vision.md) („Prinzipien“), dem README und dem, was die Tests
absichern, abgeleitet. **Offen:** Die Reihenfolge ist ein Vorschlag und muss
vom Maintainer bestätigt werden.

| Prio | Qualitätsziel | Motivation | Abgesichert durch |
|---|---|---|---|
| 1 | **Läuft überall** — Python 3.8+ nur mit Standardbibliothek, offline, unter Linux, macOS und Windows, in allen drei Agent-Hosts. | Agent-Sandboxes und CI-Runner haben oft kein Netz und keine Root-Rechte; ein fehlendes `dot`-Binary oder `pip install` würde den Skill dort unbrauchbar machen. | CI-Matrix (3.8, 3.13, Windows), Test `test_scripts_parse_as_python_3_8` |
| 2 | **Reproduzierbar** — dieselbe Spec ergibt Byte für Byte dasselbe SVG. | Diagramme liegen versioniert im Repo; ein Re-Render ohne inhaltliche Änderung darf keinen Diff erzeugen. | Test `test_committed_svgs_match_a_fresh_render`, `.gitattributes` |
| 3 | **Lesbare Diagramme** — keine Kante durch eine Box, kein Label über einer Kante, höchstens zwei Akzente. | Ein Agent sieht das gerenderte Bild nicht. Nur ein maschineller Check verhindert, dass kaputte Diagramme ausgeliefert werden. | `self_check.py`, Fail-Fixtures unter `tests/fixtures/fail/` |
| 4 | **Ehrlich über Lücken** — kein erfundener Inhalt. | Plausibel klingender, aber falscher Text ist schlimmer als ein offenes Kapitel. | Nur durch die Anleitung in `SKILL.md` — kein automatischer Check (siehe [R3](11-risiken-und-technische-schulden.md#111-risiken)) |

Konkrete Szenarien zu jedem Ziel stehen in
[Kapitel 10](10-qualitaetsanforderungen.md).

## 1.3 Stakeholder

| Rolle | Erwartung an die Architektur |
|---|---|
| **Neue Entwickler:innen im Team** (Zielgruppe dieser Doku) | Schnell verstehen, welcher Teil was tut, wo man etwas ändert und was die Tests absichern. |
| Maintainer (Christoph König) | Kleiner, überschaubarer Umfang; Beiträge, die diese Einfachheit erhalten ([CONTRIBUTING.md](../../CONTRIBUTING.md)). |
| Nutzer:innen des Skills — Entwickler:innen und Architekt:innen in anderen Projekten, vorwiegend deutschsprachig | Installation in einem Schritt, Doku ohne Build-Schritt, Diagramme, die man ohne Nacharbeit zeigen kann. |
| Leser:innen der erzeugten Doku | Markdown und SVG, die auf GitHub und offline im Browser direkt lesbar sind. |
| Agent-Hosts (Claude Code, Copilot, Codex) | Keine Menschen, aber harte Anforderungen: gültiges `SKILL.md`-Frontmatter, erkennbare Trigger-Wörter, erwarteter Ordnername. Details in [Kapitel 2](02-randbedingungen.md). |
