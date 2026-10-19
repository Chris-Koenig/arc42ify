# Bausteinsicht: Ebenen, Komponenten, Schnittstellen

Lesen, bevor Kapitel 5 geschrieben wird. Kapitel 5 ist die Stelle, an der
Entwickler:innen nachschlagen, *wie man einen Baustein benutzt* — deshalb
sind hier die Schnittstellen genauso wichtig wie die Kästen.

## Ebenen festlegen

arc42 zerlegt rekursiv: Jede Ebene ist die Whitebox eines Bausteins der
Ebene darüber. Viele Teams denken in C4-Ebenen; so passen beide zusammen:

| C4 | arc42 | Was beschrieben wird | Beispiel |
|---|---|---|---|
| Level 1 · System Context | Kapitel 3 | Das System als Blackbox, Nutzer:innen, Nachbarsysteme | Shop ↔ PSP, ERP |
| Level 2 · Container | 5.1 Whitebox Gesamtsystem (Ebene 1) | Die Softwaresysteme bzw. einzeln lauffähigen Teile: Apps, Services, Worker, Datenbanken — bei einem modularen Monolithen dessen Fachmodule | Web-App, Worker, PostgreSQL |
| **Level 3 · Component** | **5.2 ff. Whitebox je Baustein (Ebene 2)** | **Die Komponenten eines Softwaresystems: Bestandteile mit eigener Verantwortung und eigener Schnittstelle** | Bestell-Service, Outbox, Zahlungsabgleich |
| Level 4 · Code | Ebene 3, nur wenn nötig | Klassen/Funktionen einer einzelnen Komponente | — meist besser im Code selbst |

Die arc42-Nummer hängt vom Zuschnitt ab (eine Systemlandschaft hat eine
Ebene mehr als ein einzelner Service). Entscheidend ist nicht die Nummer,
sondern: **Auf der Komponentenebene bekommt jede Komponente eine Blackbox
mit vollständig beschriebenen Schnittstellen.** Steht die Zuordnung im Text,
nenne sie einmal am Anfang von Kapitel 5 („Ebene 2 entspricht C4 Level 3“).

Wie tief zerlegen:

- Ebene 1 immer vollständig.
- Ebene 2 (Komponenten) für jeden Baustein, an dem ein Top-Qualitätsziel
  aus Kapitel 1 hängt, der fachlich komplex ist oder den andere Teams
  nutzen. Nicht für triviale Bausteine („CRUD auf eine Tabelle“) — dort
  reicht die Zeile in der Ebene-1-Tabelle.
- Ebene 3 nur für eine Komponente, deren innere Struktur selbst eine
  Architekturentscheidung ist (z. B. Zustandsautomat, Plugin-Mechanismus).

## Whitebox-Vorlage (je zerlegtem Baustein)

```markdown
## 5.2 Whitebox <Baustein> (Ebene 2)

<1–3 Sätze: Warum dieser Baustein zerlegt wird, nach welchem Prinzip
(fachlich, technisch, nach Änderungsrate …).>

![<Alt-Text: welche Komponenten, wer nutzt wen über welche Schnittstelle>](assets/diagrams/05-<baustein>-ebene2.svg)

| Komponente | Verantwortung | Bietet an | Nutzt |
|---|---|---|---|
| **<Name>** (`<pfad>`) | <ein Satz> | IF-… | IF-… |

### <Komponente> (Blackbox)
…eine Blackbox je Komponente, siehe unten…
```

## Blackbox-Vorlage (je Komponente)

```markdown
### <Komponente>

**Zweck.** <Wofür es sie gibt, in einem Satz — nicht wie sie es tut.>

**Ablage.** `<pfad/zum/modul/>` · <Sprache/Framework, falls abweichend>

**Bietet an:** [IF-03](#if-03-…), [IF-04](#if-04-…)
**Nutzt:** [IF-07](#if-07-…), PostgreSQL-Tabelle `bestellung`

**Qualitäts-/Leistungsmerkmale.** <nur was belegt ist: Durchsatz, Latenz,
Idempotenz, Transaktionsverhalten; sonst „offen“>

**Offene Punkte.** <Risiken, bekannte Schwächen, Verweis auf Kapitel 11>
```

## Schnittstellen beschreiben

Jede Schnittstelle, die eine Komponente nach außen anbietet, bekommt eine
**ID** (`IF-01`, `IF-02` … fortlaufend über das ganze Kapitel) und einen
**Steckbrief**. Die Blackboxes und das Diagramm verweisen nur auf die ID —
so steht jede Schnittstelle genau einmal in der Doku.

### Schnittstellenübersicht (eigener Abschnitt am Ende von Kapitel 5)

