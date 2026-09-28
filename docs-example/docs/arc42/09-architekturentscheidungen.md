# 9. Architekturentscheidungen

<!-- status: vollständig -->

| ADR | Titel | Status |
|---|---|---|
| [ADR-001](#adr-001-modularer-monolith-statt-microservices) | Modularer Monolith statt Microservices | angenommen |
| [ADR-002](#adr-002-server-rendering-mit-htmx-statt-spa) | Server-Rendering mit htmx statt SPA | angenommen |
| [ADR-003](#adr-003-zahlstatus-nur-aus-webhooks) | Zahlstatus nur aus Webhooks | angenommen |
| [ADR-004](#adr-004-transaktionale-outbox-für-folgeaktionen) | Transaktionale Outbox für Folgeaktionen | angenommen |
| [ADR-005](#adr-005-nächtlicher-erp-abgleich-statt-live-abfrage) | Nächtlicher ERP-Abgleich statt Live-Abfrage | angenommen |

---

## ADR-001: Modularer Monolith statt Microservices

**Status:** angenommen · 2026-06-02

**Kontext.** Zwei Freelancer:innen mit zusammen 1,5 Tagen pro Woche (OR1),
kein Betriebsteam, Budget ≤ 350 €/Monat (TR5). Die Fachlichkeit hat klare
Grenzen (Katalog, Bestellungen, Röstplanung …), aber keine Teile, die
unabhängig skalieren müssten.

**Entscheidung.** Eine Codebasis, ein Container-Image, zwei Prozesse (`web`,
`worker`). Bausteine sind Python-Pakete mit öffentlicher `api.py`; ein
Import-Linter in der CI verhindert Querzugriffe.

**Konsequenzen.**
- \+ Ein Deployment, eine Datenbank, lokale Entwicklung mit einem Befehl.
- \+ Transaktionen über Baustein-Grenzen sind möglich, wo nötig (Outbox).
- − Die Modulgrenzen hängen an Disziplin und Linter, nicht an Netzwerkgrenzen.
- − Ein Speicherleck im Worker trifft alle Hintergrundjobs zugleich (siehe R2).

## ADR-002: Server-Rendering mit htmx statt SPA

**Status:** angenommen · 2026-06-02

**Kontext.** Der Shop hat wenige, formularlastige Seiten. Das Team schreibt
Python, kein TypeScript. Eine SPA bräuchte ein zweites Build-System, eine
versionierte JSON-API und doppelte Validierung.

**Entscheidung.** Seiten werden mit Jinja2 auf dem Server gerendert.
Interaktive Teile (Warenkorb, Abo-Pause, „Zahlung wird bestätigt …“) tauschen
mit htmx HTML-Fragmente aus.

**Konsequenzen.**
- \+ Eine Sprache, ein Deployment, Validierung nur im Backend.
- \+ Seiten funktionieren ohne JavaScript im Grundumfang.
- − Offline-Fähigkeit oder eine native App wären später ein eigenes Projekt.

## ADR-003: Zahlstatus nur aus Webhooks

**Status:** angenommen · 2026-06-16

**Kontext.** Nach der Zahlung leitet der PSP den Browser zurück zum Shop.
Dieser Redirect kann ausbleiben (Tab geschlossen, Netz weg) oder gefälscht
werden. Der PSP schickt zusätzlich signierte Webhooks — auch mehrfach und in
beliebiger Reihenfolge.

**Entscheidung.** Nur signierte Webhooks ändern den Zahlstatus. Der Redirect
zeigt lediglich eine Warteseite. Jeder Webhook wird über seine Event-ID genau
einmal verarbeitet. Nach 30 Minuten ohne Webhook fragt ein Job den Status aktiv
ab.

**Konsequenzen.**
- \+ Keine bezahlte Bestellung geht verloren, keine unbezahlte wird geröstet.
- − Die Danke-Seite muss einen Zwischenzustand zeigen („wird bestätigt“).
- − Lokal braucht es einen Tunnel oder die PSP-CLI, um Webhooks zu testen.

## ADR-004: Transaktionale Outbox für Folgeaktionen

**Status:** angenommen · 2026-06-16

**Kontext.** Nach einer Zahlung müssen Mail, ERP-Auftrag und später das
Versandlabel folgen. Direkte Aufrufe im Request würden den Checkout von drei
Partnern abhängig machen; ein Absturz zwischen Commit und Aufruf würde
Folgeaktionen verlieren.

**Entscheidung.** Folgeaktionen werden als Event in der Tabelle `outbox`
gespeichert — in derselben Transaktion wie die Zustandsänderung. Der Worker
überträgt sie in die Redis-Queue und führt sie mit Retry aus
([8.1](08-querschnittliche-konzepte.md#81-transaktionale-outbox)).

**Konsequenzen.**
- \+ Garantiert „mindestens einmal“; Ausfälle von Partnern verzögern nur.
- − Handler müssen idempotent sein ([8.2](08-querschnittliche-konzepte.md#82-idempotenz)).
- − Bis zu 5 Sekunden Verzögerung zwischen Zahlung und Mail.

## ADR-005: Nächtlicher ERP-Abgleich statt Live-Abfrage

**Status:** angenommen · 2026-07-07

**Kontext.** Das ERP ist führend für Bestände (TR4), erlaubt Massenzugriffe
aber nur nachts. Einzelabfragen tagsüber sind auf 60 pro Minute begrenzt —
zu wenig für Katalogseiten unter Last.

**Entscheidung.** Der Shop übernimmt die Bestände einmal pro Nacht und führt
tagsüber einen eigenen, verkaufbaren Bestand, von dem ein Sicherheitsbestand
je Sorte abgezogen ist. Bestellungen gehen nachts gesammelt ans ERP.

**Konsequenzen.**
- \+ Keine Abhängigkeit vom ERP während der Geschäftszeit.
- − Tagsüber kann der Shop-Bestand vom echten Bestand abweichen (R1).
- − Der Sicherheitsbestand bindet Ware, die sonst verkaufbar wäre.
