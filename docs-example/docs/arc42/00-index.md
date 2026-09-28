# arc42-Dokumentation — Bohnenwerk-Shop

> **Fiktives Beispiel.** Die Rösterei Bohnenwerk, ihr Shop und alle Zahlen
> sind erfunden. Diese Dokumentation zeigt, wie eine mit dem
> `arc42ify`-Skill erzeugte Doku aussieht: 12 Kapitel, Diagramme nur dort,
> wo sie mehr sagen als ein Satz.

Diese Dokumentation folgt [arc42](https://arc42.de/). Diagramme liegen als
SVG unter `assets/diagrams/` und werden aus den `*.diagram.json`-Specs im
selben Ordner erzeugt:

```bash
python3 scripts/render_diagram.py assets/diagrams/<name>.diagram.json assets/diagrams/<name>.svg
python3 scripts/self_check.py     assets/diagrams/<name>.diagram.json assets/diagrams/<name>.svg
```

## Kapitel

| Kapitel | Status | Diagramme |
|---|---|---|
| [1. Einführung und Ziele](01-einfuehrung-und-ziele.md) | vollständig | — |
| [2. Randbedingungen](02-randbedingungen.md) | vollständig | — |
| [3. Kontextabgrenzung](03-kontextabgrenzung.md) | vollständig | Kontextdiagramm |
| [4. Lösungsstrategie](04-loesungsstrategie.md) | vollständig | — |
| [5. Bausteinsicht](05-bausteinsicht.md) | vollständig | Ebene 1, Whitebox Bestellungen |
| [6. Laufzeitsicht](06-laufzeitsicht.md) | vollständig | Checkout, Röstplan-Cutoff |
| [7. Verteilungssicht](07-verteilungssicht.md) | vollständig | Produktion |
| [8. Querschnittliche Konzepte](08-querschnittliche-konzepte.md) | vollständig | Schichtenmodell |
| [9. Architekturentscheidungen](09-architekturentscheidungen.md) | vollständig | — |
| [10. Qualitätsanforderungen](10-qualitaetsanforderungen.md) | Entwurf — 1 offener Punkt | — |
| [11. Risiken und technische Schulden](11-risiken-und-technische-schulden.md) | vollständig | — |
| [12. Glossar](12-glossar.md) | vollständig | — |

## Auf einen Blick

![Fachlicher Kontext: Kund:innen und Team nutzen den Bohnenwerk-Shop, der mit Payment Provider, Mail-Dienst, ERP und Versanddienstleister spricht](assets/diagrams/03-kontext.svg)
