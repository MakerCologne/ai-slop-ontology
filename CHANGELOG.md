# Changelog

## [Unreleased]

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
