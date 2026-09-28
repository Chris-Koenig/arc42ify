# 3. Kontextabgrenzung

<!-- status: vollständig -->

## 3.1 Fachlicher Kontext

Der Shop hat zwei Gruppen von Nutzer:innen: Kund:innen, die bestellen und
Abos verwalten, und das Team der Rösterei, das Sortiment, Röstplan und
Versand im Backoffice bearbeitet. Alles, was Geld, Bestand oder Pakete
betrifft, erledigen spezialisierte Partner — der Shop koordiniert sie.

![Fachlicher Kontext: Kund:in und Team Rösterei nutzen den Bohnenwerk-Shop; der Shop spricht mit Payment Provider, Mail-Dienst, ERP-System und Versanddienstleister](assets/diagrams/03-kontext.svg)

| Partner | Was fließt | Warum |
|---|---|---|
| Kund:in | Bestellungen, Abo-Änderungen → Shop; Bestätigungen, Tracking ← Shop | Hauptnutzung |
| Team Rösterei | Sortiment, Preise → Shop; Röstplan, Versandliste ← Shop | Backoffice |
| Payment Provider | Zahlungen, Erstattungen, Abo-Abbuchungen | Kartendaten und SEPA-Mandate liegen nur dort |
| Mail-Dienst | Bestell-, Versand- und Abo-Mails | Zustellbarkeit, SPF/DKIM |
| ERP-System | Aufträge → ERP; Bestände ← ERP | ERP ist führend für Bestand und Buchhaltung (TR4) |
| Versanddienstleister | Sendungsdaten → Label + Trackingnummer | Kein Abtippen im Versand |

## 3.2 Technischer Kontext

| Partner | Richtung | Protokoll / Format | Wann |
|---|---|---|---|
| Browser | eingehend | HTTPS, HTML (server-gerendert, htmx) | laufend |
| Payment Provider | ausgehend | REST/JSON, Idempotency-Key je Bestellung | beim Checkout, bei Abo-Fälligkeit |
| Payment Provider | eingehend | Webhook, HTTPS POST, HMAC-signiert | nach jeder Zahlungsänderung |
| Mail-Dienst | ausgehend | SMTP mit TLS (Port 587) | über die Outbox, siehe [8.1](08-querschnittliche-konzepte.md#81-transaktionale-outbox) |
| ERP-System | ausgehend | REST/JSON, Bulk-Endpunkte | nachts 02:00 (TR4) |
| Versanddienstleister | ausgehend | REST/JSON, Label als PDF | wenn das Team eine Bestellung als „gepackt“ markiert |

Eingehend ist nur HTTPS über Azure Front Door erlaubt; der Webhook des PSP
kommt auf demselben Weg an (`POST /webhooks/psp`). Alle ausgehenden Aufrufe an
Partner laufen im Worker, nie im Request einer Kund:in — fällt ein Partner aus,
bleibt der Shop bedienbar.
