# arc42-Kapitel: Inhalt, Quellen, Diagrammtyp

Für jedes Kapitel: was hineingehört, wo der Agent die Information im Repo /
in der Idee findet, und welcher Diagrammtyp (falls einer) es visuell trägt.
Nicht jedes Kapitel braucht ein Bild — Kapitel 1, 2, 9, 10, 12 sind meist
reiner Text/Tabellen. Erzwinge kein Diagramm, wo ein Absatz reicht.

| # | Kapitel | Inhalt | Quelle im Repo | Diagrammtyp |
|---|---|---|---|---|
| 1 | Einführung und Ziele | Aufgabenstellung, Top-3–5 Qualitätsziele, Stakeholder | README, Issues/Tickets, Gespräch mit Nutzer | — (Tabelle: Stakeholder × Erwartung; Tabelle: Qualitätsziel × Motivation) |
| 2 | Randbedingungen | Technische Vorgaben (Sprache, Cloud, Compliance), organisatorische Vorgaben | `pyproject.toml`/`package.json`/CI-Config, README, Lizenzdatei | — (Tabelle) |
| 3 | Kontextabgrenzung | Fachlicher + technischer Kontext: wer/was kommuniziert mit dem System, worüber | Entry-Points, API-Clients, `.env.example`, Integrationscode (HTTP-Clients, SDKs, Webhooks) | `boxes` — **Kontextdiagramm** (1 fokaler Knoten = System, außen die Nachbarsysteme/Akteure) |
| 4 | Lösungsstrategie | Grundlegende Technologie- und Architekturentscheidungen, Begründung | Framework-Wahl im Code, ADRs falls vorhanden, Dependency-Liste | optional `layers` als Kurzüberblick |
| 5 | Bausteinsicht | Statische Zerlegung: Whitebox Ebene 1 (Module/Services), ggf. Ebene 2 (Komponenten je Modul) | Ordnerstruktur, Modulgrenzen, Import-Graph, `src/`-Layout | `boxes` — **Bausteindiagramm** (Gruppen = Systemgrenze, fokal = Einstiegspunkt) |
| 6 | Laufzeitsicht | 2–4 wichtige Abläufe (Request-Flow, Fehlerfall, Batch-Job) als Szenario | Controller/Handler-Code, Tests (zeigen erwarteten Ablauf!), Logs | `sequence` — **Sequenzdiagramm** pro Szenario |
| 7 | Verteilungssicht | Infrastruktur: Hosts, Container, Netzwerksegmente, Mapping Bausteine → Infrastruktur | `docker-compose.yml`, Terraform/Bicep/CloudFormation, CI/CD-Deploy-Config, k8s-Manifeste | `boxes` — **Verteilungsdiagramm** (Gruppe = Netzwerk-/Cloud-Grenze) |
| 8 | Querschnittliche Konzepte | Auth, Logging, Error-Handling, i18n, Persistenzmuster, geteilte Libraries | Middleware-Code, gemeinsame Utils, Security-Config | `layers` — **Schichtenmodell**, fokale Schicht = das gerade erklärte Konzept |
| 9 | Architekturentscheidungen | Wichtige Entscheidungen im ADR-Format (Kontext, Entscheidung, Konsequenzen) | Git-History, bestehende ADRs, Kommentare im Code | — (strukturierte Liste, ein Block pro Entscheidung) |
| 10 | Qualitätsanforderungen | Qualitätsbaum + konkrete Szenarien (Stimulus → Reaktion) je Qualitätsziel aus Kap. 1 | Tests (Performance-/Last-Tests zeigen reale Ziele), NFR-Tickets | optional `layers` als Qualitätsbaum-Ersatz, sonst Tabelle |
| 11 | Risiken und technische Schulden | Bekannte Risiken, TODO/FIXME, veraltete Dependencies, Single Points of Failure | `TODO`/`FIXME`-Grep, `npm audit`/`pip-audit`, offene Issues mit Label „tech-debt" | — (Tabelle: Risiko × Auswirkung × Gegenmaßnahme) |
| 12 | Glossar | Fachbegriffe und Akronyme, konsistent verwendet | Domänen-Code (Klassennamen, Variablennamen), README | — (Tabelle Begriff × Definition) |

## Faustregel für die Diagrammauswahl

1. Kapitel 3, 5, 7 → immer `boxes` (Kontext/Bausteine/Verteilung sind strukturell fast identisch: Knoten + Kanten + optionale Gruppen-Grenze).
2. Kapitel 6 → immer `sequence`, ein Diagramm pro Szenario, nicht eines für alles.
3. Kapitel 8 → `layers`, wenn es um geschichtete Verantwortlichkeiten geht (z. B. Presentation/API/Domain/Persistence). Für Querschnittsthemen ohne Schichtung (z. B. „wie Logging funktioniert") reicht ein kurzer Text + Codebeispiel.
4. Alle anderen Kapitel: kein generiertes Diagramm. Ein Diagramm, das nichts zeigt, was der Fließtext nicht auch in einem Satz sagt, wird weggelassen (gleiche Regel wie im Referenz-Repo `diagram-design`).
