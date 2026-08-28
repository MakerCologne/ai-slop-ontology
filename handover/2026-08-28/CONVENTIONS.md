# CONVENTIONS.md — die Regeln dieses Repos

Nicht erfunden, sondern aus den konstitutiven Dokumenten und der gelebten Commit-Historie abgelesen. Wo eine Regel automatisch erzwungen wird, steht das dabei — die anderen musst du selbst einhalten.

---

## TDD, sichtbar in der Historie

Jedes Ticket bekommt **zwei Commits**:

```
test(#NN): RED  — <was der Test behauptet und warum er heute fehlschlägt>
feat(#NN): GREEN — <Ursache, Fix, Messung>
```

Der RED-Commit muss wirklich rot sein, und die Commit-Message sagt, wie rot (`RED: 4 Subtests failed`). Bei Fixes statt Features `fix(...)`. Beide Hashes gehören in den Issue-Kommentar.

Wenn du einen Test nach dem RED-Commit noch änderst, benenne das explizit — die Historie kennt dafür den Marker `TESTS_MODIFIED_AFTER_RED:` bzw. `FIXTURE_NACH_RED:`. Stillschweigend den Test an den Code anzupassen ist der Betrug, den TDD verhindern soll.

## Commit-Messages

Deutsch, ausführlich, mit Zahlen. Muster aus der Historie:

- Erste Zeile: `typ(#NN): STUFE — Kurzfassung`
- Body: Ursache, was geändert wurde, **Messung vorher/nachher**, Gate-Stand.
- Am Ende Suite-Zahl und Benchmark, damit man ohne Checkout sieht, ob sich etwas bewegt hat.

## Die vier Regeln, die automatisch erzwungen werden

1. **Jede neue Testdatei muss in `docs/EVALS.md`** einer Ebene (L1/L2/L3) zugeordnet sein. `check_methodology.py` schlägt sonst fehl — das ist der häufigste Grund, warum die Suite nach einem neuen Test rot wird.
2. **`ontology.json` ist SSOT.** Kopien und generierte Sichten prüft `check_ssot.py` (C1 Skill-Kopie, C2 generierte View, C3 Konstanten-Register, C4 DE-Phrase-Layer). Nach Änderungen an Signalen: `python scripts/generate_signal_defs.py`.
3. **Kein Dokument über 0.40** im Self-Check, außer registriert mit Begründung. `scripts/self_check_docs.py`.
4. **FP-Baseline und Control-Set** dürfen nicht driften.

## Score-Governance (`docs/SCORE-GOVERNANCE.md`, konstitutiv)

- `slop_score` ist Messgröße, **nie Zielfunktion**.
- Threshold 0.40 ist gesperrt außerhalb einer Re-Baseline.
- Precision auf Hard Negatives darf nur nach oben. Jede Verschlechterung blockt.
- Gewichte nur aus Korpus-Statistik, nie „gefühlt", je Änderung eigenes Changeset.
- Jede score-wirksame Änderung braucht ein **Change-Protokoll**: vorher/nachher über `eval/corpus.jsonl`, mit expliziter Aussage, ob ein Hard Negative sich bewegt hat.

Das Muster dafür (aus #83):

```
geänderte Texte: 1 von 330
  slop-0202-016 [slop]  0.280 → 0.496
Hard Negatives verändert: 0
```

## Signal-DoD (`docs/SIGNAL-DOD.md`)

Jedes neue Signal: **3 Positiv-, 3 Negativ-, 2 Grenzfixtures**, plus SSOT-Eintrag mit `status`, Quellenbeleg, Benchmark-Referenz, Kollisions-Check (#46). Neue Module sind per adr/0006 **detect-only** — kein Score-Einfluss ohne eigenes Ticket.

## Zwei Engines, absichtlich

`src/` und `skills/ai-slop-detection/scripts/` duplizieren die Kernlogik. Der Skill muss self-contained bleiben, weil er einzeln in Agent-Umgebungen kopiert wird. `tests/test_engine_sync.py` pinnt das Verhalten.

**Praktische Folge:** Wenn du eine Matching-Funktion änderst, ändere sie in **allen** Kopien. Bei `_term_pattern` waren es drei Module — `src/scorer.py`, `skills/…/slop_scorer.py` und `skills/…/genre_profiles.py`. Das dritte war leicht zu übersehen und hätte dazu geführt, dass Genre-Exemptions andere Spans strippen als der Scorer matcht.

## Doku-Stil (`docs/DOC-STYLE.md`)

Zitiertes Material gehört in Markup, eigene Aussagen in Fließtext. Der Präpass entfernt nur, was Markup als Zitat ausweist. **Umformulieren, bis der Detektor schweigt, ist ausdrücklich verboten** — siehe `PITFALLS.md` §6.

## PR-Template

`.github/PULL_REQUEST_TEMPLATE.md` hat Pflichtfelder: Corpus Evidence, Test-Oracle mit RED-Hash, FP-Analyse, Prior Art, Signals-DoD-Abhaken, Governance. Wo etwas nicht zutrifft, schreib „nicht zutreffend, weil …" statt es wegzulassen.

## Sprache

Issues, Kommentare, Commit-Messages, CHANGELOG: **deutsch**. Code-Kommentare und Docstrings: englisch. `docs/USER-GUIDE.md` ist englisch, die Governance-Dokumente sind deutsch. Halte dich an das, was in der jeweiligen Datei schon steht.

## Was einen Merge blockiert

Ein PR ist fertig, wenn alle acht Gates grün sind **und** das Change-Protokoll steht **und** das Issue kommentiert ist. Solange Actions deaktiviert ist (#100), fahre die Gates lokal und **sag im PR ausdrücklich, dass es lokal war**. Behaupte nie CI-Grün, das du nicht gesehen hast.
