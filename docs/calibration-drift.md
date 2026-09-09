# Kalibrierungs-Drift-Messvorschrift (Issue #47)

**Status:** Messvorschrift · **Kadenz:** quartalsweise · **Priorität:** P2 (BS-WICHTIG)

## Problem

Gewichte und Schwellenwerte werden einmalig gegen einen Korpus kalibriert
(`eval/calibrate.py`). Modelle ändern sich aber: Wenn künftige Modelle z. B.
Em-Dashes supprimieren (GPT-5.1), sinkt der Beitrag von FormattingSlop
still — Gewicht bleibt, Kalibrierung altert unbemerkt. Diese Vorschrift
macht das Altern messbar und triggert einen Review, bevor die Detektion
schleichend blind wird.

## Artefakte

| Artefakt | Zweck |
|---|---|
| `scripts/calibration_drift.py --init` | Friert Referenz-Snapshot ein: Score-Verteilung (p10/p50/p90 je Label), per-Signal Hit-Rates, per-Fixture tolerierte Outputs + Text-Hash → `eval/calibration_reference.json` |
| `scripts/calibration_drift.py --check` | Re-Score gegen eingefrorenen Referenz-Snapshot; Alert + Exit 1 bei Drift |

Ergänzt `scripts/fp_baseline.py` (#80): jenes Register pinnt tolerierte
Outputs auf **Hard Negatives** (FP-Druck); dieses pinnt die **gesamte
Score-Verteilung und Signal-Beiträge** (Kalibrierungs-Alterung).

## Drift-Modell

| Typ | Bedeutung | Alert-Schwelle |
|---|---|---|
| `score_drift` | per-Fixture `\|Δ slop_score\|` | > 0.05 |
| `score_percentile_shift` | p10/p50/p90-Shift je Label | > 0.05 |
| `signal_rate_shift` | Hit-Rate-Delta je Signal/Label | > 0.10 |
| `signal_added` / `signal_removed` | toleriertes Output-Set eines Fixtures | jede Änderung |
| `fixture_missing` / `fixture_unknown` | Korpus vs. Referenz inkonsistent | jedes Vorkommen |
| `fixture_text_changed` | Korpus-Text unter eingefrorener ID editiert (sha256) | jedes Vorkommen → Referenz nicht mehr vergleichbar, re-init nötig |

## Messvorschrift (quartalsweise)

1. **Re-Score:** `python3 scripts/calibration_drift.py --check`
2. **Alert-Fall (Exit 1):** Kein Auto-Tuning. Jeder Alert ist ein
   **Weight-Review-Trigger**: betroffene Signale in `ontology.json`
   prüfen, `model_notes` (#36) aktualisieren, ggf. Sampling-Loop (#12)
   für frische Empirie nutzen, danach `eval/calibrate.py` und
   **bewusstes** Re-Init des Registers.
3. **Ohne Alert:** nichts tun. Das Register bleibt unverändert stehen —
   genau das ist der Punkt (Stillstand = bestätigte Stabilität).
4. **Korpus-Änderungen** (neue Fixtures, Text-Edits) sind erlaubt,
   erfordern aber ein dokumentiertes Re-Init, damit der Bruch sichtbar
   bleibt (`fixture_text_changed` macht ihn explizit).

## Schwellen-Begründung

- Score-Schwellen 0.05 ≈ 1/4 der borderline-Bandbreite aus dem
  #79-Register und deckt typische Modell-Suppressions-Sprünge.
- Signal-Rate 0.10 = 10 Prozentpunkte Hit-Rate-Delta: klein genug für
  frühe Sichtbarkeit, groß genug gegen Stichprobenrauschen des
  Referenzkorpus (n=331).

## Verknüpfte Issues

- #12 (Sampling-Harness) — liefert frische Empirie für den Review-Fall
- #36 (`model_notes`) — dokumentiert Modell-Dynamik je Signal
- #80 (FP-Baseline) — Schwester-Register, Hard-Negativ-Seite
