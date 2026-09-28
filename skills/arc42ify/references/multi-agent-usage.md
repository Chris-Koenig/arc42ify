# Installation und Aufruf je Host

Der Skill ist eine reine Dateisammlung nach dem offenen
[Agent-Skills-Format](https://agentskills.io/specification): `SKILL.md` mit
`name` + `description`, dazu Markdown-Referenzen und Python-Scripts ohne
Fremdabhängigkeiten. Jeder Host, der dieses Format liest, kann ihn nutzen.
Unterschiedlich ist nur, **in welchem Ordner** der Host nach Skills sucht.

Die ausführliche Anleitung für Menschen steht im Skill-Repo unter
`docs/installation.md`. Diese Datei ist die Kurzfassung für den Agenten.

## Wo jeder Host sucht

| Host | Projekt (im Repo) | Persönlich (alle Repos) | Aufruf |
|---|---|---|---|
| Claude Code | `.claude/skills/arc42ify/` | `~/.claude/skills/arc42ify/` | automatisch oder `/arc42ify` (als Plugin: `/arc42ify:arc42ify`) |
| GitHub Copilot (CLI, VS Code, Cloud-Agent) | `.github/skills/`, `.claude/skills/` oder `.agents/skills/` | `~/.copilot/skills/` oder `~/.agents/skills/` | automatisch oder `/arc42ify` |
| OpenAI Codex (CLI, IDE-Extension) | `.agents/skills/arc42ify/` | `~/.agents/skills/arc42ify/` | automatisch oder `$arc42ify`; `/skills` listet alle |

Kein Host braucht dafür eine Einstellung oder ein Feature-Flag.

## Ein Repo für alle drei Hosts

Den Skill-Ordner **einmal** echt ins Repo legen und für Codex verlinken:

```bash
mkdir -p .claude/skills .agents/skills
cp -R /pfad/zu/arc42ify/skills/arc42ify .claude/skills/arc42ify
ln -s ../../.claude/skills/arc42ify .agents/skills/arc42ify
```

- Claude Code und Copilot lesen `.claude/skills/` direkt.
- Codex liest `.agents/skills/` und folgt dem Symlink.
- Copilot findet den Skill an beiden Stellen, listet ihn aber nur einmal.

Unter Windows ohne Symlink-Unterstützung (`git config core.symlinks false`)
statt des Symlinks eine zweite Kopie nach `.agents/skills/arc42ify` legen.

## Als Plugin (Claude Code, Copilot CLI, Codex)

Das Skill-Repo ist zugleich Plugin und Marketplace (`.claude-plugin/` für
Claude Code und Copilot, `.codex-plugin/` + `.agents/plugins/` für Codex —
alle installieren denselben Ordner `skills/arc42ify/`):

```bash
# Claude Code (in der Session) — oder als Shell-Befehl: claude plugin …
/plugin marketplace add Chris-Koenig/arc42ify
/plugin install arc42ify@arc42ify

# GitHub Copilot CLI
copilot plugin marketplace add Chris-Koenig/arc42ify
copilot plugin install arc42ify@arc42ify

# OpenAI Codex CLI
codex plugin marketplace add Chris-Koenig/arc42ify
codex plugin add arc42ify@arc42ify
```

## Voraussetzungen für die Diagramme

- Der Agent braucht Terminal-/Shell-Zugriff, um die Scripts auszuführen.
  Ohne Shell entstehen nur die Texte, keine SVGs.
- Python 3.8 oder neuer (`python3`, `python` oder `py -3`). Keine Pakete,
  kein Netzwerk.
- Die Scripts liegen im Skill-Ordner, nicht im Ziel-Repo — siehe
  „Skript-Pfade“ in `SKILL.md`.

## Ohne Agent (CI, Handbetrieb)

```bash
python3 scripts/scaffold.py /pfad/zum/repo --lang de
python3 scripts/render_diagram.py spec.diagram.json diagramm.svg
python3 scripts/self_check.py spec.diagram.json diagramm.svg   # Exit-Code 1 bei Problemen
```

`self_check.py` taugt als CI-Gate: Es schlägt fehl, sobald eine Spec
ungültig ist oder Kanten und Labels kollidieren.
