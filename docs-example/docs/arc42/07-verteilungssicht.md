# 7. Verteilungssicht

<!-- status: vollständig -->

## 7.1 Produktion

Alles läuft in einer Azure-Ressourcengruppe in Germany West Central (TR2).
Dasselbe Container-Image startet zweimal: als `web` und als `worker`, nur der
Startbefehl unterscheidet sich.

![Verteilung Produktion: Browser über Front Door zur Web-App; Web-App und Worker nutzen PostgreSQL und Redis; der Worker spricht per HTTPS mit den SaaS-Partnern](assets/diagrams/07-verteilung.svg)

| Knoten | Azure-Dienst | Größe | Aufgabe | ca. €/Monat |
|---|---|---|---|---|
| Front Door | Azure Front Door Standard | — | TLS, Caching statischer Dateien, WAF-Regeln, Rate-Limit für `/webhooks/*` | 35 |
| Web-App | App Service for Containers | P0v3, 2 Instanzen | `uvicorn bohnenwerk.web:app` | 110 |
| Worker | App Service for Containers | P0v3, 1 Instanz | `arq bohnenwerk.worker.Settings` — Outbox-Relay, Cron-Jobs, Partner-Aufrufe | 55 |
| PostgreSQL 16 | Azure Database for PostgreSQL Flexible Server | B2s, 64 GB, Geo-Backup | Einzige Quelle für Shop-Daten | 60 |
| Redis | Azure Cache for Redis | C0 Standard | Job-Queue, Sessions | 40 |
| — | Application Insights, Key Vault | — | Telemetrie, Secrets | 15 |
| | | | **Summe** | **≈ 315** (TR5: ≤ 350) |

Die Web-App ist nur über Front Door erreichbar (Private Link); PostgreSQL und
Redis haben keinen öffentlichen Endpunkt. Webhooks des PSP kommen über Front
Door an die Web-App — der Pfeil fehlt im Bild, er entspricht dem Weg des
Browsers.

## 7.2 Umgebungen

| Umgebung | Wo | Zweck |
|---|---|---|
| lokal | `docker compose up` (web, worker, postgres, redis, Mailpit) | Entwicklung; PSP im Testmodus |
| staging | eigene Ressourcengruppe, kleinste Größen, 1 Instanz je Dienst | Abnahme durch das Team, PSP-Sandbox |
| produktion | wie oben | — |

## 7.3 Auslieferung

GitHub Actions baut bei jedem Merge auf `main` ein Image, taggt es mit dem
Commit-Hash und legt es in der GitHub Container Registry ab. Das Deployment
nach Staging läuft automatisch, nach Produktion per Freigabe. Die Web-App
wechselt per Slot-Swap ohne Ausfall; Alembic-Migrationen laufen vorher als
eigener Schritt und müssen abwärtskompatibel sein (Expand/Contract).
