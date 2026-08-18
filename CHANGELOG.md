# Changelog

## [Unreleased]

**Dokumentation entspricht wieder den Daten.** Behauptete Zahlen werden jetzt
von Tests gegen die Daten geprüft (`tests/test_doc_claims.py`).

- `SKILL.md` sprach von „459 signals"; die Datenbank hat 233 gezählte
  Textsignale (107 Buzzwords, 114 Phrasen, 7 strukturelle, 5 Interpunktion) —
  korrigiert samt Aufschlüsselung.
- README zählte 38 Referenzen, `REFERENCES.md` listet 39; die Überschrift dort
  stand noch auf v1.1.0.
- `signals.version`/`lastUpdated` in `ontology.json` sind jetzt als eigenständig
  gepflegte Signaldatenbank ausgewiesen statt als scheinbarer Widerspruch.
- **Detektor-Abdeckung ausgewiesen:** Jeder Indikator trägt `detector`
  (`implemented` oder `documented_only`). Text und Code haben Detektoren; Bild,
  Video und Audio sind dokumentiert, aber von nichts berechnet — das steht jetzt
  in README und SKILL.md, statt Multimodalität zu suggerieren.

**Dokumentation existiert genau einmal.** `docs/de/` enthielt byte-identische
Kopien von neun deutschen Wurzeldokumenten (~2.000 Zeilen), abgesichert durch
eine Handpflege-Regel — die bereits versagte: Changelog und Referenzen waren
schon auseinandergelaufen.

- Die neun Kopien sind entfernt; `docs/de/README.md` verlinkt die Originale und
  behält nur, was es dort exklusiv gibt.
- `docs/en/README.md` bezeichnete die deutschen Wurzeldokumente als „canonical
  English entry points" — ersetzt durch eine Tabelle, welches Dokument tatsächlich
  in welcher Sprache vorliegt.
- `tests/test_documentation_layout.py` verhindert neue Kopien, prüft die
  Sprachangaben und alle relativen Links.

**Erweiterung: TTL vollständig, Parität geprüft.** Die elf Dimensionen existierten
nur als nackte Bezeichner im JSON — ohne Definition und ohne Entsprechung im
TTL, obwohl README und Doku sie als Bewertungsmodell führen.

- Jede Dimension hat jetzt Label und Definition (JSON) und ein
  `:Dimension`-Individuum (TTL); `human_work_seo_slop.json` ist eingerückt
  statt einzeilig, damit Änderungen im Diff lesbar sind.
- `check_consistency.py` prüft Typen und Dimensionen JSON ↔ TTL auch für die
  Erweiterung — bisher galt das nur für den Kern.

**Aufräumen.**

- `src/scorer.py:slop_score()` entfernt: eine zweite, unkalibrierte
  Aggregation mit eigener 14-Wort-Buzzwordliste, die außer ihrer eigenen Demo
  niemand aufrief. Die Primitiven bleiben; die Aggregation ist `SlopClassifier`.
- Beide Engines verstehen jetzt beide Namen (`score`/`overall_slop_score`,
  `signals`/`signals_detected`); `SignalMatch` trägt in beiden ein `severity`.
- `--json` rundet Confidences (vorher `0.7999999999999999`).

**Zitierte Beispiele verzerren die Bewertung nicht mehr.** Ein Dokument über
Slop zitiert Slop: README (0,93), Bedienungsanleitung (0,99) und das kanonische
Fachmodell (0,99) stuften sich selbst als `slop_candidate` ein — ausgelöst von
den Beispielen in Tabellen und Code-Fences.

- Neu `slopkit/_markdown.py`: entfernt Code-Fences, Blockquotes, Tabellenzeilen,
  Inline-Code und hervorgehobene Beispiel-Aufzählungen; Zeilenstruktur bleibt
  erhalten, damit Satz- und Absatzsignale weiter greifen.
- CLI: Markdown-Dateien werden per Default so bewertet; `--no-strip-quotes`
  bewertet wörtlich, `--strip-quotes` erzwingt es für stdin/Literaltext,
  `--json` weist den Modus als `quoted_markdown_stripped` aus.
- Wirkung: README 0,93 → 0,00, ONTOLOGY.md 0,93 → 0,00, Anleitung 0,99 → 0,56,
  kanonisches Dokument 0,99 → 0,59. Auf dem Korpus ändert sich nichts:
  27/29 Slop erkannt, 0 Falsch-Positive.
