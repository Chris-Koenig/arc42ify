# 11. Risiken und technische Schulden

<!-- status: vollständig — Stand 2026-09-28 -->

Im Code gibt es keine `TODO`/`FIXME`-Kommentare, und auf GitHub sind keine
Issues angelegt. Die folgenden Punkte stammen aus dem Lesen von Code, Tests
und Doku.

## 11.1 Risiken

| ID | Risiko | Auswirkung | Gegenmaßnahme |
|---|---|---|---|
| R1 | **Geschätzte Textbreiten.** Knoten- und Lane-Namen stehen in Proportionalschrift, geschätzt mit 0,6 em je Zeichen ([8.4](08-querschnittliche-konzepte.md#84-geschätzte-textbreiten)). Breite Zeichen (W, M, Großbuchstaben) oder eine andere Systemschrift können breiter sein. | Text ragt über den Boxrand, obwohl `self_check.py` `OK` meldet. | Labels kurz halten; gerenderte SVGs vor dem Merge ansehen. Bei Häufung den Faktor in `sans_width` erhöhen (ändert alle SVGs → neu rendern). |
| R2 | **Agent-Hosts ändern sich schnell.** Skill-Pfade, Plugin-Befehle und Manifest-Formate der drei Hosts sind jung; Copilot hat z. B. `copilot plugin install owner/repo` bereits als veraltet markiert. | Installationsanleitung und `multi-agent-usage.md` stimmen nicht mehr; der Skill wird nicht gefunden. | Alle Pfade und Befehle stehen nur in [docs/installation.md](../installation.md) und [`multi-agent-usage.md`](../../skills/arc42ify/references/multi-agent-usage.md); bei neuen Host-Versionen dort nachziehen. |
| R3 | **Der Agent hält sich nicht an die Anleitung.** Er erfindet Inhalte, überspringt den Selbstcheck oder bearbeitet ein SVG von Hand. | Falsche oder kaputte Doku im Ziel-Repo. | Nicht im Skill lösbar. Im Ziel-Repo den CI-Job aus [docs/usage.md](../usage.md#in-der-ci-prüfen) einrichten (prüft Specs und vergleicht SVGs) und die Doku im Pull Request reviewen. |
| R4 | **Grenzen des Routers.** Ein Knoten in Standardgröße hat 20 Anschlusspunkte; sind sie belegt, bricht das Rendern mit `no free port left` ab. Laufzeit großer Diagramme ist nicht untersucht (Dijkstra auf dem gesamten Gitter je Kante). | Große Diagramme lassen sich nicht rendern oder werden langsam. | Diagramme klein halten (arc42 empfiehlt das ohnehin), bei Bedarf in Ebenen aufteilen. Grenzen messen ([10.3](10-qualitaetsanforderungen.md#103-offene-punkte)). |
| R5 | **Veröffentlichung von Hand.** Nutzer:innen bekommen immer den Stand von `master` auf GitHub. Die Version steht in drei Dateien und wird nicht automatisch erhöht; die Beschreibung in `marketplace.json` wird nicht mit `plugin.json` abgeglichen. | Lokale Änderungen (z. B. eine Umbenennung) erreichen Nutzer:innen erst nach dem Push; Hosts erkennen Updates eventuell nicht ohne neue Versionsnummer. | Vor jedem Push: Version in allen Manifesten erhöhen, Tests laufen lassen. Mittelfristig Git-Tags oder GitHub-Releases. |
| R6 | **Enge Kopplung Renderer ↔ Selbstcheck** ([ADR-005](09-architekturentscheidungen.md#adr-005-selbstcheck-nutzt-die-layout-funktionen-des-renderers)). | Eine Umbenennung oder geänderte Rückgabe in `layout_boxes()` bricht den Check. | Beide Dateien immer gemeinsam ändern; die Tests rufen beide auf und schlagen sofort fehl. |

## 11.2 Technische Schulden

| ID | Schuld | Warum es stört | Vorschlag |
|---|---|---|---|
| TD1 | **Design-Tokens doppelt gepflegt.** `DEFAULT_THEME` in `render_diagram.py` und die Tabelle in `style-guide.md` müssen von Hand übereinstimmen. | Stille Abweichung zwischen Doku und Ergebnis. | Test, der beide vergleicht, oder Tabelle aus dem Code erzeugen. |
| TD2 | **Ungültige Specs führen zu einem Traceback.** `render_diagram.py` validiert nicht; eine fehlende `id` oder `col` endet mit `KeyError`. | Für einen Agenten schwerer zu deuten als eine klare Meldung. | Vor dem Rendern `self_check.check_spec()` aufrufen oder eine knappe Validierung einbauen. |
| TD3 | **macOS fehlt in der CI-Matrix.** Getestet werden Ubuntu und Windows. | Plattformspezifische Fehler auf macOS (z. B. bei Pfaden oder Konsolen) fallen erst bei Nutzer:innen auf. | `macos-latest` in die Matrix aufnehmen. |
