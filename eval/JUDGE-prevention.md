# Judge-Rubrik — Prevention-Contract-Eval (L2, #232)

**Status:** Erstmessung 2026-09-17 · **Korpus:** `eval/prevention_genres.jsonl` (7 Gattungen × 3 Varianten, alle `own:handwritten`) · **Runner:** `eval/run_prevention_eval.py` (deterministisch) · **Vertrag:** `skills/ai-slop-detection/references/writing-rules.md` (#228)

## Rolle der Ebenen

- **Deterministisch (Runner):** C1–C7-Heuristiken liefern Messwerte und Kandidaten-Flags.
- **Judge (L2, diese Rubrik):** Ein Mensch oder Reviewer bewertet jedes Runner-Flag **und** eine Stichprobe nicht geflaggter Stellen nach der Taxonomie unten. Der Judge ist Befund/Veto, nie alleiniges Abbruchkriterium (analog Control-Set-Gate, adr/0003-Logik).
- **Kein Score-Einfluss:** Die Praeventionseval bewertet Generierungs-/Schreibverhalten, geht nicht in den Slop-Score ein (adr/0006 detect-only).

## Kriterien (Vertrag aus writing-rules.md)

| ID | Kriterium | Messung | Judge-Frage |
|---|---|---|---|
| C1 | Ich-Anfang ohne Personenbezug | Erstsatz `^Ich` + Anlauf-Verb (denke/moechte/wuerde) | Ist die Person tatsaechlich Gegenstand oder Haltung relevant? |
| C2 | Lob-zuerst / Paraphrase-vor-Eigenanteil | Lob-/Dank-Anfangsliste | Kommt der eigene Inhalt vor dem Echo? |
| C3 | Dreiergruppe als Default | Komma-`und`-Dreierstruktur | Tragen alle drei Elemente, oder fuellt das dritte nur? |
| C4 | Konnektor-Absatz-/Satzfolge | ≥2 Konnektorbeginne in Folge | Verzahnt der Konnektor Inhalt oder ersetzt er ihn? |
| C5 | Rhetorische Frage ohne Frageabsicht | Text endet auf `?` (Hook-Heuristik) | Wird eine echte Antwort erwartet? |
| C6 | Opener-Diversitaet | <2 Einstiegstypen je Gattung | — (deterministisch ausreichend) |
| C7 | Isometrie | CV der Variantenlaengen < 0.08 | Nur Befund: aehnliche Laenge ≠ automatisch Kopie |

## Error-Taxonomie (Judge-Urteile)

| Code | Bedeutung | Konsequenz |
|---|---|---|
| `TP` | Flag bestaetigt, Vertrag verletzt | Fix im Prompt/Text, L2-Report |
| `FP-judge` | Heuristik flaggt, Kontext rechtfertigt (keep_when) | Known-FP-Register, Heuristik pruefen |
| `FN-judge` | Kein Flag, aber Vertrag verletzt | Kriterium/Heuristik erweitern oder L1-Fixture |
| `AMBIG` | Kontextabhaengig, keine Regelveraenderung | Dokumentation als Hard Negative |

## Erstmessung 2026-09-17 (`eval/prevention_results_2026-09-17.json`)

- 14 Flags gesamt; **alle absichtlich schwachen Varianten** (Labels `ich_senderzentriert`, `lob_paraphrase_*`, `lob_triad_connector`, `connector_saetze`, `ich_connector_je_absatz`) mindestens ein Flag.
- Judge-Durchgang (Agent-Review, Goswin/OpenClaw-Burn):
  - `FP-judge`: pg-01 v3 C5 ("passt Ihnen Donnerstag?" — echte Terminfrage), pg-05 v3 C5-ahnlicher Grenzfall nicht geflaggt (`AMBIG`).
  - `FN-judge`: pg-04 v2 C3 verfehlt ("Sie bestehen aus Zahlen, sie haben Dimensionen und sie ermoeglichen Aehnlichkeit" — Wiederholungsstruktur statt Komma-Dreier) → L1-Kandidat, sobald Signal-PR #230/#231 landen.
  - pg-05 v2 traegt C2 (Dank-Anfang in Lob-Liste) — semantisch Senderzentrierung, korrekt als Befund.
- C7-Schwelle von 0.12 auf **0.08** kalibriert (0.12 flaggte 5/7 Gattungen inkl. sauberer Varianten). pg-01 bleibt Grenzfall (CV 0.073) — als `AMBIG` registriert.

## L3-Anbindung (Quartals-Re-Score)

Der Praeventions-Eval laeuft im Re-Baseline-Zyklus (SCORE-GOVERNANCE.md Kalender) mit: frischer Erstmessung auf dem eingefrorenen Korpus, Vergleich der Flag-Raten je Kriterium gegen 2026-09-17-Baseline (14 Flags: C1×3, C2×4, C3×1, C4×2, C5×3, C7×1) und Judge-Stichprobe ≥ 20 %. Drift > ±30 % je Kriterium → Review des Vertragsdokuments vor Heuristik-Aenderung.