- Bewusst nicht entfernt: Fließtext-Aufzählungen ohne Zitatform (`report.md`
  bleibt bei 0,97) und starke Formatierung ohne Liste — Letzteres ist selbst
  ein Slop-Signal.

**Quellenprüfer meldet Abdeckung statt Zuversicht.** `verify_sources.py
--online` beendete einen Lauf, in dem keine einzige URL erreichbar war, mit
„no dead links" und Exit-Code 0.

- Neue Ausgabe: `Coverage: N/M verified reachable, K not checkable, D dead`.
- Unterhalb `--min-verified` (Default 0,5) endet der Lauf als *inconclusive*
  mit Exit-Code 1 — ein Lauf, der nichts prüfen konnte, ist kein Freibrief.
- HEAD-Ablehnungen (403/405/429) werden mit GET wiederholt, bevor sie als
  „nicht prüfbar" gelten.

**Ehrliche Benchmark-Zahlen.** `eval/run_benchmark.py` weist den Standardlauf
jetzt als *in-sample* aus — die Gewichte des Skill-Scorers werden von
`eval/calibrate.py` auf genau diesem Korpus optimiert — und kennt
`--cross-validate K` für eine Holdout-Schätzung (stratifizierte k-fache
Kreuzvalidierung, Neu-Kalibrierung auf k-1 Folds).

- Ergebnis bei 5 Folds: **Pipeline F1 0,978** (in-sample 0,982) — die Pipeline
  hält, weil ihr Typ-Muster-Klassifikator nicht auf den Korpus gefittet ist;
  der kalibrierte Scorer allein fällt von 0,906 auf **0,768** (Fold-Streuung
  0,333–1,0).
- Per-Sprache-Genauigkeiten unter fünf Beispielen werden nicht mehr als Zahl
  ausgegeben (`de=n/a (n=4)`), statt „1.0" aus zwei Sätzen zu behaupten.

**Human-, Work-, Management- und SEO-Slop-Erweiterung.** Neues Modul
`extensions/human-work-seo-slop/` — technologieneutral, ohne Eingriff in die
kanonische AI-Slop-Definition, den Klassifikator oder die Schwellenwerte.

- Drei Gruppierungsbegriffe (`HumanSlop`, `WorkSlopFamily`, `SEOSlop`), 27
  konkrete Typen, 11 querschnittliche Dimensionen, sieben SEO-Untertypen.
- **Workslop** bleibt eng KI-bezogen als `AIWorkslop`; `WorkSlopFamily` ist die
  separate Oberkategorie, damit menschliche, KI-gestützte und synthetische
  Formen koexistieren, ohne die Generierungsmodi zu vermischen.
- Evidenzstatus-Modell (`established`, `emerging`, `grounded_extension`,
  `candidate`) und verbindliche Falsch-Positiv-Regeln: klassifiziert werden
  Artefakte und Systeme, nie Personen.
- Artefakte: `human_work_seo_slop.json`, `human_work_seo_slop.ttl`,
  `examples.json` (Kandidaten und Gegenbeispiele), `RESEARCH.md`.
- `verify_sources.py` prüft die 20 zitierten Quellen offline auf Struktur und
  Datumsplausibilität; eigener CI-Schritt `verify-sources`.

**Microsoft-Ontology-Playground-Adapter.** `integrations/ontology-playground/`
mit sieben importierbaren RDF/XML-Ansichten (`ai-slop-core`, `ai-slop-media`,
`ai-slop-domains`, `ai-slop-intent`, `work-slop`, `management-slop`,
`seo-slop`), je `ontology.rdf` plus `metadata.json`, einem Manifest und
`validate_adapter.py` (XML, Metadaten, Entitätszahlen, Identifier, Beziehungen,
Manifest-Parität).

**Zweisprachige Dokumentation.** Englisch bleibt kanonisch für Code, Klassen,
Properties, YAML, JSON und RDF; deutsche Parallel-Dokumentation unter
`docs/de/` mit eigenem Index, `README.de.md` als deutschem Einstieg und
`docs/en/README.md` mit der Übersetzungsregel. Technische Identifier werden
nicht übersetzt; bei Widerspruch gilt das maschinenlesbare Artefakt.

- Testsuite: 69 → **87 Tests** (Erweiterungsstruktur, Falsch-Positiv-Regression,
  Playground-Adapter, Quellenprüfung).

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
