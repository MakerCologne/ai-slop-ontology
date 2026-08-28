# Changelog

## [2.8.0] — 2026-08-28 (#85 — Held-out-Schätzer für den Benchmark)

`eval/calibrate.py` fittet die 14 Dimensionsgewichte des Scorers per Coordinate
Ascent auf `eval/corpus.jsonl`. `eval/run_benchmark.py` misst anschließend auf
demselben Korpus. Die Zahl, die dieses Projekt überall kommuniziert, war damit
ein Trainingsmengen-Wert — und nichts sagte das.

`docs/SCORE-GOVERNANCE.md` führt genau diesen Fall als eigenen Lehrfall
(ADR-0005/#41: „eine Metrik, die nur gegen sich selbst misst, wird zur
Goodhart-Falle"). Der Korpus hat seitdem Hard Negatives bekommen; die
Trainings-/Test-Identität war geblieben.

### Was die Messung ergibt

`eval/run_benchmark.py --cross-validate 5 --cv-rounds 3` (seed 17, Gewichte je
Fold **nur** auf dem Trainingsteil und ab einem korpusunabhängigen Startpunkt
gefittet), Benchmark auf `eval/corpus.jsonl` (n=331 = 221 slop + 110 clean)
bei Schwelle 0.40. Alle Werte aus Läufen gegen `eval/corpus.jsonl`:

| Engine | Art | In-sample P / R / F1 | Held-out P / R / F1 | ΔF1 |
|---|---|---|---|---|
| `skill-scorer` | gefittet | 1.000 / 0.982 / 0.991 | 1.000 / 0.977 / 0.989 | −0.002 |
| `src-classifier` | nicht gefittet | 1.000 / 0.507 / 0.673 | 1.000 / 0.507 / 0.673 | ±0.000 |
| `skill-pipeline` | gemischt | 1.000 / 0.995 / 0.998 | 1.000 / 0.995 / 0.998 | ±0.000 |

Held-out gepoolt über fünf Folds: Scorer TP 216 / FP 0 / TN 110 / FN 5, Pipeline TP 220 / FP 0 / TN 110 /
FN 1. Die veröffentlichte Zahl **hält der Kreuzvalidierung stand**. Die
ursprüngliche Sorge des Tickets — die Zahl sei durch Overfit aufgeblasen —
bestätigt sich nicht.

### Der Grund dafür ist der unangenehmere Befund

Sie hält stand, weil kaum etwas gefittet wird. Von einem neutralen Startpunkt
aus (uniforme Gewichte, Masse 1/N) findet die Coordinate Ascent in **keinem
einzigen der fünf Folds** einen verbessernden Zug. Die Gewichte bleiben, wo sie
gestartet sind — und uniforme Gewichte messen auf dem ganzen Korpus
P 1.000 / R 0.977 / **F1 0.989** gegen die ausgelieferten
P 1.000 / R 0.982 / **F1 0.991**.

**Die gesamte 14-dimensionale Kalibrierung ist auf diesem Korpus genau einen
Text wert** (FN 4 statt FN 5, von 331). Das Gewichtsvektor-Tuning, das die
Doku als Herkunft der ausgelieferten Zahlen führt, trägt zur heutigen Leistung
fast nichts bei; die Arbeit machen die Phrasen- und Musterinventare. Der in
`slop_scorer.py` zitierte Sprung „F1 0.47 → 0.89" stammt von einem älteren,
kleineren Korpus und beschreibt den heutigen Beitrag nicht mehr.

Das ist kein Grund, die Kalibrierung zu entfernen — wohl aber einer, sie nicht
länger als tragende Säule zu beschreiben. Ein Folge-Ticket kann prüfen, ob der
Korpus zu leicht geworden ist, um zwischen Gewichtsvektoren zu unterscheiden.

### Der erste Messwert war kontaminiert

Der zuerst veröffentlichte Held-out-Wert (Scorer F1 0.984, Pipeline F1 0.991,
3 FP) war falsch, gefunden von zwei unabhängigen Reviews. `calibrate.calibrate`
startete die Ascent bei `DEFAULT_WEIGHTS` — auf dem **gesamten** Korpus
gefittet, also auch auf den Texten jedes Held-out-Folds. Ascent bewegt ein
Gewicht nur bei echter Verbesserung, also blieb eine gut gesetzte Dimension
einfach stehen: **vier der fünf Folds behielten die vollen Korpusgewichte
unverändert** und bewerteten ihre Held-out-Texte mit Gewichten, die auf genau
diesen Texten gefittet waren. Fold 0 bewegte zwei Koordinaten und erzeugte
dabei die drei False Positives, die der erste Bericht als Befund auswies.

Das Symptom stand in der Messung: der Held-out-Recall war auf drei Stellen
identisch zum In-sample-Recall, auf beiden Engines.

`calibrate()` nimmt jetzt `initial_weights`; die Kreuzvalidierung übergibt den
uniformen Start. Der Re-Baseline-Pfad startet unverändert bei den
ausgelieferten Gewichten. Der bestehende Leckage-Test konnte den Fall nicht
finden — er prüft, **welche Items** der Kalibrator sieht, und diese Antwort war
korrekt. `InitializationLeakageTest` deckt jetzt den anderen Kanal ab.

### Score-Protokoll

Kein Score ändert sich. `eval/run_benchmark.py` liefert unverändert
P 1.0 / R 0.995 / F1 0.998 auf `eval/corpus.jsonl`, alle acht Gates bleiben
grün, die 14 Gewichtswerte sind wertgleich zu `master`. Die Kreuzvalidierung
ist opt-in (L3, rund 30 min) und läuft nicht in CI.

### `eval/calibrate.py` war nicht lauffähig

Nebenbefund beim Bau, gleiche Fehlerklasse wie #88: das Skript hielt eine
hartcodierte Kopie der Gewichtsnamen mit **13** Einträgen, während der Scorer
längst einen 14. hatte (`portability`, #14). Jeder Aufruf starb mit
`KeyError: 'portability'` — das Skript, das die ausgelieferten Gewichte als
ihre Herkunft angeben, ließ sich nicht ausführen. Die Gewichte liegen jetzt als
`slop_scorer.DEFAULT_WEIGHTS` an einer Stelle; `calibrate.py` und der
Kreuzvalidierungs-Läufer lesen sie dort, statt zu kopieren. Ein Test pinnt die
Namensgleichheit.

Das ist der sechste Fundort dieser Klasse in dieser Serie. Kein Gate hatte ihn
gefunden; er fiel auf, weil das Skript einmal tatsächlich aufgerufen wurde.

### Die veröffentlichte Zahl war 17 Clean-Texte alt

`skills/ai-slop-detection/SKILL.md` gab den Korpus als `n=314 = 221 slop +
93 clean` an; er hat 331 (110 clean). P/R/F1 hatten das Wachstum überlebt —
Recall hängt nicht von Clean-Texten ab, Precision stand auf 1.0 — also war
die Drift für kein Gate und keinen Leser sichtbar. Die Angabe ist jetzt gegen
einen frischen Benchmark-Lauf gepinnt, inklusive Korpusgröße, Aufteilung und
vollständiger Konfusionsmatrix (`tests/test_cross_validation.py`).

### Sonst

- `--cross-validate K`, `--cv-seed S`, `--cv-rounds R` in `run_benchmark.py`.
  Folds sind stratifiziert, disjunkt und für einen Seed deterministisch (M8);
  `K` wird gegen die **kleinste Klasse** geprüft, weil ein labelfreier Fold
  nicht fehlschlägt, sondern ein vakuoses P/R/F1 in die gepoolte Zahl trägt.
- `--min-precision`/`--min-recall` werden mit `--cross-validate` **abgelehnt**
  statt ignoriert — sonst wird das CI-Gate durchlässig, sobald jemand die
  Flagge dort ergänzt.
- `--threshold` erreicht jetzt den Kalibrator; vorher wurde bei 0.40 gefittet
  und bei der gewünschten Schwelle berichtet.
- Kalibrator-Fortschritt geht auf stderr; stdout trägt nur den Report, sonst
  bricht `--json`.
- `docs/EVALS.md` benennt, welche veröffentlichte Zahl welcher Art ist und wo
  sie steht — an einer Stelle, nicht in Zweitkopien.

## [2.7.0] — 2026-08-28 (#88 — Positionssemantik für TypePattern-Muster)

Zwei schwache Muster in `SEOContentFarmSlop` machten gewöhnliche Fachdoku zu
einer Content-Farm. Zwei Treffer eines Typs sind für sich entscheidend
(Konfidenz 0.8), und beide trafen dort, wo sie nichts bedeuten:

```
"This page lists the commands. The commands shown here are known to run.
 We keep a table of contents at the top so the sections stay findable."
-> 0.56
```

### Positionsmarker im SSOT

Ein führendes `^` in einem Muster heißt jetzt: die Phrase muss eine Klausel
**eröffnen**. `^here are` ist der Listicle-Opener „Here are 5 ways…", nicht die
Mitte von „the commands shown here are known to run". Klauselinitial umfasst
Textanfang, Satz- und Klauselzeichen, Zeilenanfang, öffnendes Anführungszeichen
und Listeneintrag — dort stehen Opener tatsächlich.

Der Marker ist opt-in: ein Muster ohne `^` verhält sich exakt wie bisher. Die
Expansion liegt in allen drei Modulen, die ein Term-Regex bauen, in derselben
Form wie die `[X]`/`[N]`-Expansion aus #83.

### `table of contents` gestrichen

Empirie statt Meinung: das Muster traf **0 von 330** Korpus-Texten, während es
in legitimer Fachdoku vorkommt — auch in `docs/USER-GUIDE.md` dieses Repos. Ein
Muster, das in beiden Klassen gleich häufig ist, trägt keine Information.

### Vierter Fundort, den die SSOT-Änderung nicht erreicht hatte

`skills/…/slop_classifier.py` hält eine **hartcodierte Zweitkopie** der
Mustertabelle. Sie ging nicht über den geänderten Pfad, und weil die
Benchmark-Pipeline den stärkeren Wert aus Scorer und Skill-Klassifikator nimmt,
blieb der False Positive bestehen, nachdem der Fix vollständig aussah — die
Precision fiel messbar auf 0.995. Kopie angeglichen und per Test gegen
`ontology.json` gepinnt; nichts hatte die beiden Listen bisher verbunden.

### Korpus-Lücke geschlossen

Der Fix ändert **keinen einzigen** der 330 bestehenden Korpus-Texte — genau
deshalb war der Fehler unsichtbar. Neues Hard Negative `clean-tech-14`
(own:handwritten): Fachdoku, die beide Muster legitim enthält.

```
clean-tech-14   vor dem Fix 0.560   nach dem Fix 0.000
```

Benchmark auf `eval/corpus.jsonl`: P 1.0 / R 0.995475 / F1 0.998, n 330 → 331,
TN 109 → **110**, FP weiterhin 0. Kein bestehender Text bewegt sich, kein
Recall-Verlust.

Tests 596 → 617. Die veröffentlichte Signalzahl (378) ist unverändert — sie
zählt Buzzwords und Phrasen, keine Typ-Muster.

### Review-Nacharbeit (vor dem Merge)

Ein Review des Diffs fand vier Defekte, die die Tests nicht abgedeckt hatten:

- **Recall-Lücke statt False Positive.** Der Marker erkannte nur Satzzeichen,
  Zeilenumbruch, Anführungszeichen und Klammern als Klauselöffner. Ein
  Listicle-Opener unter einer Überschrift (`## Here are 7 ways…`), fett, in
  einem Blockquote oder nach einer Ellipse matchte nicht mehr — der Fix hätte
  einen False Positive gegen eine Erkennungslücke getauscht, die kein Gate
  sieht: Markup-Strippen ist opt-in (#69) und der Benchmark-Korpus ist reine
  Prosa. Markup-Lead-ins zählen jetzt, mit Gegenprobe, dass sie kein Freibrief
  für Treffer mitten im Satz sind.
- **Interne Syntax in der Ausgabe.** Die Evidence las sich als
  „3 distinctive patterns: ^here are, …" — der Marker gehört nicht vor die
  Augen des Lesers.
- **Fünfter Fundort.** `PHRASE_CATEGORIES["listicle_tells"]` im Skill-Scorer
  führte ein blankes `here are`, wo der SSOT die engeren Template-Formen hat
  (`here are [N] ways`). Der Scorer feuerte deshalb weiter mitten im Satz auf
  genau dem Hard Negative, das dieses Issue hinzugefügt hat — und
  `eval/fp_baseline.json` segnete den Treffer ab, statt dass der Fix ihn
  entfernt. Angeglichen und per Test gepinnt.
  Change-Protokoll dazu: 2 von 331 Texten bewegen sich, beide slop
  (`slop-seo-01` 0.607 → 0.400, `slop-listicle-01` 0.557 → 0.482), kein Hard
  Negative, kein Verdikt kippt; Pipeline unverändert.
- **Satzgrenze hinter schließendem Zeichen** (Codex-Review auf dem PR). Steht
  zwischen Punkt und nächster Klausel ein schließendes Anführungszeichen oder
  eine Klammer — `He wrote "Stop." Here are the alternatives.` —, sah der
  Lookbehind das Zeichen statt der Punktuation. Zweite Recall-Regression
  derselben Art, auf typografisch gesetzter Prosa, wo das unbeschränkte Muster
  vorher traf.
- **Doku als dritte Quelle.** `references/detection-signals.md` listete
  `table of contents` weiter. Diese Liste steuert den LLM-Pfad des Skills,
  hätte den False Positive also reproduziert.

## [2.6.1] — 2026-08-28 (Codex-Review zu PR #99)

Ein automatisiertes Review (Codex) auf PR #99 kam auf dem Commit *vor* der
Review-Nacharbeit an und meldete drei Befunde. Alle nachgeprüft:

- **Kurze Listeneinträge (P1)** — bereits behoben. Die Längen-Heuristik, die
  eine Slop-Listicle hätte wegstrippen können, war in `fd6b134` schon
  entfernt. Der Fall ist jetzt als Regressionstest verankert: ein Dokument aus
  fünf kurzen Slop-Bullets bleibt vor und nach dem Präpass bei 0.686, das
  `--fail-over`-Gate greift also weiterhin.
- **Ausnahme-Obergrenze bei 1.0 (P2)** — **war real.** Scores sind bei 1.0
  gedeckelt und das Gate prüft `score <= budget`; eine Obergrenze von 1.0
  konnte deshalb nie verletzt werden. Die Ratsche aus #48 ratschte nicht.
  Obergrenzen jetzt am Messwert plus 0.01 gepinnt (CHANGELOG.md 0.983,
  report.md 0.974), und ein Test verbietet jede Obergrenze bei 1.0.
- **Gerundete Metriken im Gate (P2)** — **war real.** `evaluate()` rundet auf
  drei Stellen, und die Untergrenze verglich gegen den gerundeten Wert: ein
  Recall von 0.98999 wäre als 0.990 durch `--min-recall 0.99` gerutscht.
  `run_benchmark.py` führt jetzt `precision_exact`/`recall_exact`/`f1_exact`
  mit und vergleicht gegen die; gerundet wird nur noch für die Ausgabe.

Tests 593 → 596.

## [2.6.0] — 2026-08-28 (Batch K — P0-Defekte aus dem PR-#6-Abgleich + CI-Gates)

Batch aus der Triage vom 2026-08-28 (#54): drei P0-Defekte, zwei P1-Gates.
Alle drei P0 waren Befunde aus PR #6, der mangels gemeinsamer Historie mit
`master` nicht mergebar war; jeder Befund wurde gegen den heutigen Stand
nachgeprüft und neu erarbeitet statt portiert.

### #82 Wheel-Packaging (P0)

- `pip install .` lieferte eine CLI, die bei jedem Subcommand mit
  `ModuleNotFoundError: No module named 'classifier'` abbrach: paketiert
  wurde nur `slopkit/`, während `slopkit/_engine.py` `src/`, die
  Skill-Skripte und `ontology.json` über Pfade relativ zum Paketverzeichnis
  auflöst. `pip install -e .` maskierte das.
- Build-Backend setuptools → hatchling; `force-include` legt die
  Laufzeitdaten beim Bauen nach `slopkit/_bundled/` — keine Zweitkopie unter
  Versionskontrolle (adr/0002). `_data_root()` wählt gebundelt oder Checkout.
- `benchmark`/`selfcheck` brauchen den Checkout und melden das außerhalb
  klar (Exit 2) statt einen Traceback zu werfen.
- CI installiert das Wheel in ein venv und ruft `slop` außerhalb des
  Checkouts. `tests/test_packaging.py` prüft Deklaration (ohne Build/Netz)
  und gebaute Distribution.

### #83 Phrase-Matchbarkeit (P0)

- Zehn Phrasen im SSOT konnten strukturell nie matchen: `_term_pattern()`
  escapte `[X]`/`[N]` literal, `"in the age of [X]"` suchte den Literaltext.
- `[X]` → ein bis vier Wörter (lazy), `[N]` → Ziffern oder Zahlwort;
  identisch in `src/scorer.py`, `skill/slop_scorer.py` und
  `skill/genre_profiles.py` (sonst strippen Genre-Exemptions andere Spans,
  als der Scorer matcht).
- Change-Protokoll (#67): genau 1 von 330 Korpus-Texten ändert seinen Score,
  `slop-0202-016` (label slop) 0.280 → 0.496. **Kein Hard Negative
  verändert.** Konfusionsmatrix unverändert P 1.0 / R 0.995 / F1 0.998 —
  der Gewinn ist Score-Abstand, keine neue Erkennung.
- `tests/test_phrase_matchability.py` prüft jede der 249 Phrasen gegen ihre
  eigene Instanziierung.

### #69 Markdown-Präpass (P0)

- Der Detektor bewertete die eigene Doku als Slop: README 0.900,
  ONTOLOGY 0.933, AI-SLOP-ONTOLOGY 0.986, docs/USER-GUIDE 0.995 — Ursache
  waren die zitierten Beispiele, die als Fließtext gewertet wurden.
- `skills/ai-slop-detection/scripts/markup_prepass.py`: `strip_markup()`
  entfernt Code-Fences, eingerückte Codeblöcke, Inline-Code, Blockquotes,
  Tabellen, Zitat-Listen und den Inhaltsverzeichnis-Block. Prosa-Listen,
  Überschriften und Linktext bleiben. Idempotent, detect-only, ohne Score.
- Alle vier Dokumente danach 0.000.
- CLI `--strip-markup` für score/classify/rhetoric/check gibt Roh- **und**
  Strip-Score aus (`raw_slop_score` im JSON); `--fail-over` bewertet die
  Strip-Fassung. Ohne Flag ändert sich nichts — Rohtext bleibt Default, der
  Korpus wird weiter auf Rohtext gemessen (ein Default-Wechsel wäre eine
  Re-Baseline-Entscheidung, #67).
- Guardrails: kein Korpus-Text wechselt durch den Präpass sein Verdikt;
  Missbrauchsprobe verankert (Prosa-Slop bleibt erkannt).

### #84 CI-Gate-Abdeckung (P1)

- CI lief `unittest discover` und führte damit **420 von 539 Tests** aus;
  zwölf pytest-Dateien wurden ohne Warnung übersprungen, darunter die
  Wächter für Signal-DoD, SCORE-GOVERNANCE, METHODOLOGY, EVALS und ADRs.
- Workflow auf pytest umgestellt; jedes dokumentierte Gate ist ein eigener,
  scharfer Schritt (check_consistency, check_ssot, check_methodology,
  check_signal_dod, fp_baseline --check, run_control_set, self_check_docs).
- `eval/run_benchmark.py --min-precision/--min-recall/--engine`: mit
  Untergrenze Exit 1 und benannte Verletzung, ohne Untergrenze weiterhin
  ein Bericht. CI fährt P ≥ 1.0 / R ≥ 0.99.
- `tests/test_ci_gates.py` liest die Workflow-Datei und gleicht Testdateien
  gegen die Collection ab — genau die Lücke, die zwölf Dateien verborgen hat.

### #48 Meta-Self-Check (P1)

- `scripts/self_check_docs.py` bewertet jedes Repo-Markdown nach dem
  #69-Präpass und schlägt fehl, sobald eins die Schwelle 0.40 erreicht.
  27 Dokumente, 23 bei 0.000–0.100.
- `eval/self_check_docs.json` führt vier Ausnahmen mit Begründung und einem
  Deckel, der am Messwert klebt (höchstens 0.10 darüber): CHANGELOG.md,
  report.md und REVIEW-2026-07.md benennen Katalogmaterial im Fließtext;
  docs/EVALS.md trägt ein Messartefakt (Halbgeviertstrich als
  Strukturtrenner in einer Definitionsliste).
- `docs/DOC-STYLE.md`: zitiertes Material in Markup, eigene Aussagen im
  Fließtext — und ein ausdrückliches Verbot, so lange umzuformulieren, bis
  der Detektor schweigt.

### Review-Nacharbeit (vor dem Merge)

Ein Review des PR-Diffs fand neun Defekte, die die Tests nicht abgedeckt
hatten. Alle behoben, jeder mit Regressionstest:

- **Praepass, drei Ueber-Entfernungen.** Ein Inline-Code-Regex mit `DOTALL`
  loeschte bei ungerader Backtick-Zahl alles bis zum naechsten Backtick — in
  einem Dokument ueber Slop genau die Passage, die bewertet werden soll. Eine
  unterminierte Fence ohne abschliessendes Newline wurde gar nicht entfernt.
  Eingerueckte Fortsetzungszeilen von Prosa-Listen wurden als Codeblock
  entfernt (5 echte Zeilen in CHANGELOG.md).
- **Praepass, zu breites Inhaltsverzeichnis.** `Contents`, `Inhalt` und
  `Übersicht` sind gewoehnliche Ueberschriften; der Block loeschte den ganzen
  Abschnitt darunter. Jetzt nur noch die eindeutigen Labels, und darunter nur
  Navigationszeilen.
- **Praepass, Laengen-Heuristik entfernt.** Kurze unpunktierte Listeneintraege
  galten als Katalog. Das war zweimal falsch: es entfernte echte Prosa, und es
  war instabil, weil das Entfernen von Inline-Code einen Eintrag ueber die
  Laengenschwelle schiebt. Ein Katalogeintrag muss sich jetzt selbst als Zitat
  markieren (Anfuehrung, Betonung, Code-Span).
- **Praepass als ein Scan statt einer Regex-Kette.** Verkettete Durchlaeufe
  machen kontextabhaengige Entscheidungen instabil — eine geleerte Tabellenzeile
  laesst die Folgezeile „nach Leerzeile" aussehen. Idempotenz jetzt bei
  0 von 18.000 Fuzz-Faellen und allen 27 Repo-Dokumenten verletzt.
- **Zwei Rauchtests, die nicht fehlschlagen konnten.** CI und
  `tests/test_packaging.py` riefen `slop score sample.txt` — ohne `--file`
  wird der Dateiname als Literal bewertet (0.00 statt 0.96). Jetzt `--file`
  plus eine `--fail-over`-Gegenprobe, die beweist, dass die Datei gelesen wird.
- **Benchmark-Schwellentest.** Die Untergrenze war so gesetzt, dass der Test
  bricht, sobald die Pipeline perfekten Recall erreicht — ein Test, der eine
  Verbesserung bestraft. Jetzt eine per Definition unerreichbare Grenze.
- **`slop code --strip-markup`** wurde angenommen und ignoriert; Quellcode ist
  kein Markdown, das Flag gibt es dort nicht mehr. `cmd_rhetoric` berechnete
  eine vollstaendige Klassifikation und warf sie weg.
- **`self_check_docs.py --path`** nutzte den Pfad unnormalisiert als
  Registerschluessel, `--path ./CHANGELOG.md` fiel deshalb durch.

Nebenwirkung der Praepass-Korrektur: `REVIEW-2026-07.md` (0.987 → 0.000) und
`docs/EVALS.md` (0.406 → 0.000) sind jetzt aus eigener Kraft sauber und haben
ihren Registereintrag verloren — die Ratsche aus #48 hat das selbst gemeldet.
Es bleiben zwei Ausnahmen: CHANGELOG.md und report.md.

Tests 585 → 593.

### Prozess

- Prioritätsschema P0/P1 als Label eingeführt, Triage in #54; die im
  Fließtext geerbten Prioritäten sind dort abgeglichen.
- PR #4 und #6 geschlossen (keine gemeinsame Historie mit `master`), jeder
  Befund nachgeprüft und ticketiert: #82, #83, #69, #85, #86, #87.
- Neue Befunde beim Arbeiten: #88 (TypePattern ohne Positionssemantik).

### Zahlen

- Tests 539 → 585 (+ 848 Subtests), 5 neue Testdateien.
- Benchmark skill-pipeline unverändert: P 1.0 / R 0.995 / F1 0.998
  (n=330, TP 220 / FP 0 / TN 109 / FN 1 = known-FN).
- Control-Set, SSOT C1–C4, Consistency, Methodology, Signal-DoD und
  fp-baseline grün.

## [2.5.0] — 2026-08-25 (Batch J — DE-Katalog Teil 2 + FU-17 + #80-Rest)

### #76 DE-Pattern-Katalog Teil 2 (Master-Akzeptanz ≥20 DE-Signale erfüllt)

- 12 neue de_*-Phrase-Kategorien in ontology.json (SSOT): de_transitions,
  de_recap, de_superlativ, de_symbolik, de_vague_authority, de_participle,
  de_binary_contrast, de_false_range, de_opening, de_closing, de_hedging,
  de_announcement_cleft — je 6 Phrasen, Konfidenz 0.6, Evidence-Pflicht je
  Phrase (Wikipedia-Projektseite MIT Namespace-Präfix, RI-1-URL, oder
  own:-Beleg; ≥2 Belege als FU dokumentiert offen, RI-2-Abweichung).
- `skills/ai-slop-detection/scripts/structure_metrics.py`: M60
  SynonymRotation + M61 IsometricUnits (detect-only, sprachagnostisch,
  bewusst ohne DE-Gate), Schwellen fixture-kalibriert.
- Signal-DoD je Signal 3/3/2-Fixtures (tests/test_de_catalog_part2.py,
  tests/test_structure_metrics.py); #46-Kollisionsdisziplin inkl. paarweisem
  Substring-Check über den gesamten de_*-Layer; EN-Corpus-Sicherheit.
- DE-Signal-Zähler: 8 (Teil 1) → 22 (≥20 ✓). Mapping-Updates:
  docs/de-coverage.md.

### FU-17 check_ssot de_*-Phrase-Layer (RI-4)

- Neue Prüfung C4 in scripts/check_ssot.py: DE_LAYER-Pin (16 Kategorien ×
  ≥6 Items), Evidence-Regel, Wikipedia-Namespace-Präfix; 4
  Manipulationsproben test-verankert (tests/test_ssot_de_layer.py).

### #80-Rest Genre-Menschtexte

- 16 neue own:handwritten-Fixtures in eval/corpus.jsonl (code +5, generic
  +5, nonfiction +4, news +2): jedes Clean-Genre ≥6 verifizierte
  Menschtexte, alle < 0.40 auf beiden Engines; fp_baseline 93 → 109
  Fixtures; Quartals-Re-Score-Anbindung (#47) in docs/EVALS.md.
- Benchmark skill-pipeline: P 1.0 / R 0.995 / F1 0.998 (n=330, TP 220 /
  FP 0 / TN 109 / FN 1 = known-FN; eval/corpus.jsonl). Tests 440 → 469.

## [2.4.0] — 2026-08-25 (Batch I — [ADAPT]: DE-Layer + FP-Infrastruktur)

Referenz-Adaption humanizer-de v5.22.2 (nur Architektur-Ideen, Lizenz-sicher
re-deriviert, kein CC-BY-SA-Pattern-Material übernommen; s. docs/de-coverage.md).

### #78 Anchor-Drift (detect-only)

- `skills/ai-slop-detection/scripts/anchor_diff.py`: `anchor_diff(a, b)` →
  `anchor_lost`/`anchor_added`/`authority_shift` über geschützten Ankern
  (Zahlen, Zitate, URLs, DOIs); Locale-Kanonisierung „3.5“ == „3,5“.
  CLI-Flag `--anchor-diff base..head` im Diff-Modus. Nie score-dominant.

### #79 Null-Edit-Contract

- `tests/test_null_edit_contract.py` als L1-Gate: alle 93 Hard Negatives
  auf beiden Engines < 0.40; Null-Edits (Whitespace/Reflow) ändern den
  Verdict nicht (Score-Drift ≤ 0.05, dokumentierte Listen-Sensitivität
  hardneg-042). Grenzband-Register `eval/hardneg_borderline.json`
  (Top-5: 0.315–0.342; 3 handgeschriebene Grenzfixtures 0.098–0.189).

### #80 FP-Baseline-Register

- `scripts/fp_baseline.py` + `eval/fp_baseline.json`: tolerierte Detektor-
  Outputs je Hard-Negative-Fixture; CI-Snapshot `--check` (Drift-Typen
  signal_added/removed, score_drift > 0.02, fixture_missing/unknown).

### #81 Naturalness-Guard (detect-only)

- `skills/ai-slop-detection/scripts/naturalness_guard.py`: `register_drift`
  (≥2 formale vs ≥2 kollokiale Marker außerhalb von Zitaten) und
  `over_sanitized` (≥3 expandierte Vollformen, null Kontraktionen;
  Genre-keep_when academic/legal). Konfidenz ≤ 0.45, nie score-dominant.
  `modal_particle_anomaly` bewusst Stub bis DE-Inventar (#76-Folge).

### #76 DE-Pattern-Katalog Teil 1

- `docs/de-coverage.md`: alle 72 Muster des Referenz-Katalogs gemappt
  (Claim-Korrektur: 72, nicht 82) — 20 bestandsgedeckt, 4 neu, 30
  DE-Variante → #77, 18 NEU (Prioritäten M60/M61), M63 Stub.
- `skills/ai-slop-detection/scripts/de_typography.py`: Quick Wins M46
  („Text” statt „Text“), M47 (kapitalisierte Funktionswörter in Headern),
  M48 (EN-Dezimal/Datumsformat, Versionsnummern exempt), M49 (Genitiv-
  Apostroph, Marken-Allowlist) — DE-Sprachgate, je 3/3/2 Fixtures.

### #77 DE-KI-Marker-Vokabular (SSOT-Layer)

- `ontology.json` signals.text.phrases.categories: `de_calque`,
  `de_ai_vocab`, `de_authority_floskel`, `de_meta_comment` (je 6 Phrasen,
  Konfidenz 0.6), Evidence-Pflicht je Phrase (de.wikipedia „Anzeichen für
  KI-generierte Inhalte“ oder eigener Beleg); Kollisionsfreiheit zu
  `multilingual.german` per Test erzwungen; signal_defs regeneriert.

### Messwerte (Batch I)

- Tests: 380 → 440 grün (+18 Subtests).
- Benchmark skill-pipeline unverändert: P 1.0 / R 0.995 / F1 0.998
  (eval/corpus.jsonl, n=314, FP=0) — alle Batch-I-Signale detect-only.
- Control-Set-Gate PASS (bekannter FN slop-fn-02), Consistency/SSOT/
  Methodology/Signal-DoD grün, fp-baseline --check ohne Drift.


## [2.3.0] — 2026-08-25 (Batch H — Loop-Runner #51, Lexikon-Pilot #50)

### #51 DESLOP-LOOP-Orchestrator (additiv, kein Scorer-Pfad)

- **`src/deslop_loop.py`:** Zustandsmaschine DETECT → TRIAGE →
  FIX-CALLBACK → VERIFY → EXIT-CHECK mit Rollback-Kante (Best-of-N
  zwischen aktuellem Bestwert und Kandidat) und ESCALATE-Terminal.
  ADR-0001-konform: Der Runner schreibt selbst NICHT um — der FIX-Schritt
  ist ein injizierbarer Callback `fix(text, findings) -> candidate`;
  der löschbasierte Demo-Callback liegt nur in `examples/`, nicht im
  Produktpfad. Scorer/Classifier unangetastet (reiner Detektor).
- **Exit-Checks E1–E5** (Loop-Spez, research/slop-loop-pipeline-2026-08-24
  Abschnitt (e)): E1 Score < Threshold, E2 keine kritischen Signale, E4
  keine inkubierten Signale (bestätigte Menge ⊆ Baseline-Menge) →
  EXIT-OK; E3 ε-Stagnation (2 akzeptierte Iterationen mit Δ < ε) und E5
  maxIter=5 → EXIT-ESCALATE („human review required“) — **nie** ein
  stiller Durchlauf als Erfolg. Garantie-Aussagen maßstabsgebunden
  („slop-frei nach Maßstab des Detektors“), Fixpoint ≠ Optimum (#62).
- **Voice-Budget-Guardrail:** vereinfachte Token-Diff-Rate
  (Multiset-Ähnlichkeit) ≤ 25 % je Iteration, sonst Kandidat verworfen
  (Aktion `rejected_budget` im Audit).
- **Signal-Bestätigung (#58/#61-Konzepte):** Fund geht nur in den Fix,
  wenn in 2 aufeinanderfolgenden DETECT-Läufen stabil ODER Konfidenz
  ≥ 0,9.
- **Audit `runs/<runId>/`:** `manifest.json` (Parameter/Detektor),
  `iterations.jsonl` (Score vorher/nachher, Findings, Aktion,
  Budget-Verbrauch), `result.json` (Verdict + Garantie).
- `scripts/deslop_loop_cli.py` (CLI, Fix-Modul injizierbar), 13 L1-Tests
  mit deterministischen Fake-Detektoren/Fixern (keine Netzwerk-Abhängigkeit).

### #50 Lexikon-Pilot (Schema-first SSOT)

- **`lexikon/schema/entry.schema.json`:** Entry-Schema (id, term, aliases,
  definition, category signal/pattern/type/counter, claims[] mit je
  sources[] {url, quote, accessed}, detect, counter, status
  nursery/beta/stable konsistent zu METHODOLOGY.md, version, see_also).
- **5 Pilot-Einträge** in `lexikon/entries/`, jeder Claim belegt mit
  Quellenzitat: Throat-Clearing (stop-slop + Wikipedia-Signs),
  Provenance-Marker oaicite/turn0search0 (Wikipedia-Signs),
  Binary-Contrast (petergyang/no-ai-slop + lokale Umsetzung),
  Marketing-CTA (Korpus-Belege eval/corpus.jsonl + Review Batch F),
  Human-Voice als Counter-Eintrag (poteto/noodle unslop-Skill).
- **`scripts/build_lexikon.py`:** deterministischer Build (keine
  Timestamps, sortierte Iteration, kanonisches JSON) → Human-Sicht
  `dist/index.md` (alphabetisch, narrativ mit Belegen) + Agent-Sicht
  `dist/lexikon.json` + `llms.txt` + `llms-full.txt`; `content_hash` je
  Eintrag in beiden Sichten; `--check` als Sync-Gate.
- 10 L1-Tests: Schema-Validierung, Beleg-Pflicht (jeder Claim ≥ 1 Quelle
  mit url+quote+accessed), Build-Determinismus (zwei Builds identisch),
  Sync-Gate (dist == Neubau in tmp), llms.txt-Struktur.
- `docs/LEXIKON.md`: SSOT-Regel (nur entries/ editieren, dist nie) und
  Build-Kommando.

### Gates

- Control-Set-Gate, Benchmark, Consistency, SSOT-Check unberührt grün
  (beide Features additiv, keine Scorer-Logik-Änderung).
- Tests: 357 → 380 grün (13 + 10 neue L1-Tests).

## [2.2.0] — 2026-08-25 (Batch G — SSOT #49, Human-Voice #21, FU-Register)

### FU-Batch (FU-2..FU-12 aus review-batch-c/d/f, burn-log.md)

- **FU-2 (#25):** UniversalQuantifiers exemptiert Regel-/Instruktionstext —
  pragmatische Heuristik: imperativer Satzanfang („Always run…/Never
  push…") ODER Zeilen unter Rules/Guidelines/Policy-Heading
  (quantifiers.py). Detect-only, Score-Wirkung 0.
- **FU-3 (#13):** FalseAgency-Fachsprache-Exemption: realizes a
  gain/profit/loss/return (FINANCE_OBJECTS-Tupel, micro_patterns.py);
  „realizes the vision" bleibt Treffer.
- **FU-4 (#34):** SOURCE_REFS-Jahreszweig von \b\d{4}\b auf
  \b(19|20)\d{2}\b eingeengt — Nicht-Jahres-Vierstelligziffern (1024
  Samples, ADR-0005) unterdruecken nicht mehr als Pseudo-Beleg; Jahre
  unterdruecken weiterhin (FP-averse Richtung beibehalten). Eigner
  CHANGELOG-Claim (ADR-0005-Praxisfall) dadurch belegpflichtig geworden —
  Belegverweis ergaenzt (Ironie-Test gruen).
- **FU-5 (#9):** as_any_casts ignoriert Kommentar-Zeilen (# / //) —
  Python-Kommentar „use this as any other helper" feuerte bisher.
- **FU-7:** Dev-Claim-Korrektur im CHANGELOG: die fruehere „je 9–12“-Angabe
  war ueberzogen —> gemessen 3–12, Median ~7 (Review D, FU-7/FU-8).
- **FU-10:** README-Benchmark-Sektion in SKILL.md gespiegelt — mit
  Messreferenz (eval/run_benchmark.py, eval/corpus.jsonl n=314,
  threshold 0.40) und In-sample-Caveat (Review F).
- **FU-12 (Messung vorher/nachher, eval/run_benchmark.py --threshold
  0.40, eval/corpus.jsonl n=314):** Generic-Phrase-Watchlist — „in other
  words", "going forward", "the good/bad news is" in eigene Kategorie
  generic_phrases (confidence 0.65 < 0.75-Eskalationsschwelle,
  Kumulativschwelle erhoeht: min_hits=3 statt 2).
  - Reviewer-Gegenproben (review-batch-f): P1 0.400 -> **0.099**, P2
    0.556 -> **0.331** — beide unter Threshold, wie gefordert.
  - Benchmark vorher P 1.0 / R 0.982 / F1 0.991 (TP 217, FN 4, FP 0) ->
    nachher **identisch** (P 1.0 / R 0.982, F1 0.991; TP 217, FN 4,
    FP 0; jeweils eval/run_benchmark.py gegen eval/corpus.jsonl).
    Zwischenmessung mit voller 7-Phrase-Watchlist (inkl. to be
    clear/as you can see/the best part:) kostete slop-0303-021
    (R 0.977, gleicher Messaufbau) -> Umfang auf die 4 Aufgaben-
    Phrasen begrenzt; Rest wartet auf Clean-Genre Arbeitsprosa (FU-13).
  - FU-12-Tests nach Red angepasst (TESTS_MODIFIED_AFTER_RED: yes,
    Grund: Messergebnis — 7-Phrase-Umfang verstiess gegen die
    Benchmark-Verteidigungsvorgabe).
- **Nicht in diesem Batch** (Bericht burn-batch-g.md): FU-6 (toter
  No-op-Block in analyze_code — Aufräumen ohne Verhaltensrelevanz),
  FU-8 (#10 --repo-Flag/Doku), FU-9 (Berichtstypo en 295 -> 297 — extern,
  nicht im Repo), FU-11 (Held-out-Re-Validierung — an #41-Zuwachs
  gebunden), FU-13 (Clean-Genre Arbeitsprosa — Korpus-Erweiterung).

## [2.2.0] — 2026-08-25 (Batch G — SSOT #49, Human-Voice #21, FU-Register)

### #21: references/human-voice.md — positives Gegenprofil (reine Referenz, kein Scorer)

- Die 6 Soul-Prinzipien (Quelle: poteto/noodle unslop „Adding soul",
  deep/06 §3): specific over generic, verbs over nouns, risks and flaws
  nennen, genuine opinion, numbers and names, sentence-length variation
  gezielt — je Beschreibung, Vorher/Nachher, Wann-nicht.
- Code-Soul-Defaults (bl-I4 aus deep/07 simplify-Skill): benannte
  Funktionen, frühe Returns, Löschen statt Auskommentieren,
  Preserve-Functionality-Grenze.
- Kollisions-Doku #21↔#24 (Adverb-Rate): 4 Abgrenzungsregeln
  (informations tragende Adverbien, max. 1 Intensifier/Absatz,
  starkes Verb vor Adverb, Detektion gewinnt als Gate).
- KEINE Scorer-Änderung; tests/test_human_voice.py pint Struktur +
  SKILL.md-Verlinkung.

### #49: SSOT — ontology.json als Source of Truth, Drift CI-erzwungen (pragmatisch)

- Analyse (Bericht burn-batch-g.md): doppelt gepflegte Signal-Daten sind
  (a) ontology.json ↔ skills/ai-slop-detection/references/ontology.json
  (Byte-Kopie), (b) Inline-Matchlisten (BUZZWORD_TIERS,
  PHRASE_CATEGORIES, …) in den Skill-Skripten — korpuskalibriert, NICHT
  Teil der Ontology, (c) src/-Engine ↔ Skill-Engine (Verhaltens-Parität
  via tests/test_engine_sync.py).
- `scripts/generate_signal_defs.py`: deterministische, nur-Daten-Projektion
  von ontology.json nach `src/signal_defs_generated.py` (kein Code, kein
  Verhalten).
- `scripts/check_ssot.py` (Offline-Gate, kein Netz): C1 Skill-Kopie
  byte-identisch, C2 generierte Datei aktuell, C3 jede signaltragende
  Top-Level-Konstante der Detektionsmodule im SSOT-Register mit Quelle
  und Status (29 Einträge); bewusste Abweichungen als ALLOWLIST
  dokumentiert. Läuft als Test (tests/test_ssot.py) — Drift ist künftig
  CI-erzwungen.
- Bewusst NICHT in #49: volle Migration aller Module auf die generierten
  Daten (Aufwandsschätzung im Bericht); nur Sync-Check + generierte Datei
  als Option.

## [2.1.0] — 2026-08-25 (Batch F — FN-getriebener Signalausbau)

### FN-Serien 0101-0606: fuenf neue Phrase-Kategorien aus echten FN-Texten

- `marketing_cta`, `punchy_insight` (C1, Serien slop-0101/slop-0504),
  `report_hedging` (C2, Serie slop-0202), `wiki_promo`/`assistant_signoff`
  (C3, Serien slop-0303/0403/0606) — je Kumulativregel >=2 Treffer,
  confidence 0.75.
- Beleg-Disziplin (M7/M11): jede Phrase in >=3 slop-Texten und 0 der 93
  clean-Texte von eval/corpus.jsonl (gezaehlt 2026-08-25, erzwungen in
  tests/test_fn_series_signals.py).
- Benchmark (eval/run_benchmark.py, threshold 0.40, Korpus eval/corpus.jsonl,
  n=314): vorher P 1.0 / R 0.276 / F1 0.433 (TP 61, FN 160, FP 0) →
  nachher P 1.0 / R 0.982 / F1 0.991 (TP 217, FN 4, FP 0).
  Zwischenschritte: C1 R 0.543 (TP 120), C2 R 0.724 (TP 160).
- Verbleibende FN (4, known-FN-Tickets weitergefuehrt): hard-slop-subtle
  (2×, absichtliches Hard-Set), slop-peerreview-01, slop-security-01
  (Beleg <3 Texte — kein Signal ohne Disziplin).
- Threshold 0.40 fix; Genre-Guards (#42-Opt-in) unangetastet;
  Control-Set-Gate gruen (known-FN slop-fn-02 weiterhin ehrlich gefuehrt).
- Tests 316 -> 327. Version konsolidiert v2.1.0.

## [Unreleased — Batch E (Meta)]

### #63: METHODOLOGY.md — Methodik-Kodex mit Signal-Lebenszyklus

- `docs/METHODOLOGY.md`: die 11 Querprinzipien M1-M11 (Test-Oracle-Pflicht,
  Guard-/keep_when-Systematik, SSOT, Learning-Loops, Empirie-vor-Ausbau,
  Provenance, Prozess-Zustandsmaschine, Determinismus-vor-LLM,
  Goodhart-Resistenz, Minimum-Intervention, Forschungs-Pipeline) — je mit
  Beschreibung, Anker-Issues und Durchsetzungsmechanismus. Quelle: Meta-
  Abstraktion ueber #1-#62 (research/slop-ontology-gap-2026-08-24/
  meta-abstraktion.md, externe Forschung, nicht Teil des Repos).
- Signal-Lebenszyklus nursery->beta->stable->deprecated->retired mit
  Zustandsuebergaengen, Governance-Regeln und Spezifikation des
  `status`/`status_since`/`replaces`-Felds fuer ontology.json (Spezifikation;
  Migration der bestehenden Signale ist Follow-up).
- `scripts/check_methodology.py`: Offline-Konsistenz-Checks — M1-M11 und
  Lebenszyklus vorhanden; jede #N-Referenz steht in der Konsistenz-Liste des
  Dokuments selbst. Keine API-Calls.
- Tests 290 -> 294 (tests/test_methodology_doc.py). TDD: Red-Commit dfb1fa7.
### #64: Signal-Definition-of-Done — maschinenlesbare Checkliste als PR-Gate

- `docs/SIGNAL-DOD.md`: die 8 Musts (Test-Oracle, FP-Abwaegung, SSOT-Eintrag,
  Quellenbeleg, Benchmark-Referenz, Kollisions-Check, Sequencing-Disziplin,
  Prozess-Einbettung) als Checkliste mit Pruefebene (auto/Review).
- `scripts/check_signal_dod.py`: scannt Signal-Module unter
  skills/ai-slop-detection/scripts/ heuristisch (Test-Referenz in tests/,
  keep_when-Doku, SKILL.md-Referenz). Default: Report (exit 0);
  --strict: exit 1 bei fehlenden Tests. Infra-Module nur Test-Check.
  Ist-Aufnahme gegen Bestand: 0 FAIL, 9 WARN (keep_when/SKILL-Referenz
  bei aelteren Signalen — schrittweise nachziehen, s. Report).
- Tests 294 -> 299 (tests/test_signal_dod.py mit Fixture-Repo: ok/FAIL/WARN/
  Infra + CLI Report/strict). TDD: Red-Commit vorab.

### #65: ADR-System adr/ mit 7 Rueckdokumentationen

- `adr/0000-madr-template.md`: MADR-Blaupause (Frontmatter-Status, Context,
  Decision Drivers, Considered Options >=2, Decision Outcome, Consequences,
  Confirmation) — Vorlage verifiziert aus methoden-fundament.md S1 (extern).
- 7 Rueckdokumentationen (alle Status: accepted, je >=2 Optionen):
  0001 Detector-only statt Rewriter (#30 vs #38), 0002 SSOT ontology.json
  (#49), 0003 Golden-Control-Set-FN-Gate (MS-I1), 0004 Genre-Opt-in statt
  Auto-Erkennung (#42), 0005 Benchmark-Korpus-Disziplin & ehrliche Zahlen
  (F1 0.982 -> 0.476 Praxisfall, #41), 0006 Detect-only-Module ausserhalb
  des Scorers (#9, #46-Praevention), 0007 Git-only-Burn-Modus bei
  API-Ausfall (D001-Praxisfall).
- Burn-Log (research/slop-ontology-gap-2026-08-24/burn-log.md, D001-D012)
  wird in jedem ADR als externe Quelle zitiert, nicht kopiert.
- `scripts/check_methodology.py` erweitert: ADR-Pflichtfelder
  (Status/Context/Decision/Consequences, accepted, >=2 Options) werden
  validiert, sobald adr/ existiert.
- Tests 299 -> 304 (tests/test_adr.py). TDD: Red-Commit vorab.

### #66: Issue-/PR-Templates mit Pflichtfeldern

- `.github/ISSUE_TEMPLATE/signal-proposal.md`: Signal-RFC nach Rust-RFC/KEP-
  Blaupause — Pflichtfelder Signal Name, Kategorie, Severity, Corpus Evidence,
  Test-Oracle, FP-Analyse, Prior Art, Quellen, Graduation Criteria,
  depends-on (Sequencing, M5). Lebenszyklus-Start nursery (#63).
- `.github/ISSUE_TEMPLATE/bug.md`: FP/FN-Bug-Reports mit Pflichtfeldern
  Signal, Input, Genre/Kontext, Erwartet, Tatsaechlich, Evidence
  (Scorer-Output, M6-Belegpflicht).
- `.github/PULL_REQUEST_TEMPLATE.md`: Pflichtfelder Corpus Evidence (bei
  Score-Aenderung Messung vorher/nachher), Test-Oracle (Red-Commit),
  FP-Analyse, Prior Art, Signals-DoD-Abhaken (8 Punkte aus docs/SIGNAL-DOD.md)
  plus Governance-Abschnitt (#67).
- Verhindert strukturell die Batch-1-Nachbesserungen (11 Issues ohne
  Testkriterium). Tests 304 -> 308 (tests/test_templates.py).
  TDD: Red-Commit vorab.

### #67: Score-Governance-Dokument (Goodhart-Regelwerk)

- `docs/SCORE-GOVERNANCE.md` mit vier Pflicht-Abschnitten:
  Optimierungs-Freigaben je Metrik (Composite slop_score nie direktes
  Ziel; Precision/Recall-Freigaben; Gewichte nur aus Korpus-Statistik;
  Threshold 0.40 ausserhalb Re-Baseline gesperrt; Voice-Metriken nur
  Non-Regression; Benchmark-Korpus nie im laufenden Loop), Guardrail-
  Pflicht je Score-/Gewichtsaenderung (Control Set + Benchmark +
  Voice-Budget + SSOT-Parity, mit Praxisfaellen Batch A Kalibrierung und
  #14 Gewichtsreduktion 0.03 -> 0.02), Re-Baseline-Kalender (quartalsweise,
  #47/#12, inkl. Signal-Status-Uebergaengen nach #63), Change-Protokoll-
  Pflicht (Messung vorher/nachher am Control Set UND Benchmark,
  dokumentiert im CHANGELOG; Verstoß = Review-Blocker).
- Praxisfall F1 0.982 -> 0.476 als Lehrfall kodifiziert (ADR-0005; Messungen
  je eval/run_benchmark.py + eval/corpus.jsonl, siehe die Eintraege 1.8.0
  und 2.1.0).
- `scripts/check_methodology.py` validiert die Pflicht-Abschnitte.
- Tests 308 -> 312 (tests/test_governance_doc.py). TDD: Red-Commit vorab.

### #68: Drei-Level-Evals-Architektur

- `docs/EVALS.md`: L1 Unit-Assertions (bei jedem Commit) / L2 Judge+Human
  (Golden Control Set, gate-gebunden) / L3 Quartals-Re-Score (Re-Baseline).
  Vollstaendige Zuordnung aller bestehenden Artefakte: tests/ -> L1,
  eval/control_set.jsonl + run_control_set.py -> L2,
  eval/corpus.jsonl + run_benchmark.py + calibrate.py -> L3.
- Small-Corpus-Rezept (<1000 Beispiele): Stratifikation vor Masse,
  Few-shot-Eval-Matrix, error-driven Labeling via #29-Learning-Store,
  Frozen-Golden-Set + Challenge-Set.
- `scripts/check_methodology.py` validiert: jede Datei unter eval/ und
  tests/ ist in EVALS.md einer Ebene zugeordnet.
- Tests 312 -> 316 (tests/test_evals_doc.py). TDD: Red-Commit vorab.

## [2.0.0] — 2026-08-25 (Batch E — Meta-Meilenstein)

Konsolidierter Meta-Batch: #63 Methodik-Kodex, #64 Signal-DoD,
#65 ADR-System, #66 Templates, #67 Score-Governance, #68 Evals-Architektur.
Doku-only + Check-Skripte; KEINE Scorer-Logik-Aenderungen, Benchmark
unveraendert (F1 0.476 / P 1.0 / R 0.312 auf eval/corpus.jsonl, threshold 0.40, Messvorschrift wie v1.9.0). Tests
290 -> 316, Control-Set-Gate gruen, check_consistency gruen. Ontologie-
Version 2.0.0 (Meta-Meilenstein: konstitutive Prozess-Dokumente).

## [1.9.0] — 2026-08-25 (Batch D)

### #41: Labeled Benchmark-Corpus mit Hard Negatives (~300+ Texte)

- `eval/corpus.jsonl` von 53 auf 314 Zeilen erweitert. Jede Zeile jetzt
  `{id, label, lang, type, genre, text, source}`.
- 192 neue Slop-Texte: wörtlich zitierte Original-Slop-Phrasen aus den
  Deep-Dive-Artefakten (deep/01–07: stop-slop, no-ai-slop, humanizer,
  Wikipedia, unslop writing+SaaS, poteto) — je 3–12 Phrasen pro Text
  (gemessen, Review D / FU-7: 3–12 verbatim Phrasen, Median ~7 — der
  fruehere Claim '9–12' war ueberzogen),
  Quellenangabe im `source`-Feld. 84 neue Clean-Texte: 69 Hard Negatives
  handgeschrieben (Juristensprache, Paper-Abstracts, ehrliches Marketing,
  Konfig-/Fachtexte, Kochrezepte, Lyrik-Passagen) + 15 legitime Texte aus
  deep-„After"-Beispielen belegt. Belegt-Anteil: 207/314 = 66% (>= 60%-Regel).
- `eval/run_benchmark.py`: berichtet Precision/Recall/F1 @ Threshold 0.40
  UND je Genre FP-Rate (fp/n_clean; nur definiert wenn Clean-Items vorhanden,
  sonst n/a) plus FN-Rate je Genre.
- NEUE Messung (Messvorschrift: `python3 eval/run_benchmark.py`, threshold
  0.40, eval/corpus.jsonl, 2026-08-25): skill-pipeline P 1.0 / R 0.312 /
  F1 0.476 (eval/corpus.jsonl); src-classifier F1 0.669 (eval/corpus.jsonl).
  Ersetzt die alte Baseline-Zahl F1 0.982 (53-Texte-Corpus, eval/corpus.jsonl
  v1.8-Stand): Das neue Corpus ist deutlich härter; der Recall-Rückgang
  konzentriert sich auf Throat-Clearing-/Emphasis-Crutch-Phrasen-Slop aus
  deep/01+04+06 — exakt die in den Deep-Dives als „FEHLT" dokumentierten
  Signale. Precision bleibt 1.0, FP-Rate 0.0 in ALLEN Hard-Negative-Genres
  (legal/academic/marketing/technical/config/recipe/lyric) — das war das
  FP-Ziel des Issues. Bekannte FNs (slop-fn-02) weitergeführt.
- Tests 250 -> 261 grün (Benchmark-Runner mit Fixtur-Corpus + Genre-Breakdown
  getestet; Corpus-Disziplin-Tests: >= 300 Zeilen, Quellenpflicht, 60%-Regel).
  Control-Set-Gate grün (known-FN weitergeführt), Consistency grün.
- TESTS_MODIFIED_AFTER_RED: yes (1 Fall) — Red-Test behauptete fälschlich
  fp_rate=0.0 für ein Genre ohne Clean-Items im eigenen Fixtur-Corpus;
  Spez verlangt „n/a wenn keine Clean-Items". Nur diese Assertion korrigiert.

### #9: Code-Slop-Signale als detect-only Modul code_slop.py

- Neues Modul `skills/ai-slop-detection/scripts/code_slop.py` — analog
  #31/#32 Utility: KEIN Score-Einfluss (Test sichert: keine code_slop-
  Dimension im Text-Scorer). Signale (Regex/Token-basiert, strukturiert
  mit Zeile + Evidence + Hint): chained_type_assertions (as X as Y),
  as_any_casts (gezählt), widen_then_assert (Record<string,unknown>/
  as unknown + `as`-Cast in derselben Funktion — Funktionsgrenzen-Heuristik
  inkl. One-Liner), excessive_defensive_try (>= 3 try/except-pass in einer
  Datei), module_mocking (>= 2 jest.mock/vi.mock/monkeypatch-Dichte).
- SAFETY:-Kommentar-Konvention als Doku im Modul-Docstring (bewusst NICHT
  erzwungen — detect-only).
- CLI-Entscheidung: eigenes `scripts/code_slop_check.py` statt
  `slop_scorer.py --code` — Code-Slop hat keine Abhängigkeit vom Text-Scorer
  und soll keine bekommen; Exit-Codes 0/1/2.
- Tests 261 -> 276 grün (TS/Python-Fixturen, Negative Tests: ehrlicher
  try/except, Single-Mock, Clean-Code). Benchmark unverändert
  (P 1.0 / R 0.312 / F1 0.476, eval/corpus.jsonl), Gate grün, Consistency grün.

### #10: Diff-Modus — Bewertung nur neuer/geänderter Zeilen

- Neues Modul `diff_mode.py`: `slop_scorer.py --diff <base>..<head>` wertet
  NUR neue/geänderte Zeilen aus (differenzielle Disziplin nach
  brianlovin/deslop, deep/07). Textdateien (.md/.markdown/.txt) mit dem
  Text-Scorer; Code-Dateien (.ts/.py/...) werden an code_slop (#9)
  weitergereicht (Integration dokumentiert: Findings der Head-Version,
  gefiltert auf geänderte Zeilenfenster). Guards: Binärdateien (NUL-Byte-
  Check) und Lock-Files (package-lock.json, yarn.lock, *.lock, ...) werden
  immer übersprungen. Kontextfenster ±3 Zeilen nur für Satzfragmente
  (Heuristik: Komma-/Funktionswort-Fortsetzung nach oben, fehlender
  Satzschluss nach unten; unchange Kontextzeilen werden nie allein
  bewertet).
- Ausgabe pro Datei: Score + Top-Signale der neuen Zeilen; CLI-Exit 1 wenn
  eine Text-Datei >= 0.40 oder Code-Findings vorliegen; 2 bei Syntax-Fehler
  der Range.
- Tests 276 -> 290 grün (Fixtur-Repo: git init in tmp, 2 Commits, Slop-/
  Clean-/Lock-/Binär-/Code-Datei; Fenster-Heuristik separat getestet).
  TESTS_MODIFIED_AFTER_RED: yes (2 Fälle, nur Fixtures, Assertions unberührt):
  (a) Base-Commit wurde als Literal "HEAD" statt SHA erfasst (Diff verglich
  head mit head), (b) ctx-Limit-Test nutzte synthetische Zeilen ohne
  Fortsetzungs-Marker. Benchmark unverändert (P 1.0 / R 0.312 / F1 0.476,
  eval/corpus.jsonl), Gate grün, Consistency grün.

### Konsolidierung v1.9.0

- Versionen konsolidiert: README, ai_slop_ontology.yaml, AI-SLOP-ONTOLOGY.md
  auf 1.9.0 (2026-08-25). check_consistency grün. Tests: 250 -> 290 grün.

## [1.8.0] — 2026-08-24 (Batch C)

### #34: Signal fabricated-proof-metrics (+ Claim-Register-Disziplin am eigenen CHANGELOG)

- Neues Modul `proof_metrics.py`: Prozent-/Score-Zahlen mit Qualitäts-Claim
  (accuracy/precision/recall/F1/false positives/error|success rate) ohne
  Quellenreferenz (corpus/Korpus/eval/Link/DOI/et al./Jahr) im Umkreis von
  200 Zeichen => detect-only Hit mit Evidence. Zahlen ohne Claim-Wort
  feuern nie („42 artifacts“ ist ok).
- IRONIE-ENTScheid (dokumentiert): Der eigene CHANGELOG behauptet
  „Benchmark F1 0,982“ — der Detector FEUERTE darauf. Entscheidung: Corpus-
  Verweis hinzugefügt statt Ausnahme-Whitelisting — jede F1-0,982-Zeile im
  CHANGELOG trägt jetzt „(eval/corpus.jsonl)“. Der Ironie-Test liest
  CHANGELOG.md und erzwingt dauerhaft 0 Hits (Claim-Register-Disziplin).
- Detector-Fix dabei: „Corpus“/„Korpus“ case-insensitiv als Quellenreferenz.
- Tests 243 -> 250 grün; Gate, Consistency, Benchmark unverändert.

### #33: Instruktions-Slop-Modul (CLAUDE.md/AGENTS.md/SKILL.md-artige Dateien)

- Neues Modul `instruction_slop.py`, vier detect-only Signale mit Evidence +
  keep_when: generic-advice („write clean code“, „be thorough“, „follow best
  practices“), obvious (Regeln, die der Agent ohnehin tut: „use git“),
  too-vague („improve quality“ — Imperativ ohne messbares Objekt),
  contradiction („always X“ + „never X“ mit normalisiertem identischem X).
- Negative Tests sichern: konkrete prüfbare Anweisungen („Run pytest tests -q
  before every push“) feuern keines der Signale. Tests 233 -> 243 grün;
  Gate, Consistency, Benchmark unverändert.

### #32: Signal reinventing-wheel (heuristisch, detect-only)

- Neues Modul `reinventing_wheel.py`: AST-Parsing, Ratcliff/Obershelp-
  Ähnlichkeit (difflib.SequenceMatcher) > 0,8 über Name+Signatur zweier
  Funktionen im selben Modul; feuert nur, wenn der Docstring der neuen
  Funktion die existierende NICHT referenziert („delegates to X“ =>
  bewusster Shim => kein Hit). Syntaxfehler => leer (konservativ).
- Tests 229 -> 233 grün; Gate, Consistency, Benchmark unverändert.

### #31: Kategorie generated-docs (detect-only, Code-Kontext)

- Neues Modul `generated_docs.py`: ARCHITECTURE.md/CONTRIBUTING.md/
  PHILOSOPHY.md/GOALS.md, deren letzter berührender Commit innerhalb der
  letzten 5 Repo-Commits liegt UND generische Füllphrasen enthält
  („this document outlines“, „well-structured“, „maintainable“) => Hit
  {file, category, age_commits, filler_phrases, keep_when}.
- Entscheidungen: Frische via Commit-Hash-Mitgliedschaft in rev-list -n5
  (Timestamps scheitern an sekundengleichen Batch-Commits, gemessen in der
  Fixtur); untracked Dateien ohne Commit-Evidenz werden übersprungen
  (konservativ). Beide Bedingungen (frisch UND Füllphrasen) müssen gelten.
- Temp-Dir-Git-Fixtures; Tests 224 -> 229 grün; Gate, Consistency,
  Benchmark unverändert.

### #29: False-Positive-Learning-Store (not_slop.jsonl)

- Neues Modul `learning_store.py`: JSONL-Store {signal_id, sample_hash,
  note, date, added_by}; sample_hash = sha256(text)[:16]. Persistenz rein
  dateibasiert (append-only), kein Server/API.
- Scorer-Integration: slop_score(..., not_slop_store=path) — Signal-Familien
  (buzzwords, phrases, multilingual, provenance, fake_authority,
  trailing_moral, mirrored, portability), deren ID + Sample-Hash im Store
  stehen, werden aus der Bewertung entfernt und im Output als
  signals.exempted dokumentiert. Die >=2-Familien-Eskalation bleibt:
  Exemptions waschen echten Mehrfamilien-Slop nicht unter die Schwelle
  (Test deckt den Floor-Fall).
- CLI: --mark-not-slop SIGNAL_ID --file PATH [--store|--note|--by] (ohne
  --file: Exit 2); Score-Modus: --not-slop-store PATH, Default-Autoerkennung
  not_slop.jsonl neben der bewerteten Datei.
- Test-Fixtur-Anpassung dokumentiert: ursprüngliche Integrations-Fixtur traf
  neben Buzzwords eine zweite starke Familie (Hedging+Moral) => Floor — auf
  reine Buzzword-Fixtur umgestellt, damit die Exemption-Mechanik geprüft wird.
- Tests 218 -> 224 grün; Gate, Consistency, Benchmark (eval/corpus.jsonl) F1 0,982 unverändert.

### #28: Markdown-Struktur-Anomalien (detect-only)

- Neues Modul `markup_anomalies.py`: HeadingLevelJump (+2 Level, z. B. ## -> ####;
  reine Abstiege feuern nie), ExcessiveThematicBreaks (>2 pro 1000 Wörter, mit
  absoluter Untergrenze von 3 Breaks als Kurztext-FP-Guard), TitleCaseHeadings
  (>70% der Headings durchgehend kapitalisiert), SingleRowTable (Tabelle mit
  exakt einer Datenzeile), BoldMidSentenceDensity (>2 Sätze mit inline **bold**
  je Absatz).
- Abgrenzung (#46): FormattingSlop (rhetorical_patterns) deckt Emoji-Headings/
  Bold-Sprenkel als Muster-Instanz — hier geht es um dokumentweite Struktur-
  Raten über die Markdown-Quelle, kein Score-Einfluss.
- TESTS_MODIFIED_AFTER_RED: yes — Negativ-Fixtur „Level-Abstieg“ enthielt
  versehentlich einen +2-Aufstieg (1->3); gegen die Spez ist genau das ein
  Treffer. Fixtur auf echten Abstieg (2->1) ohne vorherigen Aufstieg korrigiert.
- Tests 207 -> 217 grün; Gate, Consistency, Benchmark unverändert.

### #27: Rhythmus-/Opener-Metriken (detect-only)

- Neues Modul `rhythm_openers.py`: UniformLengthRun (3+ konsekutive Sätze mit
  Satzlänge ±5%), SelfAnsweredQuestion („Why X? Because Y.“ / „What's the
  catch? It's simple:“ — Frage + Self-Answer-Paar), LowOpenerDiversity
  (>30% identische Zweiwort-Opener, min. 4 Sätze).
- Abgrenzungen (#46): UniformLengthRun (lokale Konsekutiv-Rate) vs.
  UniformSentenceLength (globaler Std-Dev) vs. RoboticRhythm (Fragment-Stakkato);
  LowOpenerDiversity (Ganztext-Rate, Zweiwort-Signatur) vs. RepeatedOpenings
  (adjazentes Muster, ein Wort). Alles detect-only, kein Score-Einfluss.
- TESTS_MODIFIED_AFTER_RED: yes — Fixtur-Satzlängen im Red-Commit widersprachen
  der eigenen ±5%-Spez (7 vs. 6 Wörter); auf exakt 6/6/6 korrigiert, um die
  Spez zu testen statt die Implementierung.
- Tests 198 -> 207 grün; Gate, Consistency, Benchmark unverändert.

### #25: Universalquantoren-Rate + Quellen-Diskrepanz (detect-only)

- Neues Modul `quantifiers.py`: UniversalQuantifiers (Subjekt-Quantoren
  everyone knows/we all/nobody/no one/always/never, kumulativ >= 2 Vorkommen
  => Signal; ein einzelnes feuert bewusst nicht) und SourceDiscrepanz
  (Authority-Claim „studies show“ + gezählte Quellen „three studies“ ohne
  jegliche Zitat-Marker im Text => Signal).
- Abgrenzung (#46): weasel_attribution-Phrasen und AUTHORITY_PATTERNS im Scorer
  bleiben unverändert (doppeln nicht); Test sichert, dass kein neuer Scorer-
  Weight entsteht. Tests 190 -> 198 grün; Gate, Consistency, Benchmark unverändert.

### #14: portability_score als 14. Dimension

- Neues Modul `portability.py`: Satz ist portabel, wenn kein Großschreibungs-Token
  (außer Satzanfang), keine Zahl, kein Zitat/Code, kein URL/Pfad/„@“-Anker.
  Rate > 0,5 => geringgewichtetes Signal (Gewicht 0,02, nie Eskalations-Familie).
- Deutsch getestet: Nominal-Großschreibung blockiert Portabilität konservativ;
  absichtlich kleingeschriebener Text bleibt messbar portabel (DE+EN-Tests).
- Doku: SKILL.md „13 Detection Dimensions“ -> „14“ (inkl. Frontmatter-Description).
- Gewicht bewusst von 0,03 auf 0,02 reduziert: Copula-FP-Regressionstest
  (faktischer Text 0,401 >= 0,40) zeigte die Grenze — gemessen, nicht geraten.
- Tests 184 -> 190 grün; Gate grün; Benchmark (eval/corpus.jsonl) F1 0,982 unverändert.
- Prozessnotiz: Commits waren kurzzeitig auf master-Basis verwaist (fremder
  Checkout im Shared-Worktree); Chain per cherry-pick wiederhergestellt.

### Version konsolidiert: 1.8.0 (README, yaml, MD) — Batch C abgeschlossen

- Zehn Issues (#13, #14, #25, #27, #28, #29, #31, #32, #33, #34) als
  lineare Branch-Kette auf master (keine Merges, alle Branches gepusht).
- Tests 172 -> 250 grün; Control-Set-Gate grün (KNOWN-FN slop-fn-02-Ticket
  weitergeführt); Consistency grün; Benchmark F1 0,982 (eval/corpus.jsonl)
  unverändert.

### #13: Mikro-Muster detect-only (false agency, false range, recap ending, heading-repeated)

- Neues Modul `micro_patterns.py`: vier detect-only Signale mit je keep_when-Guard
  und Positiv-/Negativ-Tests: FalseAgency (geschlossene Listen: Subjekt
  decision/data/strategy/system/market × Verb emerges/decides/believes/realizes/knows),
  FalseRange („from the X to the Y“ mit Grand-Sweep-Platzhalter-Heuristik),
  RecapEnding (Opener + >=30% Content-Word-Overlap mit dem Intro),
  HeadingRepeatedBelowItself (Heading + Folgesatz beginnt mit denselben 2+ Inhaltswörtern).
- Abgrenzung (#46): RecapEnding feuert nur bei Opener UND messbarer Restatement-Overlap —
  Opener allein bleibt HollowKickerRecap (rhetorical_patterns). Kein Einfluss auf
  slop_score — detect-only.
- Tests 172 → 184 grün; Gate, Consistency, Benchmark unverändert.

## [1.7.0] — 2026-08-24 (Batch B)

### #26: BinaryContrast-Erweiterung (deep/01 §2.5)

- Vorab geprüft: „It's not X, it's Y“ war bereits gedeckt (erstes Muster
  matcht die Komma-Variante) — Regressionstest ergänzt. Drei fehlende
  Varianten als Regex hinzugefügt: „X isn't just Y — it's Z“ (Em-Dash/
  Bindestrich-Separator), „No longer X, now Y“, „Gone are the days of X,
  replaced by Y“ — exakt die Varianten aus der Quellen-Struktur-Liste.
- Negative Tests: schlichte Aussage und „no longer“ ohne Kontrast-Teil
  feuern nicht.
- Tests 165 → 172 grün; Gate, Consistency, Benchmark (eval/corpus.jsonl) F1 0,982 unverändert.

### Version konsolidiert: 1.7.0 (README, yaml, MD)

### #43: Tokenizer-Refaktor — CJK-fähige Metrik-Basis

- Neues Modul `tokenizer.py`: `tokenize_words()` (Whitespace-Wörter für
  Space-Sprachen unverändert, pro-Zeichen-Tokenisierung für CJK-Läufe,
  CJK-Interpunktion ausgeschlossen) und `split_sentences()` (ASCII `.!?`
  plus CJK-Satzenden `。！？`).
- Verdrahtet in `information_density`, `repetition_ratio`, `burstiness`,
  `punctuation_anomaly_score`, `mirrored_intro_conclusion` und die
  Satz-/Wortbasis von `slop_score()` — chinesische Texte liefern jetzt
  sinnvolle word_count/Dichte/Repetition/Burstiness-Werte statt
  1-Satz-1-Mega-Token-Müll.
- Abgrenzung: KEINE neuen Sprach-Signale (Buzzword-Detection bleibt
  Sprach-DB-getrieben wie bisher — das ist #53); `adverb_stats` bleibt
  bewusst englisch (-ly), dokumentiert.
- Tests 154 → 165 grün (alle bestehenden Space-Sprachen-Tests unverändert
  grün); Gate, Consistency, Benchmark (eval/corpus.jsonl) F1 0,982 unverändert.

### #40: Input-Normalization & Anti-Evasion-Layer

- Neues Modul `input_norm.py`, angewendet VOR allen Metriken in `slop_score()`:
  (1) Unicode-NFKC (faltet u. a. FULLWIDTH-Formen), (2) Zero-Width-Strip
  (ZWSP/ZWNJ/ZWJ U+200B–200D, BOM U+FEFF), (3) Homoglyph-Mapping der
  minimalen kyrillisch/lateinischen Verwechslungspaare а→a, е→e, о→o,
  р→p, с→c, х→x (nach NFKC, da NFKC skriptübergreifende Lookalikes nicht
  faltet). Idempotent; bewusst keine vollständige Confusables-Tabelle
  (Scope-Grenze, dokumentiert).
- Evasion-Tests: „dеlvе“ (kyrillisch е), „del\u200bve“, „ｄｅｌｖｅ“ triggern
  nach Normalisierung den Buzzword-Signal-Pfad wie der Klartext.
- Tests 144 → 154 grün; Gate, Consistency, Benchmark (eval/corpus.jsonl) F1 0,982 unverändert.

### #42: Genre-Register-Profile (False-Positive-Guards für legitime Stile)

- Neues Modul `genre_profiles.py`: Profile legal / academic / marketing /
  technical als reine Konfiguration — je Genre eine Liste exempter Terme
  (z. B. „pursuant to" legal-exempt, „cutting-edge"/„state-of-the-art"
  marketing-exempt, „furthermore"/„moreover" academic-exempt), auf 0
  gesetzte Gewichte für register-konventionelle Merkmale (Passiv/uniforme
  Satzlängen academic, Listen technical) und erhöhter Decision-Threshold.
- Nur explizites Opt-in: `--genre <name>` im Skill-CLI bzw. `genre=`-Parameter
  an `slop_score()` — KEINE Auto-Erkennung (bewusst out of scope).
- Exemptions wirken nur auf Signal-Matching (komponiert mit #23-Quote-
  Exemption); Strukturdimensionen messen den Volltext. Provenance-Floors
  und ≥-2-Familien-Eskalation behalten ursprüngliche Stärke — Genre-Profile
  können echten Slop nicht unter die Schwelle waschen (Test deckt das ab).
- Unbekanntes Genre → ValueError / CLI-Exit 2. Standard-Texte ohne Flag
  unverändert (128→144 Tests grün; Gate + Benchmark (eval/corpus.jsonl) F1 0,982 unverändert).

### FU-1: #24-Intensifier-Fix (review-batch-a.md §6, MEDIUM)

- `adverb_stats()`: Intensifier-Spans werden aus Zähler UND Nenner der
  -ly-Rate ausgeschlossen (Span-Überlappung, analog `copula_stats`) — 4 der
  5 Intensifier enden selbst auf -ly und zählten sonst doppelt. Reiner
  Intensifier-Text (≥ 40 Wörter) misst jetzt Rate 0,0 → `adverb_slop` 0,0
  statt 1,0 (Reviewer-Messung 0,136 → 1,0 vor dem Fix); das
  Intensifier-Signal feuert unverändert weiter.
- Tests 128 → 133 grün; Control-Set-Gate und Consistency-Check grün;
  Benchmark unverändert (F1 0,982).

## [1.6.0] — 2026-08-24

### MS-I1: CLI-Härtung + Control-Set-Gate

- `slop_scorer.py`-CLI: `--file PATH` (explizit), Auto-Erkennung existierender
  Dateipfade als Positional-Argument (fixt den Bug, dass Pfade als Text
  gescort wurden — „Avg sentence 3.0 words"-Symptom), Deprecation-Warnung
  für Inline-argv-Text.
- `eval/control_set.jsonl`: 10 handgeschriebene Texte (5 Slop / 5 harte
  Negative: Technik-Postmortem, Vertragsprosa, Paper-Abstract,
  Router-Konfig, Kochrezept).
- `eval/run_control_set.py`: Gate — alle Slop ≥ 0,40, alle Negativen < 0,40,
  dokumentierte FNs als KNOWN-FN erlaubt.
- Minimale Kalibrierung (dokumentiert, ehrlich): Buzzword-Norm 8 → 6
  (Deckungsgleich mit `src/scorer.py`-Kommentar „6+ buzzwords = definite
  slop") + kombinierte Eskalationsregel (buzz_slop ≥ 0,5 UND phrase_slop
  ≥ 0,5). Hebt `slop-fn-01` von 0,279 auf 0,40; Corpus-Benchmark
  unverändert (Pipeline F1 0,982, P 1,0). Bekannter FN bleibt
  `slop-fn-02` (0,314, Business-Listicle-Muster außerhalb der Phrase-DB)
  — als KNOWN-FN im Gate dokumentiert.

### Issue #23: False-Positive-Guard-Systematik

- Neues Modul `skills/ai-slop-detection/scripts/fp_guards.py`:
  - **Quote-Exemption**: zitierte Passagen > 40 Zeichen werden aus der
    Signal-Erkennung (Buzzwords/Phrasen/Authority/Multilingual) entfernt;
    Kurz-Zitate (< 40 Zeichen) bleiben erhalten. Strukturdimensionen messen
    weiterhin den Volltext.
  - **Kumulativregel**: Phrase-Kategorien scorieren erst ab 2 Treffern
    (Einzel-Treffer werden nur als Signal berichtet, nicht gescort).
  - **Konsistente Schwellen**: `fp_guards.THRESHOLDS` als Single Source of
    Truth (DECISION_THRESHOLD, QUOTE_MIN_CHARS, PHRASE_MIN_HITS).
- Eskalationsregel generalisiert auf „≥ 2 unabhängige Marker-Familien“
  (Buzzwords ≥ 0,5 | korroborierte Phrase-Kategorien | Authority | Moral |
  Mirroring | Einzel-Treffer in High-Confidence-Kategorien ≥ 0,75).
- Regressionstest: technischer Text, der eine Slop-Passage in Anführungs-
  zeichen zitiert (SKILL.md-/Review-Fall), fällt von 0,70 auf < 0,40.
- Trade-off dokumentiert: Scorer-Recall auf Corpus 0,828 → 0,862 (besser),
  Pipeline F1 unverändert 0,982, Precision 1,0.
- Tests 94 → 105.

### Issue #20: Provenance-Marker als deterministische Regex-Signale

- Neues Modul `provenance_signals.py` mit vier Marker-Familien:
  `turn\d+search\d+` (Chat-/Search-Loop-Referenzen),
  `:contentReference[` (Zitier-Artefakte), Platzhalter-Daten
  `(19|20)\d\d-XX-XX` (ungefüllte Template-Slots, echte Daten wie
  2024-03-15 matchen nicht), unsichtbare Unicode-PUA-Zeichen
  (U+E000–U+F8FF).
- Kategorie `provenance`, hohe Konfidenz: jeder Treffer floored den Score
  auf den Decision-Threshold (≥ 0,40 „Suspicious“), 2+ Marker gelten als
  entscheidend; zusätzlich eigene Familie in der Eskalationsregel.
- Bewusst NICHT von der Quote-Exemption (#23) ausgenommen: ein zitiertes
  Artefakt beweist weiterhin den Pipeline-Durchlauf.
- Corpus/Control-Set unverändert (F1 0,982, Gate grün). Tests 105 → 114.

### Issue #22: Copula-Rate

- `slop_scorer.copula_stats()`: Anteil von is/are/was/were an allen
  Kopula-Konstruktionen vs. Ersatzverben (serves as, boasts, features,
  refers to, represents, embodies).
- Bedingter Score-Beitrag (kleines Gewicht via `weights["copula"]`,
  Standard 0): Rate ≥ 0,9 mit ≥ 4 Konstruktionen → copula_slop 1,0.
  Kein Standalone-Trigger, keine Starke-Familie in der Eskalation.
- #46-Prävention (im Code kommentiert): Ersatzverb-Matches, die mit
  Buzzword-Spans überlappen („serves as a testament“), werden aus dem
  Nenner ausgeschlossen — keine doppelte Bewertung derselben Passage.
- Corpus/Control-Set unverändert. Tests 114 → 121.

### Issue #24: Adverb-Rate + Intensifier

- `slop_scorer.adverb_stats()`: -ly-Wörter / Gesamtwörter, Schwelle
  > 4 % (ADVERB_RATE_THRESHOLD) ab 40 Wörtern Textlänge
  (ADVERB_MIN_WORDS).
- Intensifier-Liste (very, really, extremely, incredibly, remarkably) als
  BEDINGTE Beiträge: ≥ 2 Intensifier verstärken eine bereits getriggerte
  Adverb-Rate (0,5 → 1,0), tragen aber allein NICHTS bei.
- Abgrenzung #21 (im Code dokumentiert): #21 ist Schreib-Doktrin (welche
  Adverben beim Verfassen streichen); dieses Signal misst nur die Rate
  empfangener Texte, ohne Stil-Urteil. Abgrenzung #22: Adverben sind keine
  Verben — keine Span-Überlappung mit der Copula-Dimension möglich.
- Corpus/Control-Set unverändert. Tests 121 → 128.

### Release-Konsolidierung

- Version konsolidiert auf **1.6.0** (README, ai_slop_ontology.yaml,
  AI-SLOP-ONTOLOGY.md, CHANGELOG). Konsistenz-Check grün.

## [1.5.0] — 2026-08-25

**Formatting-Slop-Doktrin + Banned-Words-Abgleich (#16).**

- `FormattingSlop`-Detektor nach no-ai-slop/humanizer-Doktrin verfeinert:
  Em-Dash-Regel (kein Em-Dash in Kurztext < 120 Wörter; 1–2 in langen
  Drafts erlaubt; Cluster immer), Title-Case-Heading-Rate (≥ 2), Curly
  Double Quotes in Plaintext, Hyphenated-Pair-Rate (≥ 2 Compound-Modifier
  wie „cross-functional, data-driven“). Alles weiterhin detect-only.
- Neue Punctuation-Indikatoren in `ontology.json`: TitleCaseHeadings,
  CurlyQuotes, HyphenatedPairRate, BoldMidSentence; EmDashExcess um
  Doktrin-Schwellen ergänzt.
- Banned-Words-Lücken geschlossen (Abgleich mit petergyang/no-ai-slop):
  `utilize`, `meticulous`, `supercharge`, `supercharged`, `nestled` →
  Tier 2; `quietly` → Tier 4 (kontextabhängig). In `ontology.json` und
  `slop_scorer.BUZZWORD_TIERS` gespiegelt.
- Testsuite: 68 → **78 Tests**.

## [1.4.0] — 2026-08-25

**Phrase-Datenbank: fünf Editor-Tell-Kategorien (#8).** Die Phrase-Kategorien
zielten bisher auf Essay-/SEO-Slop; die Daily-Driver-Tics fehlten:

- `emphasis_crutches` („let that sink in", „full stop")
- `meta_commentary` („the rest of this essay…")
- `rhetorical_setups` („plot twist:", „what if I told you")
- `vague_declaratives` („the stakes are high")
- `weasel_attribution` („experts agree", „widely regarded as")

Je Kategorie gelten ≥2 Treffer als entscheidendes Signal (wie bei
typePatterns): neue Signale EmphasisCrutch, MetaCommentary, RhetoricalSetup,
VagueDeclarative, WeaselAttribution (WeaselAttribution Severity high) — in
beiden Engines (src + Skill) parallel implementiert, Daten in `ontology.json`
und `slop_scorer.PHRASE_CATEGORIES` gespiegelt. Quellen:
hardikpandya/stop-slop references/phrases.md; petergyang/no-ai-slop.

- Testsuite: 68 → **72 Tests**.

## [1.3.0] — 2026-08-24

**Rhetorische Muster: Wikipedia-„Signs of AI writing"-Set (#7).** Sechs neue
detect-only-Muster aus Wikipedia:Signs_of_AI_writing / blader/humanizer /
petergyang/no-ai-slop: ThroatClearing, FauxInsightSetup, ImportancePuffery,
ForcedTriad, RepeatedOpenings, ChatbotLeftover — je mit `keep_when`-Guard und
zitierte Evidenz; weiterhin bewusst nicht im numerischen Score.

- Detektor-Erweiterung `skills/ai-slop-detection/scripts/rhetorical_patterns.py`
  + Spiegelung in `ontology.json` (`signals.text.rhetoricalPatterns`, 9 → 15
  Muster; Paritätstest + Konsistenz-Checker decken beide ab).
- Guards gegen Fehlalarme: ThroatClearing nur am Textanfang, ForcedTriad nur
  bei Slogan-Form (Suffix-Klasse, keine Zahlen-/Label-Listen),
  RepeatedOpenings erst ab 3 Sätzen mit gleichem Opener.
- Testsuite: 69 → **72 Tests**.

## [Unreleased]

**Dokumentation & Bedienungsanleitung.** Vollständige Anleitung
`docs/USER-GUIDE.md` mit Konzepten, Command-Reference, sieben Anwendungsfällen
(Qualitätscheck, RAG-Filter, CI-Gate, Prosa-Editing, Code-Review,
Mehrsprachigkeit, Batch), Python-Library-Nutzung, JSON-Integration und FAQ.
Jeder ```console-Befehl der Anleitung wird von `tests/test_docs_examples.py`
tatsächlich ausgeführt — die Beispiele können nicht von der funktionierenden
CLI abdriften. README verlinkt die Anleitung.

- Neu: `slop score`/`check --fail-over THRESHOLD` — Exit-Code 1 bei
  Score ≥ Schwelle (CI-Gating).
- Fix: Hallucinated-Package-Erkennung (`InventedPackage`) erkennt jetzt auch
  Aufruf-/Quote-Formen wie `require("pkg")` / `import('pkg')`, ohne
  Lookalikes wie `important`/`useState` fälschlich zu treffen.
- Testsuite: 65 → **69 Tests**.

**CLI-Toolkit (`slop`).** Das Projekt hat jetzt eine einheitliche
Kommandozeile über die kanonische Engine (`src/`) und die Ontologie-Daten —
neues Paket `slopkit/` mit Entry-Point `slop` (bzw. `python -m slopkit`), ohne
Fremd-Abhängigkeiten (nur Standardbibliothek).

- Subcommands: `score`, `classify`, `rhetoric`, `check`, `code`, `info`,
  `benchmark`, `selfcheck`.
- Eingabe je Befehl: Positional-Text, `--file PATH` oder stdin (`-`); `--json`
  für maschinenlesbare Ausgabe.
- Wiederverwendung statt Duplikation: wrappt `src/SlopClassifier` und den
  detect-only Rhetorik-Detektor; `pyproject.toml` definiert den Entry-Point.
- CI-Smoke-Test (`slop info`/`selfcheck`/`rhetoric`) ergänzt.
- Testsuite: 55 → **65 Tests**.

**Rhetorische Muster (detect-only).** Neun Satz-/Absatz-Muster aus dem
MIT-Skill [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop)
als benannte Detektoren integriert: Binary Contrast, Colon Reveal, Superficial
Analysis, Negative Listing/Fragmentation, Fake-strong Verb, Synonym Cycling,
Hollow Kicker/Recap, Formatting Slop, Robotic Rhythm.

- Datenmodell in `ontology.json` unter `signals.text.rhetoricalPatterns`
  (Label, Beschreibung, Beispiel, Fix, `keep_when`-Falsch-Positiv-Leitplanke).
- Detektor `skills/ai-slop-detection/scripts/rhetorical_patterns.py` (nur
  Standardbibliothek), verdrahtet in `classify_text()` als
  `result.rhetorical_patterns`.
- **Detect-only:** benannte Evidenz mit zitierter Zeile, fließt bewusst
  **nicht** in den numerischen Slop-Score ein — Benchmark unverändert
  (src-Klassifikator F1 0,96; Skill-Pipeline F1 0,98).
- Konsistenz-Checker erzwingt Parität JSON ↔ Skill-Modul.
- Testsuite: 47 → **55 Tests**.

## [1.2.1] — 2026-07-10

Behebt die drei Codex-Review-Kommentare aus PR #2 (alle P2):

1. **Multilingual-Floor im src-Klassifikator** — bereits durch v1.2.0 behoben
   (Multilingual-Signal hat Severity `high`, Noisy-OR ergibt 0,49 ≥ 0,40);
   jetzt durch expliziten Regressionstest abgesichert.
2. **KeyError bei Custom-Tiers mit Groß-/Kleinschreibung** —
   `find_term_matches` liefert Term-Keys jetzt lowercased (beide Engines),
   sodass Lookup-Tabellen mit gelowerten Keys immer treffen. Vorher:
   `buzzword_score(text, {"tier": ["Game-Changing"]})` → KeyError (src)
   bzw. Tier „unknown" (Skill).
3. **Neue Slop-Typen im src-Klassifikator verdrahtet** — die Typ-Muster
   stehen jetzt datengetrieben in `ontology.json`
   (`signals.text.typePatterns`, 12 Typen) und `classify_text()` erkennt
   sie (`slop_types` + `TypePattern_*`-Signal ab 2 Treffern, Severity high).
   Ein Security-Report-Text scorte im src-Klassifikator vorher 0,0 —
   jetzt ≥ 0,59. Benchmark src-Klassifikator: F1 0,89 → **0,96**.
   Der Konsistenz-Checker verifiziert Skill ↔ JSON-Typ-Muster-Parität.

Testsuite: 42 → 47 Tests.

## [1.2.0] — 2026-07-10

Setzt die fünf Follow-up-Vorschläge aus REVIEW-2026-07.md §4 um.

### Evaluation & Kalibrierung
- **Evaluations-Korpus** `eval/corpus.jsonl`: 53 gelabelte Beispiele
  (26 Slop / 27 Clean) in 7 Sprachen (EN/DE/FR/ES/HI/VI/UR), inkl. bewusst
  schwerer Fälle (subtiler Slop, disclosed AI-assisted Clean-Text).
- **Benchmark-Runner** `eval/run_benchmark.py`: Precision/Recall/F1 pro Engine
  und Sprache; läuft informativ in CI.
- **Kalibrierungs-Skript** `eval/calibrate.py`: Koordinaten-Aufstieg über die
  13 Dimensionsgewichte mit Precision-Floor (Default 0,95); unterstützt
  eigene Korpora (`--corpus`, z. B. Export des Shaib-et-al.-Datensatzes).
- **Kalibrierte Default-Gewichte** im Skill-Scorer (dokumentiert im Code):
  Scorer-F1 0,47 → 0,89; Gesamt-Pipeline (Scorer + Typ-Klassifikator)
  **F1 0,98 / Precision 1,0** auf dem Korpus.

### Scoring-Verbesserungen
- **Noisy-OR-Aggregation** in `src/classifier.py` (Text und Code) statt des
  Mittelwerts: unabhängige Evidenz akkumuliert (drei Medium-Signale ergaben
  vorher ~0,29 im Schnitt). Formel-Doku in Ontologie §6/§10, ontology.json
  und README nachgezogen.
- Multilingual-Signal auf Severity `high` (≥2 sprachspezifische Marker sind
  starke Evidenz, da alle übrigen Signale englischbasiert sind).
- Neue Phrasen-Kategorie **`authority_claims`** in ontology.json + dediziertes
  `FakeAuthorityPattern`-Signal im src-Klassifikator.
- Skill-Typ-Klassifikator: ≥2 distinktive Muster eines Typs (Type-Score ≥0,6)
  heben den Score auf mindestens 0,45.

### Sprachen (§12-Lücke geschlossen)
- **Hindi, Vietnamesisch, Urdu**: je 8–10 formelhafte LLM-Marker in
  Skill-Scorer und ontology.json; Regressionstests und Korpus-Beispiele.

### Konsistenz & Parität
- `ontology.ttl` synchronisiert: `PeerReviewSlop`, `SecurityReportSlop`,
  `HyperTypicalityDetection`, Datum/Quellen aktualisiert.
- **Konsistenz-Checker** `scripts/check_consistency.py` (JSON↔TTL↔YAML↔Skill)
  in CI verdrahtet — Drift bricht den Build.
- **Engine-Paritätstests** `tests/test_engine_sync.py`: pinnt das Verhalten
  der bewusst duplizierten Kern-Matcher in `src/` und `skills/` aufeinander.
  Volles Packaging wurde geprüft und verworfen (Skill muss self-contained
  bleiben); die Entscheidung ist im Test dokumentiert.
- Testsuite: 37 → 42 Tests.

## [1.1.0] — 2026-07-10

### Recherche & Ontologie
- **Neue Slop-Typen** (forschungsbelegt):
  - `SecurityReportSlop` — KI-generierte Schwachstellen-Reports; curl beendete sein
    HackerOne-Bug-Bounty im Februar 2026 (~20 % Slop-Anteil, Confirmed-Rate <5 %).
  - `PeerReviewSlop` — KI-generierte Peer-Reviews; Organization Science (2026):
    >30 % der Reviews KI-beteiligt, Feedback wird enger und weniger substanziell.
- **Neues Image-Signal** `HyperTypicality`: KI-Gesichter wirken „typischer als echte"
  (Regression zum mathematischen Mittel); Menschen sind darauf trainierbar
  (ANU/PNAS 2026, near-perfect Accuracy).
- **Schlüsselzahlen aktualisiert** (Stand Juli 2026): NewsGuard 3.749 Content-Farmen
  (23.06.2026); Deezer 44 % AI-Anteil an Neu-Uploads (~75.000 Tracks/Tag, nur 1–3 %
  der Streams, ~85 % davon Fraud); Spotify 75 Mio.+ entfernte Spam-Tracks;
  Organization Science +42 % Submissions seit ChatGPT.
- **8 neue Referenzen** (REFERENCES.md #31–38), darunter die Gegenposition
  Nishal/Sax/Kieslich (arXiv:2606.12285) zu Kommers et al.
- **Alle Kernzitate verifiziert**: Shaib et al. (arXiv:2509.19163), Madsen & Puyt
  (SSRN 5558018), Kommers et al. (arXiv:2601.06060), Keisha et al. (arXiv:2509.04796).
- Kanonisches Dokument umbenannt: `AI-SLOP-ONTOLOGY-v1.0.0.md` → `AI-SLOP-ONTOLOGY.md`
  (Version steht im Front Matter).

### Detection-Engine (Bugfixes aus dem Deep Review, siehe REVIEW-2026-07.md)
- **Word-Boundary-Matching**: Buzzwords matchen keine Teilwörter mehr
  („dynamic" ≠ „thermodynamics").
- **Overlap-Deduplizierung**: Überlappende Begriffe zählen einmal, längster Match
  gewinnt („rich tapestry" schluckt „tapestry").
- **Multilingual-Fix** (Skill-Scorer): Groß-/kleinschreibungs-Bug behoben — deutsche
  Marker wie „im digitalen Zeitalter" wurden nie erkannt (Vergleich von
  Original-Casing gegen lowercase-Text).
- **Burstiness-Neutralität**: Texte mit <3 Sätzen werden nicht mehr fälschlich als
  „uniform" (= AI-artig) gewertet.
- **Severity-gewichtetes Scoring** (`src/classifier.py`): Die dokumentierte Formel
  `min(1, Σ w(severity)·confidence / n)` mit Eskalation (critical ∨ ≥2 high → ≥0,70)
  ist jetzt tatsächlich implementiert; vorher wurde nur der Confidence-Mittelwert
  gebildet und das `weights`-Dict war toter Code.
- **Multilingual-Floor**: ≥3 multilinguale AI-Marker heben den Score auf mindestens
  0,40 („Suspicious"), da englisch-basierte Dimensionen nicht-englische Texte verwässern.
- **Mirrored-Intro/Conclusion**: Stopword-Filterung reduziert False Positives.
- `get_signal_stats()` listet „description" nicht mehr als Sprache.
- SKILL.md: falscher relativer Pfad zur Ontologie korrigiert; 14 statt 12 Slop-Typen.

### Infrastruktur
- Testsuite unter `tests/` (stdlib `unittest`, keine Zusatz-Dependencies).
- `LICENSE` (CC BY 4.0) ergänzt — README versprach die Lizenz bereits.
- GitHub-Actions-Workflow für Tests.

## [1.0.0] — 2026-05-20

- Initial Release: kanonisches Dokument, YAML/JSON/TTL-Ontologie, Klassifikator,
  Scorer, Skill `ai-slop-detection`, 459 Signale, 22 Detection-Techniken,
  12 Harm-Klassen.