```markdown
## 5.n Schnittstellen

| ID | Name | Anbieter | Nutzer | Art | Vertrag |
|---|---|---|---|---|---|
| IF-01 | Bestell-API | Bestell-Service | Checkout, Abos | Funktionsaufruf, synchron | `bestellungen/api.py` |
```

### Steckbrief (je Schnittstelle)

```markdown
### IF-01: <Name>

| | |
|---|---|
| **Anbieter → Nutzer** | <Komponente> → <Komponenten/Systeme> |
| **Art** | synchroner Aufruf · REST · gRPC · Event/Queue · Datei · gemeinsame Tabelle |
| **Protokoll / Format** | <z. B. HTTPS + JSON, AMQP + Avro, Python-Aufruf in-process> |
| **Vertrag** | <Link auf OpenAPI/AsyncAPI/.proto/JSON-Schema/öffentliches Modul> |
| **Operationen / Events** | <die 3–7 wichtigsten, mit Kurzbeschreibung — Rest steht im Vertrag> |
| **Fehlerverhalten** | <Fehlercodes/Exceptions, was Nutzer:innen tun sollen; Timeouts, Retries> |
| **Garantien** | <Idempotenz, Reihenfolge, Zustellung (at-least-once …), Transaktionsgrenze> |
| **Sicherheit** | <AuthN/AuthZ, Signatur, Netzgrenze — nur wenn relevant> |
| **Version / Stabilität** | <Versionierung, Kompatibilitätsregel, „intern, darf brechen“> |
```

Regeln:

- **Vertrag verlinken, nicht abschreiben.** Gibt es eine OpenAPI-, AsyncAPI-,
  `.proto`- oder Schema-Datei, ist sie die Wahrheit; der Steckbrief fasst
  zusammen und erklärt das, was im Vertrag *nicht* steht (Garantien,
  Fehlerverhalten, Begründung).
- **Nur Belegtes eintragen.** Was nicht im Code, in Tests oder in Aussagen
  der Nutzer:innen steht, wird `offen` — nie ein plausibel klingender
  Timeout oder SLA erfinden.
- **Benötigte Schnittstellen zu Fremdsystemen** (PSP, ERP …) stehen schon
  im technischen Kontext (Kapitel 3.2). In Kapitel 5 nur darauf verweisen
  und ergänzen, *welche Komponente* sie nutzt.
- **Datenbanktabellen**, die zwei Komponenten gemeinsam lesen/schreiben,
  sind eine Schnittstelle und bekommen eine ID — gerade weil das oft
  übersehen wird.
- Bei vielen Schnittstellen (> 10) nur die bausteinübergreifenden mit
  Steckbrief; komponenteninterne reichen als Zeile in der Übersicht.

### Wo Schnittstellen im Code stehen

| Art | Typische Fundstellen |
|---|---|
| REST/HTTP | `openapi.yaml`/`swagger.json`, Router/Controller (`@app.get`, `@RestController`, `router.ts`), API-Tests |
| Events/Messaging | AsyncAPI, Event-/Message-Klassen, Topic-/Queue-Namen in Config, Producer/Consumer-Code |
| gRPC | `*.proto` |
| Modul-/Bibliotheksgrenze | `api.py`, `__init__.py` mit `__all__`, `index.ts`-Barrels, `public`-Pakete, Import-Linter-/ArchUnit-Regeln |
| Datenbank | Migrationen, ORM-Modelle, die von mehreren Modulen importiert werden |
| Fehler/Garantien | Exception-Klassen, Retry-/Timeout-Config, Unique-Constraints, Idempotency-Keys, Tests für Fehlerfälle |

## Im Diagramm

- Die Whitebox ist eine Gruppe mit `"kind": "box"`: Der Baustein der Ebene
  darüber wird als Box gezeichnet, gefüllt mit seinen Komponenten. Name
  als `label`, Ebene und Pfad als `sublabel` (z. B. `"Ebene 1 · orders/"`).
  Vorlage: `assets/templates/whitebox-diagram.json`.
- Kanten zwischen Komponenten tragen die Schnittstellen-ID plus ein
  Stichwort als Label, z. B. `IF-01 anlegen()` — das bleibt unter der
  Label-Grenze von ca. 20 Zeichen, und die Details stehen im Steckbrief.
- Richtung der Kante = Richtung der Nutzung (Nutzer → Anbieter), wie in
  der Ebene-1-Sicht. Bei Events: Produzent → Konsument, `style: "dashed"`
  für asynchrone Kommunikation.
- Nachbarbausteine, die von außen auf die Komponenten zugreifen, als
  `kind: "external"` an den Rand legen — dann sieht man, welche
  Schnittstellen nach außen angeboten werden.
