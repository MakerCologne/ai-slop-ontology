# Loop-Guard #36 — Modell-Dynamik (model_notes + Halbwertszeiten)

Issue: MakerCologne/ai-slop-ontology#36 (Backlog-Spiegel btm-openclaw-platform#1133)

## Problem

Signale sind modell- und generationsabhängig. GPT-5.1+ supprimiert Em-Dashes,
Claude nutzt sie häufiger als Profis; CurlyQuotes treten fast nur bei
ChatGPT/DeepSeek auf; Puffery-Vokabular wandert ("blatantly positive" →
"subtly positive"). Statische Gewichte veralten still — ohne Register bleibt
die Drift unsichtbar, bis Signale puffern.

## Mechanismus

- `signalModelDynamics` in ontology.json: `modelNotes` (model / effect /
  evidence / asOf) + `halfLives` (quarters / rationale / reviewed_on) je
  Signal, Schema im Block selbst dokumentiert.
- Gate `scripts/check_model_dynamics.py` (M1–M5): Schema-Pflicht, evidence
  Pflicht, bekannte Signalnamen, Halbwertszeit-Pflicht für volatile Notizen
  (weaker/absent/only_model). In `verify.sh` Schritt 3 integriert.
- Kein Score-Impact: model_notes steuern nur Review-Kadenz und
  Risiko-Kommunikation, nie Gewichte direkt (`rules.noScoreImpact`).

## Quellen der Starter-Einträge

Wikipedia "Signs of AI writing" (AIDASH/AICURLY/AIPUFFERY) + Economist-Studie
07/2026 · Deep-Dive `deep/03` (I31) · research/slop-ontology-gap-2026-08-24.

## Verknüpfung

- #47 Kalibrierungs-Drift: Quartals-Re-Score liefert die Empirie-Notizen
  (rules.quarterlyEmpirieNote), Einträge älter als 2 Quartale ohne Re-Score
  gelten als stale.
- #12 Sampling-Loop: neue Generationsstichproben als Evidenzquelle.
- #116 signalReliability: komplementäre Achse (Verlässlichkeit/Status),
  gleiche Register-Disziplin (kein freies Raten, evidence-Pflicht).
