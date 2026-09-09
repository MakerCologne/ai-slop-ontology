# Modell-Dynamik: model_notes & Signal-Halbwertszeiten (#36)

**Status:** spec (implementiert in `ontology.json` → `signalModelDynamics` + per-signal `model_notes`) · **Verwandt:** #12 (Sampling-Loop), #47 (Drift-Messvorschrift), #59 (Trajectory-Monitoring), adr/0003

## Problem

Signale sind modell- und generationsabhängig: GPT-5.1+ supprimiert Em-Dashes, Claude nutzt mehr als Profis; Curly Quotes sind ein ChatGPT/DeepSeek-Tell; Puffery-Marker verschieben sich von „blatantly positive" zu „subtly positive". Statische Gewichte veralten still — ohne dokumentierte Modell-Abhängigkeit bleibt das unsichtbar.

## Mechanik

1. **`model_notes` (optional, je Signal):** dokumentiert bekannte Modell-Abhängigkeiten in `ontology.json` (z. B. `"weaker for GPT-5.1+"`, `"Claude-only"`). Kein Ersatz für Gewichtsänderungen — die laufen über den Re-Baseline-Zyklus (SCORE-GOVERNANCE.md).
2. **`signalModelDynamics` (SSOT-Sektion, analog `signalSeverity`/`collisionMatrix`):** Regeln (scope/evidence/review), Halbwertszeit-Kategorien und die dokumentierten Entries je Signal.
3. **Halbwertszeit-Kategorien:**
   - **short** — Oberflächen-Tells (Typografie, Vokabular-Listen wie CurlyQuotes, ImportancePuffery): Monate; Vokabular quartalsweise auffrischen (#12).
   - **medium** — Struktur-/Rhythmus-Tells (UniformSentenceLength, RepeatedOpenings): 1–2 Jahre; quarterly re-score; Deprecation nach zwei scheiternden Zyklen (#63-Lebenszyklus).
   - **long** — semantische/provenance-Tells (FakeAuthoritySlop, halluzinierte APIs): generationsrobust; jährliches Review.
   Halbwertszeiten werden **gemessen** (#47-Drift-Artefakte), nie geschätzt; ohne Messung: `unmeasured`.
4. **Quartals-Empirie-Notiz:** je Signal im Re-Baseline-Zyklus prüfen: `status_since` + `model_notes` zusammen; neue Evidenz aus Sampling-Artefakten (`eval/drift/YYYY-Qn.json`) nachtragen.
5. **Evidence-Pflicht (M6):** jede model_note zitiert ihre Quelle (Studie, Wikipedia AIDASH/AICURLY/AIPUFFERY, oder Quartals-Artefakt).
