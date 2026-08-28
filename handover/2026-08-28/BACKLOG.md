# BACKLOG.md — offene Issues, priorisiert

**Stand: nach v2.8.0.** Gegenüber der ersten Fassung sind #88 und #85 erledigt; #104, #106 und #107 sind neu dazugekommen. Zähl nicht auf die Zahl im alten Titel — hol dir die Liste mit `list_issues`.

Label ist die Wahrheit, nicht der Fließtext. **Kein Prioritätslabel = P2.** Die Konvention und ihre Herleitung stehen in #54 (Triage-Kommentar vom 2026-08-28 plus Korrektur).

Historische Warnung: ein Teil der Issues trägt im Text noch `**Priorität:** P2 (BS-WICHTIG)` aus der Ursprungsrecherche. Das ist Herkunftsspur, nicht Steuerung. Wo Label und Text auseinandergehen, steht der Grund in #54.

---

## P0 — einer

### #100 · GitHub Actions ist deaktiviert

Der einzige Blocker, den ein Agent **nicht allein** lösen kann. Details in `HANDOVER.md` §2.

Einstieg: prüfen, ob der Workflow inzwischen aktiv ist (`gh workflow list` oder ein `workflow_dispatch`-Versuch). Wenn ja: Lauf auf `master` starten, grün sehen, Issue mit dem Lauf-Link schließen.

---

## Erledigt seit der ersten Fassung

- **#88** · TypePattern ohne Positionssemantik → v2.7.0 (PR #103). `^`-Präfix im SSOT als klauselinitialer Marker, vierter Fundort der hartcodierten Musterkopie (`slop_classifier.py`) angeglichen, Hard Negative `clean-tech-14` ergänzt.
- **#85** · Benchmark-Zahl war In-Sample → v2.8.0 (PR #105). `--cross-validate K`. **Lies dazu Fallen 7 und 8 in `PITFALLS.md`** — die erste Messung war falsch, die zweite Schlussfolgerung auch, beide von Reviews zurückgeholt.

## P1 — sieben Defekte plus zwei neue

Reihenfolge begründet: was eine falsche Zahl produziert, kommt vor dem, was nur eine Absicherung vermissen lässt.

### #106 · Beitrag der Kalibrierung ist unbeziffert (neu)

Uniforme Gewichte messen F1 0.989, die kalibrierten 0.991 — auf dem ganzen Korpus ein Text von 331. Ob die Kalibrierung wirklich so wenig trägt, ist damit **nicht** entschieden: die Coordinate Ascent bleibt von einem uninformierten Start aus auf einem Plateau stehen, obwohl bessere Vektoren existieren (Falle 8).

Einstieg: `--cv-starts` aus #85 benutzen, Ablation uniform vs. kalibriert vs. Multi-Start-Refit auf Korpus, Control Set **und** Hard Negatives. Nebenher: der Herkunfts-Kommentar in `slop_scorer.py` führt „F1 0.47 → 0.89" als Leistung der Kalibrierung — das ist ein älterer, kleinerer Korpus und beschreibt den heutigen Beitrag nicht.

### #107 · Held-out gilt nur für die Gewichte (neu)

Die Signalinventare (`BUZZWORD_TIERS`, `PHRASE_CATEGORIES`, …) sind aus demselben Korpus gewonnen — `check_ssot.py` führt sie selbst als `corpus-calibrated`, und die Batch-F-Phrasen stammen aus dessen FN-Texten. Ein Fold kann von Signalen belohnt werden, die nach Ansicht seiner eigenen Texte entworfen wurden.

