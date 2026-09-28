# 4. Lösungsstrategie

<!-- status: vollständig -->

Die Strategie folgt aus den drei Qualitätszielen und dem kleinen Team. Das
Grundmuster: **so wenige bewegliche Teile wie möglich, aber jede Wirkung nach
außen entkoppelt und wiederholbar.**

| Qualitätsziel | Ansatz | Details |
|---|---|---|
| Betreibbarkeit (3) | **Modularer Monolith** in einer Codebasis, als zwei Prozesse deployt: `web` (Requests) und `worker` (Hintergrundjobs). | [ADR-001](09-architekturentscheidungen.md#adr-001-modularer-monolith-statt-microservices), [Kap. 5](05-bausteinsicht.md) |
| Betreibbarkeit (3) | **Server-Rendering mit Jinja und htmx** statt Single-Page-App — kein zweites Build-System, kein API-Versioning zwischen Frontend und Backend. | [ADR-002](09-architekturentscheidungen.md#adr-002-server-rendering-mit-htmx-statt-spa) |
| Zuverlässige Zahlungen (1) | **Gehostete Zahlungsseite des PSP**; der Zahlstatus wird ausschließlich aus signierten Webhooks gesetzt, nie aus dem Redirect des Browsers. | [ADR-003](09-architekturentscheidungen.md#adr-003-zahlstatus-nur-aus-webhooks), [6.1](06-laufzeitsicht.md#61-checkout-mit-zahlung) |
| Zuverlässige Zahlungen (1) | **Transaktionale Outbox:** Folgeaktionen (Mail, ERP, Versand) werden in derselben DB-Transaktion wie die Zustandsänderung gespeichert und vom Worker mit Retry abgearbeitet. | [ADR-004](09-architekturentscheidungen.md#adr-004-transaktionale-outbox-für-folgeaktionen), [8.1](08-querschnittliche-konzepte.md#81-transaktionale-outbox) |
| Termintreue (2) | **Röstplanung als eigener Baustein** mit festem Cutoff um 12:00; der Cutoff-Job ist idempotent und kann nachgeholt werden. | [5.1](05-bausteinsicht.md), [6.2](06-laufzeitsicht.md#62-röstplan-zum-cutoff) |
| Termintreue (2) | **ERP bleibt führend** für Bestände; der Shop gleicht nachts ab und hält tagsüber einen Sicherheitsbestand zurück. | [ADR-005](09-architekturentscheidungen.md#adr-005-nächtlicher-erp-abgleich-statt-live-abfrage), [R1](11-risiken-und-technische-schulden.md) |

**Technologie im Überblick:** Python 3.12, FastAPI, Jinja2, htmx,
SQLAlchemy 2, Alembic, PostgreSQL 16, Redis als Job-Queue (`arq`), Betrieb als
Container in Azure App Service.
