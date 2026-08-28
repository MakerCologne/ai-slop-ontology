# STATE.md — verifizierter Stand, 2026-08-28

Alle Zahlen hier sind gemessen, nicht geschätzt. Jede Zeile hat ein Kommando, mit dem du sie nachprüfst.

## Kopf

| | |
|---|---|
| `master` | nach Merge von PR #105 — Hash mit `git log --oneline -1` prüfen |
| Version | 2.8.0 (`AI-SLOP-ONTOLOGY.md`, `ai_slop_ontology.yaml`) |
| Tests | `python -m pytest -q` nachzählen; zuletzt 655 passed, 66 Testdateien |
| Korpus | `eval/corpus.jsonl` — 331 Texte = 221 slop + 110 clean |
| Benchmark skill-pipeline (in-sample) | P 1.0 / R 0.995475 / F1 0.998 (TP 220 / FP 0 / TN 110 / FN 1) |
| Benchmark skill-pipeline (held-out, Gewichte) | s. `docs/EVALS.md` — **kein** Generalisierungsschätzer, #107 |
| Der eine FN | `hard-slop-subtle-01` bei 0.254 — bekannt, kein Regressionsfall |
| Self-Check | 27 Dokumente, 2 registriert, Schwelle 0.40 |

Nachmessen: `bash scripts/verify.sh`

## Was in der Vorgängersession gelandet ist

### PR #99 → v2.6.0 (fünf Issues)

| Issue | Sache | Kern des Fixes |
|---|---|---|
| #82 | `pip install .` lieferte kaputte CLI | Backend setuptools → hatchling, `force-include` legt Laufzeitdaten nach `slopkit/_bundled/` |
| #83 | 10 SSOT-Phrasen konnten nie matchen | Platzhalter-Expansion in allen drei Term-Regex-Modulen |
| #69 | Detektor bewertete eigene Doku 0.90–0.995 | Markdown-Präpass, opt-in über `--strip-markup` |
| #84 | CI lief 420 von 539 Tests | Workflow auf pytest, jedes Gate als eigener Schritt, Benchmark mit Untergrenze |
| #48 | kein Self-Check gegen die eigene Doku | `scripts/self_check_docs.py` + Ausnahmen-Register + `docs/DOC-STYLE.md` |

Vor dem Merge fand ein Review **neun** Defekte im eigenen Diff — Details in `PITFALLS.md`, dokumentiert im CHANGELOG unter „Review-Nacharbeit (vor dem Merge)".

### PR #101 → v2.6.1 (Codex-Review-Nachtrag)

Zwei reale Gate-Defekte, beide in dem, was #99 gerade erst eingeführt hatte: eine Ausnahme-Obergrenze bei 1.0, die nie verletzt werden konnte, und Untergrenzen, die gegen gerundete Metriken verglichen.

### PR #103 → v2.7.0 (#88, Positionssemantik)

Ein führendes `^` in einem SSOT-Muster heißt jetzt „diese Phrase muss eine Klausel **eröffnen**". `^here are` ist der Listicle-Opener, nicht die Mitte von „the commands shown here are known to run". Opt-in: ein Muster ohne `^` verhält sich wie bisher.

Nebenbefund, der die Serie fortsetzt: `slop_classifier.py` hielt eine **hartcodierte Zweitkopie** der Mustertabelle, die nicht über den geänderten SSOT-Pfad ging. Der False Positive blieb bestehen, nachdem der Fix vollständig aussah — die Precision fiel messbar auf 0.995. Vierter Fundort dieser Klasse.

### PR #105 → v2.8.0 (#85, Held-out-Schätzer)

`eval/run_benchmark.py --cross-validate K`. Was du davon wissen musst, bevor du die Zahl benutzt:

