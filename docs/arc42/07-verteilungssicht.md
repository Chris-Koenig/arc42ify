# 7. Verteilungssicht

<!-- status: vollständig -->

`arc42ify` hat keinen Server, keinen Container und keine Datenbank. „Deployen“
heißt hier: Der Skill-Ordner kommt vom GitHub-Repo auf den Rechner (oder in
den Cloud-Agenten) der Nutzer:in, und der Agent-Host startet dort die Scripts
mit dem lokalen Python.

## 7.1 Infrastruktur

![Verteilung: Das arc42ify-Repo auf GitHub löst bei Push und Pull Request GitHub Actions aus; Nutzer:innen installieren den Skill entweder als Plugin oder als kopierten Ordner; der Agent-Host lädt eine der Kopien und startet die Scripts mit dem lokalen Python, das ins Ziel-Repo schreibt](assets/diagrams/07-verteilung.svg)

| Knoten | Was dort liegt oder läuft | Anforderungen |
|---|---|---|
| **arc42ify-Repo** (`github.com/Chris-Koenig/arc42ify`, Branch `master`) | Quelle für alle Installationen; zugleich Plugin-Marketplace. | Was nicht gepusht ist, erreicht niemanden — Plugin-Installationen lesen den Stand auf GitHub. |
| **GitHub Actions** | Test-Matrix aus [6.5](06-laufzeitsicht.md#65-ci-lauf-in-diesem-repo). | Nur `contents: read`. |
| **Plugin-Install** | Kopie des Repos im Plugin-Cache des Hosts, installiert über den Marketplace. | Host mit Plugin-Unterstützung (Claude Code, Copilot CLI, Codex CLI). |
| **Ordner-Kopie** | `skills/arc42ify/` von Hand kopiert — persönlich (`~/.claude/skills/`, `~/.copilot/skills/`, `~/.agents/skills/`) oder im Ziel-Repo (`.claude/skills/`, `.github/skills/`, `.agents/skills/`). | Ordner muss exakt `arc42ify` heißen und `SKILL.md` direkt enthalten. |
| **Agent-Host** | Claude Code, GitHub Copilot (CLI, VS Code, Cloud-Agent) oder OpenAI Codex (CLI, IDE). | Terminal-Zugriff — ohne Shell entsteht nur Text, keine SVGs. |
| **Python ≥ 3.8** | Führt `scaffold.py`, `render_diagram.py`, `self_check.py` aus. | `python3`, `python` oder `py -3`; keine Pakete, kein Netz. |
| **Ziel-Repo** | Bekommt `docs/arc42/`. | Schreibrechte im Arbeitsverzeichnis. |

## 7.2 Installationswege je Host

| Host | Plugin | Persönlich | Im Ziel-Repo | Aufruf |
|---|---|---|---|---|
| Claude Code | `/plugin marketplace add Chris-Koenig/arc42ify`, dann `/plugin install arc42ify@arc42ify` | `~/.claude/skills/arc42ify/` | `.claude/skills/arc42ify/` | `/arc42ify` bzw. `/arc42ify:arc42ify` |
| GitHub Copilot | `copilot plugin marketplace add …`, dann `copilot plugin install arc42ify@arc42ify` | `~/.copilot/skills/` oder `~/.agents/skills/` | `.github/skills/`, `.claude/skills/` oder `.agents/skills/` | `/arc42ify` |
| OpenAI Codex | `codex plugin marketplace add …`, dann `codex plugin add arc42ify@arc42ify` | `~/.agents/skills/arc42ify/` | `.agents/skills/arc42ify/` | `$arc42ify` |

Für Teams mit gemischten Agenten: den Ordner einmal nach `.claude/skills/`
legen und `.agents/skills/arc42ify` als Symlink darauf zeigen lassen. Die
vollständige Anleitung inklusive Fehlersuche steht in
[docs/installation.md](../installation.md).

## 7.3 Versionen und Releases

- Die Version steht von Hand in drei Dateien:
  `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` und
  `.codex-plugin/plugin.json` (derzeit `1.0.0`). Die Tests sichern, dass sie
  gleich sind — nicht, dass sie erhöht wurde.
- Es gibt keine Git-Tags und keine GitHub-Releases. Nutzer:innen bekommen
  immer den aktuellen Stand von `master`.
- Ein umbenannter Plugin-Name wird von bestehenden Installationen **nicht**
  übernommen: Wer `arc42-docs@arc42ify` installiert hatte, muss es
  entfernen und `arc42ify@arc42ify` neu installieren
  ([ADR-006](09-architekturentscheidungen.md#adr-006-ein-name-und-ein-skill-ordner-für-alle-hosts)).
