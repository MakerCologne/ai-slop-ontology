# Changelog

## [1.9.0] — 2026-08-25 (Batch D)

### #41: Labeled Benchmark-Corpus mit Hard Negatives (~300+ Texte)

- `eval/corpus.jsonl` von 53 auf 314 Zeilen erweitert. Jede Zeile jetzt
  `{id, label, lang, type, genre, text, source}`.
- 192 neue Slop-Texte: wörtlich zitierte Original-Slop-Phrasen aus den
  Deep-Dive-Artefakten (deep/01–07: stop-slop, no-ai-slop, humanizer,
  Wikipedia, unslop writing+SaaS, poteto) — je 9–12 Phrasen pro Text,
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

### (Batch D läuft weiter: #10 diff-Modus — Eintrag folgt.)

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
