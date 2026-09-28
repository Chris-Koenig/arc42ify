---
name: arc42-docs
description: Erzeugt oder aktualisiert arc42-Softwarearchitektur-Dokumentation aus einem Repo, einer Idee oder losen Texten — als Markdown + editorial-gestaltete SVG-Diagramme, ablagefähig direkt im GitHub-Repo unter docs/arc42/. Nutzen bei "erstelle die Architekturdoku", "arc42", "dokumentiere die Architektur", "Doku für dieses Repo", oder wenn Code/Ideen in eine strukturierte, visuelle Doku überführt werden sollen.
license: MIT
compatibility: Braucht Python 3.8+ (nur Standardbibliothek) und einen Agenten mit Terminal-Zugriff, z. B. Claude Code, GitHub Copilot oder OpenAI Codex. Kein Netzwerkzugriff nötig.
---

# arc42-docs

Verwandelt Code, eine Produktidee oder verstreute Notizen in eine vollständige
[arc42](https://arc42.de/)-Dokumentation: 12 Kapitel als Markdown, mit
sauberen, editorial gestalteten SVG-Diagrammen statt generischer
Mermaid-Boxen — und alles landet als normale Dateien im Repo
(`docs/arc42/`), versionierbar, ohne Build-Schritt, in jedem Browser und auf
GitHub direkt lesbar.

## Wann dieser Skill greift

- "Erstelle/aktualisiere die Architekturdokumentation nach arc42."
- "Dokumentiere dieses Repo" / "Dokumentiere diese Idee."
- Eine bestehende `docs/arc42/`-Struktur soll nach einer Code-Änderung
  aktualisiert werden (Diagramm + Text für das betroffene Kapitel neu
  erzeugen, Rest unberührt lassen).

**Nicht** für: API-Referenzdokumentation (Docstrings/OpenAPI — andere
Aufgabe), README-Schreiben (das ist Marketing/Onboarding, kein arc42), oder
ein einzelnes Ad-hoc-Diagramm ohne Doku-Kontext (dann direkt
`render_diagram.py` mit einer Spec verwenden, ohne das volle Kapitel-Gerüst).

## Skript-Pfade — zuerst klären

Die Scripts liegen im Skill-Ordner, nicht im Ziel-Repo. `SKILL_DIR` ist der
Ordner, in dem diese `SKILL.md` liegt:

- **Claude Code:** `${CLAUDE_SKILL_DIR}`.
- **GitHub Copilot, OpenAI Codex, andere:** der Pfad, aus dem diese Datei
  geladen wurde, z. B. `.claude/skills/arc42-docs`, `.agents/skills/arc42-docs`,
  `.github/skills/arc42-docs` oder `~/.agents/skills/arc42-docs`.

Alle Befehle unten laufen **im Root des Ziel-Repos** und rufen die Scripts
über `"$SKILL_DIR/scripts/…"` auf. Wenn `python3` fehlt (typisch unter
Windows), `python` oder `py -3` verwenden. Die Scripts brauchen nur die
Standardbibliothek — nichts installieren.

## Ablauf

### 1. Quelle bestimmen

- **Bestehendes Repo:** Code lesen — Ordnerstruktur, Entry-Points,
  Abhängigkeiten (`package.json`/`pyproject.toml`/`go.mod`/…),
  Infrastruktur-Dateien (`docker-compose.yml`, Terraform/Bicep, CI-Configs),
  README, offene Issues mit „tech-debt"/„risk"-Label.
- **Reine Idee (noch kein Code):** Aus der Beschreibung des Nutzers die
  gleichen Fakten extrahieren, die sonst aus Code kämen — welche Systeme
  reden miteinander, welche Technologie-Entscheidungen stehen schon fest,
  wer sind die Stakeholder. Kapitel, für die noch keine Information
  existiert, bleiben explizit als `<!-- TODO -->` markiert statt erfunden zu
  werden.
- **Lose Texte:** Wie Idee behandeln, aber zusätzlich prüfen, ob Texte
  bereits Diagramme (Mermaid, draw.io, Screenshots von Whiteboards)
  enthalten — deren *Inhalt* (Knoten, Kanten) übernehmen, nicht die
  Optik.

### 2. Gerüst anlegen

```bash
python3 "$SKILL_DIR/scripts/scaffold.py" . --lang de   # oder --lang en
```

Legt `docs/arc42/00-index.md` bis `12-glossar.md` plus
`docs/arc42/assets/diagrams/` an. Bereits vorhandene Dateien werden nie
überschrieben — sicher bei wiederholtem Aufruf. Sprache nach der Sprache des
Nutzers bzw. des Repos wählen.

### 3. Pro Kapitel: Inhalt sammeln, dann erst schreiben

Reihenfolge und Quelle pro Kapitel stehen in
`references/arc42-sections.md` — dort auch, welches Kapitel ein Diagramm
bekommt und welchen Typ. Nicht jedes Kapitel braucht ein Bild; siehe die
Faustregel am Ende dieser Datei und in `references/diagram-spec.md`
("Wann KEIN Diagramm").

**Reihenfolge pro Kapitel: erst die Fakten sammeln (Code lesen, Fragen
stellen wenn nötig), dann den Text schreiben, dann erst das Diagramm.**
Ein Diagramm zuerst zu bauen und den Text dazu zu erfinden, produziert
hübsche, aber inhaltsleere Doku — das ist genau der Fehler, den dieser
Skill vermeiden soll.

### 4. Diagramme erzeugen

Für jedes Diagramm:

1. `references/diagram-spec.md` für das JSON-Format des gewählten Typs
   lesen (`boxes` | `layers` | `sequence`).
2. Eine `<kapitel>-<name>.diagram.json` unter `docs/arc42/assets/diagrams/`
   schreiben, z. B. `03-kontext.diagram.json`, `06-checkout.diagram.json`.
3. Rendern:
   ```bash
   python3 "$SKILL_DIR/scripts/render_diagram.py" docs/arc42/assets/diagrams/<name>.diagram.json docs/arc42/assets/diagrams/<name>.svg
   ```
4. Prüfen:
   ```bash
   python3 "$SKILL_DIR/scripts/self_check.py" docs/arc42/assets/diagrams/<name>.diagram.json docs/arc42/assets/diagrams/<name>.svg
   ```
   Bei `FAIL`: Spec korrigieren (zu lange Labels kürzen, mehr als 2 fokale
   Elemente reduzieren, fehlende Referenzen fixen, Knoten umsetzen, wenn
   Kanten durch Boxen laufen), erneut rendern.
5. Im Markdown einbinden: `![<Alt-Text>](assets/diagrams/<name>.svg)`
   direkt über oder unter dem Absatz, den es illustriert — nie als
   einziger Kapitelinhalt. Der Alt-Text beschreibt, was das Bild aussagt,
   nicht nur seinen Typ.

Die Beispiel-Specs in `assets/templates/*.json` sind Startpunkte zum
Kopieren, keine Pflichtstruktur — Raster (`col`/`row`), Gruppen und Anzahl
Knoten frei an den tatsächlichen Fund im Code anpassen.

Das Farb-/Schrift-System steht in `references/style-guide.md` und ist die
einzige Stelle, die für ein Corporate-Design-Match geändert werden muss
(oder projektlokal per `"theme"`-Feld in der jeweiligen Spec).

### 5. Zusammenfassen und abschließen

- `docs/arc42/00-index.md` mit einer Tabelle Kapitel → Status
  (vollständig/Entwurf/TODO) aktuell halten.
- Kurze Zusammenfassung an den Nutzer: welche Kapitel neu/aktualisiert
  sind, welche noch offen (fehlende Information), Link/Pfad zur Doku.
- Nichts committen, wenn nicht ausdrücklich darum gebeten — Dateien liegen
  im Arbeitsverzeichnis des Ziel-Repos bereit für `git add`/PR durch den
  Nutzer oder eine anschließende explizite Bitte.

## Aktualisieren statt neu erzeugen

Wenn `docs/arc42/` schon existiert: nur die Kapitel neu erzeugen, die sich
durch die aktuelle Code-Änderung tatsächlich geändert haben (z. B. neue
Komponente → Kapitel 5 + zugehöriges Diagramm; neue Infrastruktur →
Kapitel 7). Alle anderen Kapitel unangetastet lassen. Diff-Charakter
bewahren, nicht die ganze Doku neu schreiben. Diagramme immer über ihre
`.diagram.json` ändern und neu rendern, nie das SVG von Hand editieren.

## Referenzen in diesem Skill (bei Bedarf nachladen)

| Datei | Wann lesen |
|---|---|
| `references/arc42-sections.md` | Immer zu Beginn — Kapitelübersicht, Quellen, Diagrammtyp je Kapitel |
| `references/diagram-spec.md` | Bevor ein Diagramm gebaut wird — JSON-Format je `kind` |
| `references/style-guide.md` | Nur bei Marken-/Farbanpassung nötig |
| `references/multi-agent-usage.md` | Bei Fragen zur Installation in Claude Code, Copilot, Codex |

## Es funktioniert, wenn…

- `docs/arc42/` im Ziel-Repo liegt, mit 13 Markdown-Dateien und einem
  `assets/diagrams/`-Ordner voller `.svg` + `.diagram.json`.
- Jedes SVG öffnet einzeln im Browser, offline, ohne Netzwerkzugriff.
- `self_check.py` für jede erzeugte Spec `OK` meldet.
- Kein Kapitel besteht nur aus einem Diagramm ohne erklärenden Text.
- Ein Kapitel ohne verfügbare Information ist als solches markiert, nicht
  mit plausibel klingendem, aber erfundenem Inhalt gefüllt.
