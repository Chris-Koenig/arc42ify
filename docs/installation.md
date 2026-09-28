# Installation

`arc42-docs` ist ein Agent-Skill im offenen
[Agent-Skills-Format](https://agentskills.io/specification). Er läuft in
**Claude Code**, **GitHub Copilot** und **OpenAI Codex** — ohne Anpassung,
nur der Ablageort unterscheidet sich.

- [Voraussetzungen](#voraussetzungen)
- [Welcher Weg passt?](#welcher-weg-passt)
- [Claude Code](#claude-code)
- [GitHub Copilot](#github-copilot)
- [OpenAI Codex](#openai-codex)
- [Ein Repo für alle drei Hosts](#ein-repo-für-alle-drei-hosts)
- [Aktualisieren und entfernen](#aktualisieren-und-entfernen)
- [Fehlersuche](#fehlersuche)

## Voraussetzungen

| Was | Warum |
|---|---|
| Python 3.8 oder neuer | Die Diagramm-Scripts. Nur Standardbibliothek — kein `pip install`. |
| Ein Agent mit Terminal-Zugriff | Der Agent führt die Scripts selbst aus. Ohne Shell entsteht nur Text, keine SVGs. |
| Git (optional) | Zum Klonen dieses Repos für die manuelle Installation. |

Kurztest, ob Python da ist:

```bash
python3 --version
```

Unter Windows heißt der Befehl oft `python` oder `py -3`. Der Skill weiß das
und probiert die Varianten durch.

## Welcher Weg passt?

| Du willst … | Weg |
|---|---|
| … den Skill in **Claude Code** für alle deine Projekte | [Claude-Code-Plugin](#a-als-plugin-empfohlen) |
| … den Skill in der **Copilot CLI** für alle deine Projekte | [Copilot-CLI-Plugin](#a-als-plugin-copilot-cli) |
| … den Skill in **Codex** für alle deine Projekte | [persönlicher Skill-Ordner](#a-persönlich-alle-projekte) |
| … dass **das ganze Team** den Skill in einem Repo hat, egal mit welchem Agenten | [Ein Repo für alle drei Hosts](#ein-repo-für-alle-drei-hosts) |
| … den Skill im **Copilot-Cloud-Agenten** auf GitHub | [Im Repo ablegen](#b-im-repo-vs-code-cli-cloud-agent) |

Für die manuellen Wege brauchst du eine lokale Kopie dieses Repos:

```bash
git clone https://github.com/Chris-Koenig/arc42ify.git
```

Im Folgenden steht `ARC42IFY` für den Pfad dieses Klons.

---

## Claude Code

### A) Als Plugin (empfohlen)

Dieses Repo ist zugleich Plugin und Marketplace. In einer Claude-Code-Session:

```text
/plugin marketplace add Chris-Koenig/arc42ify
/plugin install arc42-docs@arc42ify
```

Oder direkt im Terminal:

```bash
claude plugin marketplace add Chris-Koenig/arc42ify
```

```bash
claude plugin install arc42-docs@arc42ify
```

Als Plugin heißt der Befehl `/arc42-docs:arc42-docs`; solange kein anderer
Skill `arc42-docs` heißt, reicht auch `/arc42-docs`.

### B) Persönlich, ohne Plugin

Für alle Projekte auf deinem Rechner:

```bash
mkdir -p ~/.claude/skills
cp -R ARC42IFY/skills/arc42-docs ~/.claude/skills/arc42-docs
```

### C) Im Projekt

Für ein einzelnes Repo, mit eingecheckt — dann haben alle im Team den Skill:

```bash
mkdir -p .claude/skills
cp -R ARC42IFY/skills/arc42-docs .claude/skills/arc42-docs
```

### Prüfen

Neue Session starten und `/` tippen — `arc42-docs` steht in der Liste.
Beim Plugin zusätzlich:

```bash
claude plugin list
```

---

## GitHub Copilot

Copilot liest Agent-Skills in der **Copilot CLI**, im **Agent-Modus von VS
Code** (und JetBrains) und im **Copilot-Cloud-Agenten** auf GitHub. Eine
Einstellung ist dafür nicht nötig.

### A) Als Plugin (Copilot CLI)

Direkt aus diesem Repo:

```bash
copilot plugin install Chris-Koenig/arc42ify
```

Oder über den Marketplace:

```bash
copilot plugin marketplace add Chris-Koenig/arc42ify
```

```bash
copilot plugin install arc42-docs@arc42ify
```

### B) Im Repo (VS Code, CLI, Cloud-Agent)

Copilot sucht Projekt-Skills in `.github/skills/`, `.claude/skills/` und
`.agents/skills/`. Der übliche Ort für Copilot:

```bash
mkdir -p .github/skills
cp -R ARC42IFY/skills/arc42-docs .github/skills/arc42-docs
```

Einchecken — dann steht der Skill auch dem Copilot-Cloud-Agenten zur
Verfügung, wenn er an einem Issue arbeitet. Wer das Repo zusätzlich mit
Claude Code oder Codex nutzt, nimmt stattdessen das
[Setup für alle drei Hosts](#ein-repo-für-alle-drei-hosts).

### C) Persönlich

Für alle Projekte auf deinem Rechner:

```bash
mkdir -p ~/.copilot/skills
cp -R ARC42IFY/skills/arc42-docs ~/.copilot/skills/arc42-docs
```

`~/.agents/skills/` funktioniert ebenfalls und wird auch von Codex gelesen.

### Prüfen

```bash
copilot skill list
```

`arc42-docs` steht unter „Project skills“, „Personal skills“ oder „Plugin
skills“. In VS Code: im Chat den Agent-Modus wählen und `/arc42-docs` tippen.

---

## OpenAI Codex

Codex liest Skills in der **Codex CLI** und der **IDE-Extension**. Kein
Feature-Flag nötig.

### A) Persönlich (alle Projekte)

```bash
mkdir -p ~/.agents/skills
cp -R ARC42IFY/skills/arc42-docs ~/.agents/skills/arc42-docs
```

### B) Im Repo

Codex sucht in `.agents/skills/` im aktuellen Ordner und in allen
übergeordneten Ordnern bis zum Repo-Root:

```bash
mkdir -p .agents/skills
cp -R ARC42IFY/skills/arc42-docs .agents/skills/arc42-docs
```

### Prüfen

In der Codex CLI `/skills` eingeben — `arc42-docs` steht in der Liste.
Aufrufen lässt er sich mit `$arc42-docs`.

---

## Ein Repo für alle drei Hosts

Wenn im Team verschiedene Agenten im Einsatz sind: den Skill **einmal** echt
unter `.claude/skills/` ablegen und für Codex verlinken.

```bash
mkdir -p .claude/skills .agents/skills
cp -R ARC42IFY/skills/arc42-docs .claude/skills/arc42-docs
ln -s ../../.claude/skills/arc42-docs .agents/skills/arc42-docs
git add .claude/skills .agents/skills
```

| Host | liest | Ergebnis |
|---|---|---|
| Claude Code | `.claude/skills/arc42-docs` | direkt |
| GitHub Copilot | `.claude/skills/` und `.agents/skills/` | findet ihn an beiden Stellen, listet ihn einmal |
| OpenAI Codex | `.agents/skills/arc42-docs` | folgt dem Symlink |

Unter Windows ohne Symlinks (`core.symlinks=false`) statt `ln -s` eine zweite
Kopie nach `.agents/skills/arc42-docs` legen und beide beim Aktualisieren
gemeinsam ersetzen.

## Aktualisieren und entfernen

| Installiert als | Aktualisieren | Entfernen |
|---|---|---|
| Claude-Code-Plugin | `claude plugin marketplace update arc42ify`, dann `claude plugin update arc42-docs@arc42ify` | `claude plugin uninstall arc42-docs@arc42ify` |
| Copilot-CLI-Plugin | `copilot plugin update arc42-docs` (bzw. `arc42-docs@arc42ify`) | `copilot plugin uninstall arc42-docs` |
| Kopierter Ordner | `git -C ARC42IFY pull`, dann den Ordner erneut kopieren | Ordner löschen |

Die erzeugte Doku in `docs/arc42/` gehört deinem Projekt und bleibt beim
Entfernen des Skills unberührt.

## Fehlersuche

| Symptom | Ursache und Lösung |
|---|---|
| Der Skill taucht nicht auf. | Der Ordner muss exakt `arc42-docs` heißen und `SKILL.md` direkt enthalten (nicht `arc42-docs/arc42-docs/SKILL.md`). Danach eine neue Session starten; in der Copilot CLI reicht `/skills reload`. |
| Der Agent schreibt Text, aber keine SVGs. | Er hat keinen Terminal-Zugriff oder darf keine Befehle ausführen. Terminal-Tool freigeben bzw. Befehle erlauben. |
| `python3: command not found` | Python installieren oder unter Windows `py -3` nutzen. Der Skill braucht keine Pakete. |
| `No such file …/scripts/render_diagram.py` | Der Agent hat die Scripts im Ziel-Repo statt im Skill-Ordner gesucht. Ihn auf den Skill-Pfad hinweisen (z. B. `.claude/skills/arc42-docs/scripts/`). |
| `self_check.py` meldet `FAIL`. | Gewollt: Der Check findet kollidierende Kanten, zu lange Labels oder zu viele Akzente. Der Agent korrigiert die Spec und rendert neu — siehe [Nutzung](usage.md#diagramme-prüfen). |
| Copilot fragt bei jedem Script nach Erlaubnis. | Für `python3` eine dauerhafte Freigabe erteilen. Die Scripts greifen nicht aufs Netz zu und schreiben nur die Dateien, die ihnen als Ziel übergeben werden. |
