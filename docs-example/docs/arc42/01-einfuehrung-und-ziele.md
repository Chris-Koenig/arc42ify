# 1. Einführung und Ziele

<!-- status: vollständig -->

## 1.1 Aufgabenstellung

Bohnenwerk ist eine Kaffeerösterei in Leipzig mit 14 Mitarbeitenden. Sie
verkauft Röstkaffee online, heute rund 2.000 Bestellungen und 600 aktive Abos
im Monat. Bisher läuft der Verkauf über eine gemietete Shop-Plattform. Die
kann zwei Dinge nicht, die das Geschäftsmodell trägt:

- **Abos mit freiem Intervall** (alle 2, 4 oder 6 Wochen), die Kund:innen
  selbst pausieren und verschieben.
- **Das Röstfrisch-Versprechen:** Was bis 12:00 bezahlt ist, wird am nächsten
  Werktag geröstet und noch am selben Tag verschickt. Dafür muss der Shop aus
  den Bestellungen einen Röstplan bilden.

Der Bohnenwerk-Shop ersetzt die Plattform. Er umfasst Katalog, Warenkorb,
Checkout, Abos, Bestellabwicklung und die Röstplanung, jeweils für
Kund:innen und für das Backoffice des Teams. Warenwirtschaft und Buchhaltung
bleiben im bestehenden ERP-System.

**Wesentliche Anforderungen**

| ID | Anforderung |
|---|---|
| F1 | Kund:innen kaufen Kaffee als Einzelbestellung oder schließen ein Abo ab. |
| F2 | Kund:innen verwalten ihr Abo selbst: Intervall, Sorte, Pause, Kündigung. |
| F3 | Der Shop bildet werktags um 12:00 den Röstplan für den nächsten Werktag. |
| F4 | Bezahlte Bestellungen gehen nachts als Auftrag ans ERP; Bestände kommen von dort zurück. |
| F5 | Das Team pflegt Sortiment und Preise und sieht Röstplan und Versandliste im Backoffice. |

## 1.2 Qualitätsziele

Die drei wichtigsten Qualitätsziele, nach Priorität. Szenarien dazu stehen in
[Kapitel 10](10-qualitaetsanforderungen.md).

| Prio | Qualitätsziel | Motivation |
|---|---|---|
| 1 | **Zuverlässige Zahlungen** — keine Zahlung geht verloren, keine wird doppelt belastet, nichts wird unbezahlt geröstet. | Jeder Fehler hier kostet Geld und Vertrauen und muss von Hand in ERP und PSP korrigiert werden. |
| 2 | **Termintreue** — jede bis 12:00 bezahlte Bestellung steht im Röstplan des nächsten Werktags. | Das Röstfrisch-Versprechen ist das Verkaufsargument gegenüber dem Supermarkt. |
| 3 | **Betreibbarkeit durch ein Kleinstteam** — zwei Freelancer:innen mit zusammen rund 1,5 Tagen pro Woche können das System betreiben und weiterentwickeln. | Es gibt keine eigene IT und kein Budget für Rufbereitschaft. |

## 1.3 Stakeholder

| Rolle | Erwartung an die Architektur |
|---|---|
| Geschäftsführung | Planbare Betriebskosten, keine Abhängigkeit von einer einzelnen Person, DSGVO-konform. |
| Röstmeister:in | Verlässlicher Röstplan um 12:05, gebündelt nach Sorte und Chargengröße. |
| Versand-Team | Versandlabels ohne Abtippen, Tracking-Mail geht automatisch raus. |
| Kundenservice | Sieht zu jeder Bestellung Zahlstatus, Versandstatus und Mailverlauf an einer Stelle. |
| Entwicklungsteam (2 Freelancer:innen) | Eine Codebasis, ein Deployment, lokal mit `docker compose up` lauffähig. |
| Steuerberatung | Alle Umsätze kommen vollständig und unverändert im ERP an. |
