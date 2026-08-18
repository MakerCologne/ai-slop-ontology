# Deutsche Dokumentation

**Aktueller Stand:** Ontologie 1.2.1, CLI-Toolkit `slop`, neun rhetorische Detect-only-Muster sowie die experimentelle Human-/Work-/Management-/SEO-Slop-Erweiterung und der Microsoft-Ontology-Playground-Adapter.

**Sprachen:** [English, kanonisch](../en/README.md) · Deutsch

Technische Klassen-, Property- und Dateinamen bleiben Englisch. Die erklärenden Texte in diesem Ordner geben den aktuellen fachlichen Stand auf Deutsch wieder.

## Aktuelle Kerndokumente

- [`ai-slop-ontology.md`](ai-slop-ontology.md) — kanonisches Fachmodell, Version 1.2.1
- [`ontology.md`](ontology.md) — Taxonomie und Klassifikationslogik
- [`ontology-structure.md`](ontology-structure.md) — ontologische Grundentscheidungen und Properties
- [`references.md`](references.md) — Quellen und Referenzen
- [`changelog.md`](changelog.md) — Versionsverlauf inklusive unveröffentlichter Änderungen
- [`review-2026-07.md`](review-2026-07.md) — Review von Code, Daten und Quellen
- [`../../REVIEW-2026-08.md`](../../REVIEW-2026-08.md) — Deep Review August 2026 (Packaging, Engine-Drift, Integrationen)
- [`human-work-seo-slop.md`](human-work-seo-slop.md) — aktuelle deutsche Dokumentation der Erweiterung
- [`ontology-playground.md`](ontology-playground.md) — Import in Microsoft Ontology Playground

## Werkzeuge

- [`../USER-GUIDE.md`](../USER-GUIDE.md) — vollständige Anleitung zum CLI-Toolkit `slop` (englisch, kanonisch); jedes Beispiel darin wird von `tests/test_docs_examples.py` ausgeführt
- [`../../README.de.md`](../../README.de.md) — deutsche Kurzreferenz der `slop`-Befehle

## Forschungsberichte

- [`report.md`](report.md) — Deep Research, Runde 1
- [`report-extended.md`](report-extended.md) — erweiterte Recherche, Runde 2
- [`research-v0.1.md`](research-v0.1.md) — historischer Forschungsstand v0.1

Die Forschungsberichte bleiben für Nachvollziehbarkeit erhalten. Bei Widersprüchen gelten das kanonische Dokument 1.2.1, die maschinenlesbaren Dateien und das aktuelle Changelog.

## Sprach- und Versionsregeln

1. `README.md`, YAML, JSON, RDF und Code sind technisch kanonisch Englisch.
2. Die deutsche Dokumentation verwendet dieselben englischen Identifier.
3. Übersetzungen dürfen keine Klassen oder Schwellenwerte umbenennen.
4. Neue fachliche Änderungen müssen gleichzeitig im deutschen Index und in den betroffenen deutschen Kerndokumenten nachgezogen werden.
5. Historische Berichte werden nicht nachträglich umgeschrieben, sondern als historische Stände gekennzeichnet.

## Stand der Erweiterungen

### Human, Work, Management und SEO Slop

- drei Gruppierungsbegriffe,
- 27 konkrete Typen,
- elf querschnittliche Dimensionen,
- sieben SEO-Slop-Untertypen,
- Quellenstatus und Fehlklassifikationsregeln.

### Ontology Playground

Sieben RDF/XML-Ansichten:

- `ai-slop-core`
- `ai-slop-media`
- `ai-slop-domains`
- `ai-slop-intent`
- `work-slop`
- `management-slop`
- `seo-slop`

Alle werden durch Tests und einen eigenen Adapter-Validator geprüft.
