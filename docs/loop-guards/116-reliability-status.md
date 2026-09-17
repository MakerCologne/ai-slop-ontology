# Signal-Reliability & Status (Lebenszyklus) (#116)

**Status:** spec · **Verwandt:** #47 (Kalibrierungs-Drift), #36 (model_notes), #59 (Trajectory), adr/0005

## Problem

Das Ontology-Schema kannte keine Verfalls-/Verlässlichkeits-Dimension je
Signal. Tells veralten (Bild-Hände 2023 weitgehend gepatcht; Purple-Gradient
2024→2026 in Migration). Ohne `status`/`last_verified` wird veraltetes Wissen
weiter gescort, als wäre es aktuell — und Kalibrierungsdrift (BS-I8) bleibt
unsichtbar.

## Schema (SSOT: `ontology.json → signalReliability`)

| Feld | Werte | Bedeutung |
|---|---|---|
| `reliability` | `strong \| moderate \| weak` | strong = kaum zufällig menschlich; moderate = aussagekräftig in Kombination; weak = nur Dichte zählt |
| `status` | `current \| fading \| obsolete` | current = gilt; fading = Migration erkennbar; obsolete = gepatcht, kein Detektionssignal mehr |
| `last_verified` | ISO-Datum | letzter #47-Quartals-Re-Score oder letzte dokumentierte Evidenz |
| `false_positives` | string (Pflicht bei `weak`) | legitime menschliche Arbeit mit gleichem Zeichen |

Methodik-Vorbild: [febbhav/signs-of-ai-design](https://github.com/febbhav/signs-of-ai-design)
(CC BY-SA 4.0): „Reliability describes how much a single match tells you.
Status describes whether the sign still applies to current tools.“
Leitmaxime: **„Judge the absence of decisions, not the presence of a style.“**

## Regeln

1. **obsoleteExcluded:** `obsolete`-Signale werden nicht mehr gescort,
   bleiben aber im Register (Forensik + Kalibrierungshistorie).
2. **weakRequiresFP:** `weak`-Einträge müssen `false_positives` führen.
3. **quarterlyRefresh:** `last_verified` aktualisiert im #47-Quartals-Re-Score;
   Statuswechsel nur mit Evidenz aus `eval/drift/YYYY-Qn.json`.
4. **Kein Raten:** Einträge nur mit dokumentierter Quelle. Starter-Satz nutzt
   das deterministische Konfidenz-Mapping
   (`>=0.85 → strong, 0.6–0.85 → moderate, <0.6 → weak`) — Notation, keine
   Neu-Kalibrierung.

## Starter-Einträge

- **Achse `image`:** alle Indikatoren mit dokumentierter `confidence` (11+).
- **Achse `text.buzzwords`:** Tier 1/2/3 → strong/moderate/weak.

## UI-Achse: `lexikon/ui-tells.yaml`

Kuratierte Import-Auswahl (12 Einträge) aus febbhav/signs-of-ai-design
(CC BY-SA 4.0, Attribution im Dateikopf). Detect-only-Datenbasis — Visuals
brauchen Screenshot-/DOM-Inspektion, kein Scanner-Bestandteil.
Interpretations-Regeln: (1) Zeichen stapeln, nie einzeln; (2) Abwesenheit von
Entscheidungen bewerten, nicht Anwesenheit eines Stils; (3) menschliche
Detektion ≈ Chance-Level → probabilistisch bleiben (#37).

## Durchsetzung

- `scripts/check_signal_reliability.py` (Gate): validiert Enums, Datumsformat,
   FP-Pflicht bei weak, UI-Tells-Attribution.
- Test: `tests/test_signal_reliability.py`.
- Kopplung: Re-Baseline-Kalender in SCORE-GOVERNANCE.md (#67) muss
  `last_verified`-Refresh einschließen.
