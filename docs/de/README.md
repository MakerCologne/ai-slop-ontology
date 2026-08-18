# Deutsche Dokumentation

**Aktueller Stand:** Ontologie 1.2.1, CLI-Toolkit `slop`, neun rhetorische
Detect-only-Muster sowie die experimentelle Human-/Work-/Management-/SEO-Slop-Erweiterung
und der Microsoft-Ontology-Playground-Adapter.

**Sprachen:** [English index](../en/README.md) · Deutsch

## Wo die deutschen Dokumente liegen

Die Fachdokumente des Projekts sind auf Deutsch verfasst und liegen im
Wurzelverzeichnis. Dieser Ordner enthielt bis August 2026 byte-identische
Kopien davon — neun Dateien, rund 2.000 Zeilen doppelt gepflegter Text, der
bereits auseinanderzulaufen begann. Die Kopien sind entfernt; hier stehen nur
noch Verweise und die Dokumente, die es sonst nirgends gibt.

- [`../../AI-SLOP-ONTOLOGY.md`](../../AI-SLOP-ONTOLOGY.md) — kanonisches Fachmodell, Version 1.2.1
- [`../../ONTOLOGY.md`](../../ONTOLOGY.md) — Taxonomie und Klassifikationslogik
- [`../../ONTOLOGY-STRUCTURE.md`](../../ONTOLOGY-STRUCTURE.md) — ontologische Grundentscheidungen und Properties
- [`../../REFERENCES.md`](../../REFERENCES.md) — Quellen und Referenzen
- [`../../CHANGELOG.md`](../../CHANGELOG.md) — Versionsverlauf
- [`../../REVIEW-2026-07.md`](../../REVIEW-2026-07.md) — Review Juli 2026 (Code, Daten, Quellen)
- [`../../REVIEW-2026-08.md`](../../REVIEW-2026-08.md) — Review August 2026 (Packaging, Engine-Drift, Integrationen)

## Nur hier

- [`human-work-seo-slop.md`](human-work-seo-slop.md) — deutsche Dokumentation der Erweiterung
- [`ontology-playground.md`](ontology-playground.md) — Import in Microsoft Ontology Playground

## Werkzeuge

- [`../USER-GUIDE.md`](../USER-GUIDE.md) — vollständige Anleitung zum CLI-Toolkit `slop` (englisch); jedes Beispiel darin wird von `tests/test_docs_examples.py` ausgeführt
- [`../../README.de.md`](../../README.de.md) — deutscher Einstieg mit Kurzreferenz der `slop`-Befehle

## Forschungsberichte

- [`../../report.md`](../../report.md) — Deep Research, Runde 1
- [`../../report-extended.md`](../../report-extended.md) — erweiterte Recherche, Runde 2
- [`../../RESEARCH-v0.1.md`](../../RESEARCH-v0.1.md) — historischer Forschungsstand v0.1

Die Forschungsberichte bleiben für Nachvollziehbarkeit erhalten. Bei
Widersprüchen gelten das kanonische Dokument, die maschinenlesbaren Dateien und
das aktuelle Changelog.

## Sprachregeln

1. **Bezeichner sind Englisch**, überall: Klassen, Properties, Signal-IDs,
   Dateinamen, YAML-, JSON- und RDF-Inhalte. Sie werden nie übersetzt.
2. **Die Fließtext-Dokumentation ist Deutsch** — das ist der Ist-Zustand des
   Projekts, nicht ein Übergangszustand. Englisch sind derzeit `README.md`,
   `docs/USER-GUIDE.md` und `docs/en/README.md`.
3. Bei Widerspruch zwischen Erklärung und maschinenlesbarem Artefakt gilt das
   Artefakt.
4. **Keine Parallelkopien.** Ein Dokument existiert genau einmal. Wer eine
   englische Fassung eines deutschen Dokuments anlegt, ersetzt das Original und
   verlinkt es — er kopiert es nicht.
   `tests/test_documentation_layout.py` prüft das.
