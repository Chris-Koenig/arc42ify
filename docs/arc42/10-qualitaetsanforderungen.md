# 10. Qualitätsanforderungen

<!-- status: Entwurf — 2 offene Punkte -->

## 10.1 Qualitätsbaum

| Qualitätsziel ([1.2](01-einfuehrung-und-ziele.md#12-qualitätsziele)) | Unterziele | Szenarien |
|---|---|---|
| 1 · Läuft überall | Python 3.8+, Windows-Konsolen, offline | Q1.1–Q1.3 |
| 2 · Reproduzierbar | Byte-gleiche SVGs, auf jedem Betriebssystem | Q2.1–Q2.2 |
| 3 · Lesbare Diagramme | keine Kollisionen, passende Texte, ein Akzent | Q3.1–Q3.3 |
| 4 · Ehrlich über Lücken | offene Kapitel statt erfundener Inhalte | Q4.1 |
| Weitere | Erweiterbarkeit, Erkennbarkeit durch Agenten, Laufzeit | Q5.1–Q5.2, Q6.1, Q7.1 |

## 10.2 Qualitätsszenarien

Jedes Szenario nennt, was es heute absichert. Wo nichts automatisch prüft,
steht das ausdrücklich da.

| ID | Stimulus | Erwartete Reaktion | Abgesichert durch |
|---|---|---|---|
| Q1.1 | Ein Beitrag nutzt Syntax, die es erst ab Python 3.10 gibt (z. B. `match`). | Lokaler Testlauf und CI-Job auf 3.8 schlagen fehl, bevor gemergt wird. | `test_scripts_parse_as_python_3_8`, CI-Job `ubuntu-22.04` / 3.8 |
| Q1.2 | `self_check.py` meldet auf einer Windows-Konsole (cp1252) ein Label mit „→“. | Ausgabe `FAIL …` mit Exit-Code 1, kein Traceback. | `test_failures_exit_1_even_on_a_console_that_cannot_print_the_label` |
| Q1.3 | Der Skill läuft in einer Sandbox ohne Netz. | Alle Scripts laufen; kein SVG enthält eine externe URL. | Nur Standardbibliothek (TR1); `check_svg()` |
| Q2.1 | Ein unveränderter Spec wird unter Windows neu gerendert. | Das SVG ist Byte für Byte identisch mit dem eingecheckten. | `test_committed_svgs_match_a_fresh_render` auf `windows-latest`, `.gitattributes` |
| Q2.2 | Eine Renderer-Änderung verschiebt eine Koordinate. | Der Test schlägt fehl und nennt den Befehl zum Neu-Rendern des betroffenen SVG. | dieselbe Testmethode |
| Q3.1 | Der Agent schreibt ein Kanten-Label mit über 40 Zeichen zwischen zwei Nachbarknoten. | `self_check.py` meldet `FAIL` mit „overlaps node … — shorten it or widen the grid“; der Agent kürzt und rendert neu. | Fixture `boxes-label-too-long.json` |
| Q3.2 | Eine Kante verbindet zwei Knoten, zwischen denen ein dritter steht. | Der Router führt sie rechtwinklig außen herum, mit mindestens 24px Abstand zu jeder fremden Box. | `test_edges_keep_clear_of_other_boxes`, Fixture `boxes-edge-around-box.json` |
| Q3.3 | Eine Spec markiert drei Knoten als `focal`. | `FAIL` mit „3 focal nodes — keep it to 1-2“. | Fixture `boxes-too-many-focal.json` |
| Q4.1 | Das Ziel-Repo hat keine Infrastruktur-Dateien. | Kapitel 7 wird als offen markiert, nicht mit plausiblem Inhalt gefüllt. | **Nur die Anleitung in `SKILL.md`.** **Offen:** Es gibt keinen automatischen Test für das Verhalten des Agenten. |
| Q5.1 | Jemand ergänzt eine neue Prüfregel in `self_check.py`. | Ohne Fail-Fixture und Eintrag in `EXPECTED` gilt die Regel als nicht getestet. | `test_every_fail_fixture_has_an_expectation`, `test_fail_fixtures_are_reported` |
| Q5.2 | Jemand ergänzt eine neue Diagrammart. | Änderung an bekannten Stellen: `render_<kind>` + `RENDERERS`, ggf. `layout_<kind>`, Template, Fixtures, `diagram-spec.md`, `arc42-sections.md`. | Checkliste in [CONTRIBUTING.md](../../CONTRIBUTING.md) — kein Test |
| Q6.1 | Jemand kürzt die `description` und streicht dabei „Bausteinsicht“. | Test schlägt fehl; Agenten würden den Skill bei dieser Bitte sonst seltener laden. | `test_description_keeps_its_trigger_words` |
| Q7.1 | Ein dichtes `boxes`-Diagramm (8 Knoten, 10 Kanten) wird gerendert. | **Offen:** Kein Zielwert festgelegt. Gemessen am 2026-09-28 auf einem Mac (Python 3.14.7): ca. 0,07 s; die gesamte Testsuite (26 Tests) ca. 1,6 s. | — |

## 10.3 Offene Punkte

1. **Verhalten des Agenten prüfen (Q4.1).** Ob ein Agent Lücken markiert
   statt zu erfinden, hängt am Sprachmodell. Denkbar wäre eine kleine
   Evaluierung mit einem Repo ohne Infrastruktur — existiert bisher nicht.
2. **Grenzen für Diagrammgröße und Laufzeit (Q7.1).** Ab wie vielen Knoten
   und Kanten der Router zu langsam wird oder keinen Port mehr findet, ist
   nicht untersucht.