- Sie ist held out **mit Bezug auf die Gewichte**. Die Signalinventare stammen aus demselben Korpus (#107) — das steht als Vorbehalt in der Ausgabe selbst und ist per Test gepinnt.
- Der Lauf kostet rund 30–60 Minuten (L3). Er läuft **nicht** in CI, und `--min-precision`/`--min-recall` werden zusammen mit `--cross-validate` abgelehnt statt ignoriert.
- Jeder Fold startet bei uniformen Gewichten plus mehreren korpusunabhängig geseedeten Neustarts (`--cv-starts`). Der Grund steht in `PITFALLS.md` 7 und 8 — beide Male hatte ich eine Zahl veröffentlicht, die ein Review zurückholen musste.

Zwei weitere Nebenbefunde: `eval/calibrate.py` war überhaupt nicht lauffähig (13-Namen-Kopie gegen 14 Dimensionen, `KeyError: 'portability'` — sechster Fundort), und SKILL.md nannte einen 17 Clean-Texte alten Korpusstand. Beide sind jetzt an eine Messvorschrift gebunden statt an ein Versprechen.

### Geschlossen ohne Merge

- **PR #4 und #6**: keine gemeinsame Historie mit `master` (`git merge-base -a` liefert nichts, 50 gegen 66 bzw. 56 Commits). Jeder ihrer Befunde wurde gegen den heutigen Stand nachgeprüft und entweder als erledigt festgestellt oder ticketiert (#82, #83, #69, #85, #86, #87). Die Branches bleiben erhalten.
- **#78, #79**: waren umgesetzt, aber nie geschlossen. Mit Beleg geschlossen.

## Die acht Gates

In der Reihenfolge, in der der Workflow sie fährt:

| Gate | Kommando | erwartete Ausgabe |
|---|---|---|
| Suite | `python -m pytest -q` | `655 passed` |
| Konsistenz | `python scripts/check_consistency.py` | `Consistency check passed` |
| SSOT C1–C4 | `python scripts/check_ssot.py` | `SSOT check passed` |
| Methodik | `python scripts/check_methodology.py` | `OK — METHODOLOGY.md, ADRs …` |
| Signal-DoD | `python scripts/check_signal_dod.py` | `0 FAIL, 10 WARN` |
| FP-Baseline | `python scripts/fp_baseline.py --check` | `no drift against committed register` |
| Control-Set | `python eval/run_control_set.py` | `GATE PASSED` |
| Self-Check | `python scripts/self_check_docs.py` | `SELF-CHECK PASSED (27 documents, 2 registered …)` |
| Benchmark | `python eval/run_benchmark.py --min-precision 1.0 --min-recall 0.99` | `BENCHMARK GATE PASSED` |

`check_signal_dod` meldet **10 WARN** — das ist der erwartete Stand, keine Regression. Nur `FAIL` ist ein Blocker.

## Selbstanwendung: der Detektor auf die eigene Doku

Nach dem Präpass (#69):

```
README.md            0.000   (vorher 0.900)
ONTOLOGY.md          0.000   (vorher 0.933)
AI-SLOP-ONTOLOGY.md  0.000   (vorher 0.986)
docs/USER-GUIDE.md   0.000   (vorher 0.995)
```

Zwei Dokumente bleiben registriert, weil sie Katalogmaterial im Fließtext führen müssen: `CHANGELOG.md` (0.973, Deckel 0.983) und `report.md` (0.964, Deckel 0.974).

## Wichtige Wege im Repo

```
ontology.json                              SSOT — alles andere ist Sicht darauf
src/classifier.py, src/scorer.py           Engine 1
skills/ai-slop-detection/scripts/          Engine 2 (bewusste Kopie, muss self-contained bleiben)
slopkit/                                   CLI, lädt beide über _engine.py
eval/corpus.jsonl                          Benchmark-Korpus, 331 Texte (221 slop / 110 clean)
eval/control_set.jsonl                     Golden Control Set (L2-Gate)
eval/fp_baseline.json                      tolerierte Detektor-Outputs je Hard Negative
eval/self_check_docs.json                  Ausnahmen des Doku-Self-Checks
docs/SCORE-GOVERNANCE.md                   Goodhart-Regelwerk, konstitutiv
docs/EVALS.md                              L1/L2/L3-Zuordnung — Pflicht für jede neue Testdatei
docs/SIGNAL-DOD.md                         3/3/2-Regel je Signal
docs/DOC-STYLE.md                          Schreibregel für die eigene Doku (#48)
eval/calibrate.py                          Gewichts-Kalibrierung (L3) — liest DEFAULT_WEIGHTS
                                           aus dem Scorer, kopiert sie nicht (#85)
adr/                                       Architekturentscheidungen, MADR
```

## Eine bekannte Inkonsistenz, nicht ticketiert

`slop info` mischt die Version aus dem kanonischen Markdown (2.6.1) mit dem Datum aus `ontology.json` (2026-08-25). Der Consistency-Check merkt das nicht, weil er nur JSON gegen TTL vergleicht. Kosmetisch, aber es gehört inhaltlich zu #70 (Claim-Register) — dort mitnehmen, statt ein eigenes Ticket aufzumachen.
