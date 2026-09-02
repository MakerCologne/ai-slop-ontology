# Kalibrierungs-Drift-Messvorschrift (#47)

**Status:** spec · **Verwandt:** #12 (Sampling), #36 (model_notes), adr/0003

## Messvorschrift

1. **Eingefrorener Referenzkorpus:** `eval/corpus.jsonl` wird per Commit-Hash als Referenz-Version pinned (aktuelle Version im `maintenance`-Block von ontology.json). Änderungen = neuer Referenzstand (adr/0005-Disziplin), niemals In-place.
2. **Quartals-Re-Score:** fixer Lauf `run_benchmark.py --corpus eval/corpus.jsonl` + Score-Verteilung (Histogramm je Signal) je Quartal; Output als Artefakt im Repo (`eval/drift/YYYY-Qn.json`) mit Datums- und Hash-Feld.
3. **Drift-Alert:** Perzentil-Vergleich zum Vorquartal: Shift > 5 Prozentpunkte bei P50/P90 des slop_score ODER Signal-Beitragsverschiebung > relativ 25 % in einer Kategorie (z. B. FormattingSlop schrumpft, weil künftige Modelle Em-Dashes suppressen) → Ticket + Review-Trigger der Gewichte (Kopplung #106: uniform-Vergleich Pflicht).
4. **Abgrenzung:** intra-Run-Anomalien (#59) vs. Verteilungs-Shift über Modell-Generationen (dieses Dokument).
