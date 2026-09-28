# 2. Randbedingungen

<!-- status: vollständig -->

## 2.1 Technische Randbedingungen

| ID | Randbedingung | Hintergrund |
|---|---|---|
| TR1 | Python 3.12 und FastAPI | Beide Entwickler:innen arbeiten seit Jahren damit; eine zweite Sprache ist für das Team nicht tragbar. |
| TR2 | Betrieb in der EU, Azure-Region Germany West Central | DSGVO; die Geschäftsführung will Kundendaten in Deutschland. |
| TR3 | Der Payment Provider (PSP) ist gesetzt | Bestehender Vertrag mit guten Konditionen. Angebunden wird die gehostete Zahlungsseite, der Shop sieht keine Kartendaten. |
| TR4 | Das ERP bleibt führend für Bestand und Buchhaltung | Der ERP-Anbieter erlaubt Massenzugriffe über die REST-API nur zwischen 22:00 und 06:00. |
| TR5 | Cloud-Kosten höchstens 350 € im Monat | Budgetvorgabe der Geschäftsführung, inklusive Staging. |

## 2.2 Organisatorische Randbedingungen

| ID | Randbedingung | Hintergrund |
|---|---|---|
| OR1 | Zwei Freelancer:innen, zusammen ca. 1,5 Personentage pro Woche | Keine eigene IT-Abteilung. |
| OR2 | Code auf GitHub, CI/CD mit GitHub Actions | Vorhandene Konten und Erfahrung. |
| OR3 | Go-live vor dem Weihnachtsgeschäft, spätestens Mitte November | Das Weihnachtsgeschäft macht ein Viertel des Jahresumsatzes aus. |
| OR4 | Keine Rufbereitschaft | Störungen außerhalb der Geschäftszeit dürfen bis zum nächsten Morgen warten, ohne dass Daten verloren gehen. |

## 2.3 Konventionen

- Architekturdoku nach arc42 im Repo unter `docs/arc42/`, Entscheidungen als
  ADR in [Kapitel 9](09-architekturentscheidungen.md).
- Fachbegriffe heißen im Code wie im Glossar, also deutsch (`bestellungen`,
  `roestplanung`, `Charge`). Technische Begriffe bleiben englisch
  (`repository`, `outbox`, `handler`).
- Formatierung und Linting mit `ruff`, Typprüfung mit `mypy --strict` in der CI.
- Datenbankänderungen nur über Alembic-Migrationen, nie von Hand.
