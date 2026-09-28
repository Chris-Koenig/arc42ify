# 10. Qualitätsanforderungen

<!-- status: Entwurf — 1 offener Punkt (10.2, Q8) -->

## 10.1 Qualitätsbaum

| Qualitätsmerkmal | Verfeinerung | Szenarien |
|---|---|---|
| **Zuverlässigkeit** (Ziel 1) | Korrektheit der Zahlungen | Q1, Q2 |
| | Fehlertoleranz gegenüber Partnern | Q3 |
| **Termintreue** (Ziel 2) | Vollständiger Röstplan | Q4, Q5 |
| **Betreibbarkeit** (Ziel 3) | Deployment ohne Ausfall | Q6 |
| | Nachvollziehbarkeit von Fehlern | Q7 |
| **Verfügbarkeit** | Erreichbarkeit des Shops | Q8 |
| **Effizienz** | Antwortzeit unter Last | Q9 |

## 10.2 Qualitätsszenarien

| ID | Situation (Stimulus) | Erwartete Reaktion | Messgröße |
|---|---|---|---|
| Q1 | Der PSP schickt denselben Webhook dreimal. | Die Bestellung wechselt genau einmal auf `bezahlt`, es geht genau eine Mail raus. | 0 Duplikate in `outbox` je Bestellung und Event-Typ |
| Q2 | Die Kund:in schließt den Tab direkt nach der Zahlung. | Die Bestellung wird trotzdem bezahlt und eingeplant, weil der Webhook ankommt. | 100 % der beim PSP bezahlten Bestellungen sind im Shop `bezahlt` (täglicher Abgleich) |
| Q3 | Der Mail-Dienst ist 2 Stunden nicht erreichbar. | Checkout funktioniert weiter; alle Mails gehen nach Wiederherstellung raus. | 0 verlorene Mails, Checkout-Fehlerrate unverändert |
| Q4 | Eine Bestellung wird um 11:59:30 bezahlt. | Sie steht im Röstplan des nächsten Werktags. | Stichtag laut PSP-Zeitstempel, nicht Eingang des Webhooks |
| Q5 | Der Worker ist um 12:00 gerade im Neustart. | Der Cutoff läuft beim Start nach, der Röstplan steht bis 12:10. | Alarm, wenn um 12:10 kein Röstplan existiert |
| Q6 | Ein Release geht um 10:30 an einem Werktag live. | Kund:innen bemerken nichts. | 0 HTTP-5xx während des Slot-Swaps |
| Q7 | Eine Kund:in meldet: „Ich habe keine Bestellmail bekommen.“ | Der Kundenservice findet über die Bestellnummer den Mail-Job und seinen Status. | < 5 Minuten bis zur Ursache |
| Q8 | Die Web-App ist außerhalb eines Deployments nicht erreichbar. | Front Door liefert eine Wartungsseite; der Alarm geht an das Team. | <!-- TODO: Verfügbarkeitsziel mit der Geschäftsführung klären (Vorschlag: 99,5 % pro Monat) --> _offen_ |
| Q9 | Black Friday: 20 Bestellungen pro Minute über eine Stunde. | Seiten bleiben flüssig bedienbar. | p95 Antwortzeit < 800 ms für Katalog und Checkout |

Q8 ist absichtlich offen: Ein Verfügbarkeitsziel ist eine geschäftliche
Entscheidung und steht noch aus. Die Doku markiert das, statt eine Zahl zu
erfinden.
