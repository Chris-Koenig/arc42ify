# 12. Glossar

<!-- status: vollständig -->

| Begriff | Bedeutung |
|---|---|
| **Abo** | Vertrag über wiederkehrende Lieferung einer Sorte im Intervall von 2, 4 oder 6 Wochen. Erzeugt zu jedem Fälligkeitstag eine Bestellung. |
| **Bestellposten** (kurz Posten) | Eine Zeile einer Bestellung: Sorte, Röstgrad, Mahlgrad, Menge. Die Röstplanung arbeitet auf Posten, nicht auf Bestellungen. |
| **Charge** | Eine Röstung in der Trommel: eine Sorte, ein Röstgrad, höchstens 15 kg Rohkaffee. |
| **Cutoff** | Werktäglich 12:00 (Europe/Berlin). Was bis dahin bezahlt ist, kommt in den Röstplan des nächsten Werktags. |
| **Dead-Letter** | Tabelle für Outbox-Jobs, die nach 8 Versuchen gescheitert sind. Werden von Hand geprüft und neu angestoßen. |
| **Gehostete Zahlungsseite** | Zahlungsseite, die der PSP betreibt. Der Shop leitet dorthin um und sieht keine Kartendaten. |
| **Idempotency-Key** | Schlüssel, den der Shop bei einem Aufruf mitschickt, damit der Empfänger eine Wiederholung als solche erkennt. Beim PSP: die Bestell-ID. |
| **Outbox** | Tabelle, in die eine Zustandsänderung ihre Folgeaktionen in derselben Transaktion schreibt. Der Worker arbeitet sie ab. |
| **PSP** | Payment Service Provider — der Zahlungsdienstleister. |
| **Rohkaffee / Röstkaffee** | Ungerösteter bzw. gerösteter Kaffee. Beim Rösten gehen ca. 16 % des Gewichts verloren (Röstverlust). |
| **Röstfrisch-Versprechen** | Zusage an Kund:innen: bis 12:00 bezahlt, am nächsten Werktag geröstet und verschickt. |
| **Röstplan** | Liste der Chargen eines Tages mit zugeordneten Posten. Entsteht zum Cutoff. |
| **Sicherheitsbestand** | Menge je Sorte, die der Shop nicht verkauft, um Abweichungen zum ERP-Bestand abzufedern. |
| **Webhook** | HTTP-Aufruf, mit dem der PSP den Shop über eine Zahlungsänderung informiert. |
| **Worker** | Zweiter Prozess neben der Web-App: Outbox-Relay, Cron-Jobs, alle Aufrufe an Partner. |
