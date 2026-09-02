# SCORE-GOVERNANCE.md — Score-Governance & Goodhart-Regelwerk

**Status:** konstitutiv (v2.0.0, Issue #67) · **Geltungsbereich:** jede Änderung an Scores, Gewichten, Thresholds und Metriken dieses Repos.
**Referenz:** docs/METHODOLOGY.md (M9 Goodhart-Resistenz), adr/0005 (ehrliche Zahlen), Loop-Research Goodhart-Kapitel (`research/slop-loop-pipeline-2026-08-24/report.md`, extern — Exit-Checks E1–E5).

Grundprinzip (Campbell/Goodhart): **Kein einzelner Score darf alleiniges Ziel sein.** Jede Optimierung braucht Freigabe, Guardrails, kalendarische Re-Baselines und ein Change-Protokoll. Goodhart-Varianten mit Relevanz hier: *Extremal* (Slop-Stil verschiebt sich mit Modellgenerationen, #36) und *Adversarial* (ein Rewriter optimiert den Scorer statt die Qualität, #40/#59 — s. adr/0001).

---

## Optimierungs-Freigaben

Was darf der Loop (Burn, Kalibrierung, Rewriter-Konsumenten) optimieren — und was nicht?

| Metrik / Größe | Optimierung erlaubt? | Regel |
|---|---|---|
| `slop_score` (Composite, threshold 0.40) | **Nein als direktes Ziel.** | Der Score ist Messgröße, nie Zielfunktion. Loop-Exit nur über Multi-Kriterien-Exit-Checks (Score + qualitative Guardrails + Stabilität + Human-Eskalation; Loop-Report E1–E5). |
| Precision auf Hard Negatives | **Ja — nach oben.** | FP-Rate 0.0 je Genre (#41-Korpus) ist geschützt; jede Verschlechterung blockt den Merge (FP-Gate). |
| Recall auf #41-Korpus | **Ja — nach oben**, ohne Precision-Verlust. | Recall-Lücken werden zu Tickets (aktuell F1 0.476, R 0.312 — Throat-Clearing/Emphasis-Phrasen), nicht durch Threshold-Senkung „gekauft". |
| Signal-Gewichte | **Nur aus Korpus-Statistik.** | Nie „gefühlt": Gewichte aus Kalibrierungsdaten (eval/calibrate.py), je Änderung eigenes Changeset + Change-Protokoll (unten). |
| Threshold 0.40 | **Gesperrt** außerhalb einer Re-Baseline. | Änderung nur im Re-Baseline-Zyklus mit voller vorher/nachher-Messung. |
| Voice-/Stil-Metriken | **Nein** (nur Non-Regression). | Voice-Budget β=25% (#56) ist Guardrail, kein Optimierungsziel. |
| Benchmark-Korpus selbst | **Nein im laufenden Loop.** | Korpus-Änderungen sind eigene Changesets mit Belegtquote ≥ 60 % + Quellenpflicht (adr/0005) — niemals nebenbei im Optimierungs-PR. |

## Guardrail-Pflicht

Jede Score-/Gewichtsänderung braucht im PR einen **Non-Regression-Beweis** auf:

1. **Control Set** (eval/run_control_set.py): Gate bleibt grün; bekannte FNs lösen sich nur durch dokumentierte RESOLVED-Meldung.
2. **Benchmark** (eval/run_benchmark.py): Precision je Genre nicht schlechter (FP-Rate bleibt 0.0), Recall nicht schlechter — oder die Verschlechterung ist benannt, begründet und akzeptiert.
3. **Voice-Budget** (#56, M10): bei allem, was Ausgabetexte berührt — β=25 % Token-Änderung als Non-Regression-Gate.
4. **Konsistenz** (scripts/check_consistency.py): SSOT-Parity grün (adr/0002).

**Praxisfälle:**
- **ADR-0005 / #41 (Benchmark-Disziplin):** die alte Baseline F1 0.982 (53-Texte-Corpus ohne Hard Negatives) wurde durch die ehrliche Zahl F1 0.476 (P 1.0 / R 0.312, 314-Texte-Korpus, 2026-08-25) ersetzt — Lehrfall: eine Metrik, die nur gegen sich selbst misst, wird zur Goodhart-Falle. Beide Zahlen gehören ins Change-Protokoll jeder Baseline-Ablösung.
- **Batch A Kalibrierung:** Guardrails liefen mit (#23-Quote-Exemption + Kumulativregel; Benchmark P 1.0 gehalten, Recall +0.034) — Musterfall: Zielmetrik-Verbesserung *mit* FP-Guardrail im selben PR.
- **#14 Gewichtsreduktion 0.03 → 0.02:** Score-wirksame Ein-Parameter-Änderung wurde als eigenes Changeset mit Control-Set- und Benchmark-Messung geführt — Musterfall für die Change-Protokoll-Pflicht unten.

## Re-Baseline-Kalender

- **Rhythmus:** quartalsweise (Q-Ende) — Messvorschrift #47 (Drift gegen eingefrorenen Referenzkorpus), Kalibrierungs-Loop #12.
- **Umfang je Zyklus:** Re-Score des kompletten Korpus (L3, s. docs/EVALS.md #68), Drift-Bericht je Signal (Halbwertszeiten #36), Gewichte neu aus Korpus-Statistik ableiten ( SpamAssassin-Analogie: mass-check → rescore), Threshold-Review, Signal-`status`-Übergänge prüfen (#63-Lebenszyklus: ≥2 überlebte Zyklen → stable; Rückfälle → deprecated).
- **Außerplanmäßige Re-Baseline:** bei neuem Hard-Negative-Genre, Modellgenerations-Wechsel oder Trajektorien-Anomalie (#59) — jeweils mit begründetem Ticket.
- **Dokumentation:** Ergebnis je Zyklus im CHANGELOG (eigener Abschnitt „Re-Baseline QX/YYYY").

## Change-Protokoll

Für **jede** Score-/Gewichts-/Threshold-Änderung gilt zwingend:

1. **Messung vorher/nachher** am Control Set **und** am Benchmark (Zahlen im PR, nicht im Kopf).
2. **Guardrail-Beweis** nach Abschnitt „Guardrail-Pflicht".
3. **Dokumentation im CHANGELOG** mit: alter Wert → neuer Wert, Messvorschrift (Kommando, Korpus-Version, Datum), Ergebnis, Begründung; Versions-Bump konsolidiert am Batch-Ende.
4. **SSOT-Eintrag**:ontology.json aktuell (inkl. `status`/`status_since`, #63), Parity-Gate grün.
5. **Optimierungs-Freigabe** geprüft (Tabelle oben): ist die Größe überhaupt optimierbar? Falls nein: nur im Re-Baseline-Zyklus.

Verstoß gegen 1–3 = Review-Blocker (CHANGES_REQUESTED), unabhängig vom Messergebnis.

## Held-out-Grenze: Gewichte ja, Signalinventare nein (#107, 2026-09-02)

`run_benchmark.py --cross-validate K` schließt die Leckage über die **Gewichte**, nicht über die **Merkmale**: `BUZZWORD_TIERS`, `PHRASE_CATEGORIES`, `STRUCTURAL_INDICATORS`, `MORAL_PATTERNS`, `AUTHORITY_PATTERNS`, `SUBSTITUTE_VERB_PATTERNS`, `INTENSIFIERS` sind als `corpus-calibrated` aus demselben Korpus gewonnen (Allowlist in `scripts/check_ssot.py` sagt es selbst; SKILL.md sagt es für Batch F).

Konsequenz: Die Zahl aus `--cross-validate` ist ein **Held-out-Wert bezüglich der Gewichte**, kein Generalisierungsschätzer. Sie bleibt informativ, ist aber in Claim-Kontexten so zu nennen.

Ehrliche Auswege (eigene Arbeit, nicht nebenbei):

1. **Unberührter Evaluationskorpus** — ein zweites, nach dem Inventar-Schnitt eingefrorenes Korpus, das nie in Signals/Phrasen eingeflossen ist.
2. **Anspruch in Doku zurücknehmen** — Zahlen konsequent als gewichts-held-out ausweisen (dieser Abschnitt + #106).

Bis (1) gilt (2): alle Doku-Stellen, die CV-Zahlen als Generalisierung lesen lassen, verwenden die Formulierung „held-out bezüglich der Gewichte".
