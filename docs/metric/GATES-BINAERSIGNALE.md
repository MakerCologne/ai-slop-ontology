# Metrik-Design: Gates statt Score für Binärsignale (#118)

**Status:** spec (nicht aktiviert) · **Governance:** docs/SCORE-GOVERNANCE.md · **Verwandt:** #55 (signalSeverity/Hard-Gates) · **Quelle:** piyushbhattadforapps/pseo-quality-gate (13 harte Gates, „necessary, not sufficient")

## Problem

Manche Signale sind **binär** (Platzhalter-Credentials, Elision-Comments, HardcodedSecret) — ein Score-Beitrag ist hier die falsche Kategorie: Fail ist starker Prädiktor, Pass ist keine Garantie. Aktuell gibt es keine Gate-Kategorie im Scorer.

## Vorschlag

Gate-Kategorie `gates` im Scorer-Vertrag:

- `gate: true` je Signal (Extension von `signalSeverity`, #55): Fail → harte Markierung im Report + Hard-Gate-Verhalten (wie critical, #55), **kein** Score-Beitrag.
- Semantik wie pseo-quality-gate: Fail irgendeines Gates ist „necessary, not sufficient"-Indikator; Pass aller Gates impliziert nichts.
- SEO/Website-Achse zuerst: Platzhalter-Credentials, Elision-Comments, Deindexations-Vorstufen.

## Aktivierungspfad

Spec → Gate-Flags je Signal (ontology.json) → Runner-Ausgabe `gates: pass|fail` getrennt vom Score → Freigabe via SCORE-GOVERNANCE. Kein Score-Verhalten wird in diesem PR geändert.