Einstieg: die zwei Wege stehen im Issue. Der interessantere ist, die Evidenzregel („≥3 Slop-Texte, 0 Clean-Texte") als **ausführbaren Code** zu schreiben — dann lässt sich die Merkmalsauswahl je Trainingsfold nachfahren, und die Regel wird nebenbei vom Brauch zum Gate.

### #70 · Claim-Register + Zählregel

`scripts/count_signals.py` existiert nicht. Jede Umfangszahl in README/CHANGELOG braucht eine maschinell ausführbare Messvorschrift oder die Kennzeichnung als Schätzung.

Einstieg: hängt inhaltlich an #83 (die zehn toten Phrasen wurden mitgezählt) und #85. Die Regel, die #83 etabliert hat: **gezählt wird nur, was matchen kann.** Nimm die `slop info`-Datumsinkonsistenz aus `STATE.md` mit.

Das Muster für die Umsetzung liegt seit #85 vor: `tests/test_cross_validation.py::DocumentationTest` bindet die in SKILL.md veröffentlichten Zahlen — Korpusgröße, Aufteilung, P/R/F1, Konfusionsmatrix — an einen frischen Benchmark-Lauf. Genau das braucht #70 für jede Umfangszahl. Zwei echte Drifts hat dieser Pin schon gefunden (SKILL.md 17 Clean-Texte alt, `docs/EVALS.md` mit `314 Texte`).

### #52 · Kurztext-/Längen-Guards

`std_dev` über weniger als drei Sätze ist undefiniert; „per 500 words"-Normalisierungen entarten bei 50-Wort-Texten. Gemessen: der Skill-Scorer liefert für ein einzelnes Wort 0.20, für einen Vier-Wort-Titel 0.17 — Rauschen aus degenerierter Statistik, kein FP über Schwelle, aber undefiniertes Verhalten.

Einstieg: Mindestlängen je Metrik, definiertes Verhalten (skip oder skaliert), Fixtures für 5/20/50 Wörter. Solange das fehlt, ist jede FP-Aussage für Kurztext unbelegt.

### #46 · Signal-Kollisions-Matrix

Kollisionsdisziplin wird heute je Batch handgeprüft. Bei 70 registrierten Signalkonstanten trägt das nicht mehr. Vier konkrete Paare stehen im Issue.

### #47 · Kalibrierungs-Drift-Messvorschrift

Der Referenzkorpus liegt seit #72 vor (`eval/discourse_ref.jsonl`), die Messvorschrift fehlt. Ein eingefrorener Korpus ohne Re-Score-Regel altert stillschweigend.

### #55 · Severity-Tier je Signal

`severity: critical|high|medium` in `ontology.json`, critical als Hard-Gate. Trug schon in der Ursprungsrecherche P1.

### #56 · Voice-Drift-Guardrail

β = 25 % Token-Änderung als Non-Regression. Trug schon P1. Wird erst relevant, wenn etwas Ausgabetexte verändert — heute tut das nichts (adr/0001).

---

## Vorhaben-Strang — Human / Ideological Slop (Epic #89)

Aus dem Übergabepaket `human-slop-handover` vom 2026-08-28, von mir als Issues angelegt. **Die Reihenfolge zwischen diesem Strang und dem Defekt-Strang hat der Auftraggeber nicht entschieden — frag ihn.**

```
#92  B-Nursery (detect-only Rhetorik)   ─┐
                                          ├─> #90 ADR 0008 ─> #93 A-Extension ─> #98 Eval-Korpus
#94  Ethnopluralismus-Lexikon           ─┘
#95 / #96 / #97  Fallstudien   (liefern die annotierten Texte für #98)
#91  Optionsbewertung A vs. B  (Entscheidungsvorlage für #90)
```

Harte Randbedingungen aus dem Paket, die du nicht neu verhandelst:

- Detect-only zuerst, kein Score. `polemic_risk` niemals in die Noisy-OR von `slop_score` falten.
- Parteizugehörigkeit ist kein Signal. Frames und Falsifizierbarkeit sind Signale.
- `keep_when` ist Pflicht in jedem Pattern; Precision auf dem Hard-Negative-Satz = 1.0, Recall nachrangig.
- Eigenes Eval-File `eval/human_ideological.jsonl`, **nicht** in `eval/corpus.jsonl` mischen (adr/0005).
- Kein Auto-Rewrite politischer Texte (adr/0001).

Wenn du #92 anfängst: das sind ~100 kurze Beispieltexte in eigenen Worten (10 Patterns × 3/3/2 plus 20 Hard Negatives). Kläre vorher mit dem Auftraggeber, wie ausführlich die sein sollen — insbesondere für `EnemyVermin` (Entmenschlichungs-Metaphorik).

---

## P2 — der Rest

Portierung aus PR #6: **#86** (human/work/SEO-Extension, braucht erst eine ADR-Entscheidung), **#87** (Playground-Adapter, hängt an #86).

Abgleich mit Fremdkatalog: **#104** (Lücken gegenüber `petergyang/no-ai-slop`, MIT — Re-Derivation mit Attribution, keine Übernahme).

Fallstudien: **#95**, **#96**, **#97**.

Ontologie-Extension: **#93**.

Alles Übrige ohne Prioritätslabel, damit P2: #81, #77, #76, #75, #73, #71, #62, #61, #60, #59, #58, #57, #54, #53, #45, #44, #39, #38, #37, #36, #35, #30, #15, #12, #11.

Zwei davon sind wahrscheinlich schon weitgehend umgesetzt und nur nicht geschlossen — **#81** (`naturalness_guard.py` existiert mit Tests) und **#76** (Akzeptanzkriterium „≥20 DE-Signale" ist mit 22 erfüllt). Prüf sie mit Beleg, bevor du Neues baust; #78 und #79 waren derselbe Fall und ließen sich mit einem Kommentar schließen.
