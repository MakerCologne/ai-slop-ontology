# Changelog

## [Unreleased — Batch B]

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
- Tests 144 → 154 grün; Gate, Consistency, Benchmark F1 0,982 unverändert.

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
  unverändert (128→144 Tests grün; Gate + Benchmark F1 0,982 unverändert).

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
