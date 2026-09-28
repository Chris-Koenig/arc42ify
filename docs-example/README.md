# Beispiel: Bohnenwerk-Shop

> **Fiktiv.** Die Rösterei Bohnenwerk, ihr Shop, alle Zahlen und Entscheidungen
> sind für dieses Beispiel erfunden.

So sieht eine Architekturdoku aus, die mit dem `arc42-docs`-Skill entsteht.
Der Ordner hat dieselbe Struktur, die der Skill in deinem Repo anlegt:
`docs/arc42/` mit 13 Markdown-Dateien und `assets/diagrams/` mit je einer
`.diagram.json` (Quelle) und einem `.svg` (erzeugt).

**[→ Zur Doku](docs/arc42/00-index.md)**

## Was das Beispiel zeigt

| Kapitel | Achte auf |
|---|---|
| [1 Einführung](docs/arc42/01-einfuehrung-und-ziele.md) | Drei priorisierte Qualitätsziele mit Motivation — sie tragen alle späteren Entscheidungen. |
| [3 Kontext](docs/arc42/03-kontextabgrenzung.md) | Diagramm für den fachlichen Kontext, Tabelle für die technischen Details. |
| [5 Bausteine](docs/arc42/05-bausteinsicht.md) | Ebene 1 plus eine Whitebox (Ebene 2) nur für den Baustein, an dem das wichtigste Qualitätsziel hängt. |
| [6 Laufzeit](docs/arc42/06-laufzeitsicht.md) | Zwei Abläufe mit Sequenzdiagramm, ein dritter bewusst nur als Liste. |
| [7 Verteilung](docs/arc42/07-verteilungssicht.md) | Gruppe als Cloud-Grenze, Kosten gegen die Budget-Randbedingung gerechnet. |
| [8 Konzepte](docs/arc42/08-querschnittliche-konzepte.md) | Schichtenmodell als Überblick, danach Text und ein kurzes Codebeispiel. |
| [9 Entscheidungen](docs/arc42/09-architekturentscheidungen.md) | Fünf ADRs mit Kontext, Entscheidung und Konsequenzen (+/−). |
| [10 Qualität](docs/arc42/10-qualitaetsanforderungen.md) | Ein Wert ist **offen** markiert statt erfunden — so geht der Skill mit fehlender Information um. |

Kapitel 1, 2, 4, 9, 10, 11 und 12 kommen ohne Diagramm aus: Dort sagt eine
Tabelle mehr als ein Bild.

## Diagramme neu erzeugen

Aus dem Root dieses Repos:

```bash
for spec in docs-example/docs/arc42/assets/diagrams/*.diagram.json; do
  svg="${spec%.diagram.json}.svg"
  python3 skills/arc42-docs/scripts/render_diagram.py "$spec" "$svg"
  python3 skills/arc42-docs/scripts/self_check.py "$spec" "$svg"
done
```
