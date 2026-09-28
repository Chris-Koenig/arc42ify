# 11. Risiken und technische Schulden

<!-- status: vollständig -->

## 11.1 Risiken

| ID | Risiko | Auswirkung | Gegenmaßnahme |
|---|---|---|---|
| R1 | Der Bestand wird nur nachts abgeglichen ([ADR-005](09-architekturentscheidungen.md#adr-005-nächtlicher-erp-abgleich-statt-live-abfrage)); tagsüber verkaufen Café und Shop dieselbe Ware. | Überverkauf knapper Sorten, Absagen an Kund:innen. | Sicherheitsbestand je Sorte (Standard 5 kg); das Café bucht Entnahmen im Backoffice. |
| R2 | Nur eine Worker-Instanz. | Fällt sie aus, verzögern sich Mails, Versandlabels und der Cutoff. | App Service startet den Container neu; alle Jobs sind nachholbar; Alarm nach 15 Minuten ohne Outbox-Fortschritt. |
| R3 | Bus-Faktor 2: das Wissen liegt bei zwei Freelancer:innen. | Ausfall oder Wechsel legt die Weiterentwicklung lahm. | Diese Doku, Runbooks im Repo, lokale Umgebung mit einem Befehl. |
| R4 | Der Webhook-Endpunkt ist öffentlich erreichbar. | Gefälschte Zahlungsmeldungen, Last-Angriffe. | HMAC-Prüfung vor jeder Verarbeitung, Rate-Limit an Front Door, Status wird im Zweifel beim PSP gegengeprüft. |
| R5 | Das Weihnachtsgeschäft bringt die dreifache Last des Normalbetriebs. | Langsame Seiten zur umsatzstärksten Zeit. | Lasttest vor dem 15.11. (siehe TD2); Web-App kann per Regel auf 4 Instanzen skalieren. |

## 11.2 Technische Schulden

| ID | Schuld | Warum eingegangen | Abbau |
|---|---|---|---|
| TD1 | Die Röstplanung kennt den Rohkaffee-Bestand nicht und warnt nicht, wenn eine Charge nicht gedeckt ist. | Go-live-Termin (OR3). | Q1/2027: Rohkaffee-Bestand aus dem ERP-Abgleich in die Röstplanung übernehmen. |
| TD2 | Lasttests laufen nicht automatisiert, sondern von Hand mit `locust`. | Aufwand für eine stabile Testumgebung. | Vor jedem Weihnachtsgeschäft manuell; Automatisierung offen. |
| TD3 | Mail-Texte liegen als Templates im Code; das Team kann sie nicht selbst ändern. | Einfachste Lösung für den Start. | Texte ins Backoffice verlagern, sobald Änderungen häufiger als monatlich anfallen. |
