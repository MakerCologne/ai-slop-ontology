# METHODOLOGY.md — Methodik-Kodex der AI Slop Ontology

**Status:** konstitutiv (v2.0.0, Issue #63) · **Geltungsbereich:** jedes Signal, jeder Scorer-Change, jedes Eval-Artefakt in diesem Repo.
**Quelle:** Meta-Abstraktion über alle Issues #1–#62 (2026-08-24, `research/slop-ontology-gap-2026-08-24/meta-abstraktion.md` — externe Recherche, nicht Teil des Repos).

Dieser Kodex kodifiziert die Querprinzipien, die bisher nur implizit in Issue-Bodies, PR-Praxis (#17–#19) und Nachbesserungskommentaren verstreut waren. Die Qualitätsvarianz der Batches 1–2 (11 nachbesserungspflichtige Issues) war die direkte Folge dieser Lücke.

---

## 1. Die elf Querprinzipien (M1–M11)

Jedes Prinzip: Beschreibung · Anker-Issues · Durchsetzungsmechanismus.

### M1 — Test-Oracle-Pflicht / messbare Abnahmekriterien
**Beschreibung:** Jede Verhaltensänderung formuliert ein Test-Oracle *vor* Implementierung: exakte Matcherspezifikation, ≥1 Positiv- und Negativ-Fixture, Akzeptanzschwelle. Issues ohne Testkriterium wurden bisher explizit nachgebessert.
**Anker-Issues:** #17, #18, #19 (Maßstab-PRs), #20, #22, #23, #24, #26, #28, #29, #40, #41, #43, #52
**Durchsetzung:** TDD-Disziplin (Red-Commit vor Implementierung, siehe Burn-Log D002/D005) + DoD-Checkliste #64 (Punkt 1) + PR-Template #66 (Pflichtfeld Test-Oracle).

### M2 — Guard-/keep_when-Systematik gegen False Positives
**Beschreibung:** Jedes Signal wird mit einem Gegenmaß-Flügel geboren: `keep_when`-Dokumentation, Quote-/Pre-2022-Exemption, Genre-Register, Kumulativregel, Längen-Guards, Voice-Budget, Allowlisten. FP-Reduktion ist eine eigenständige Qualitätsdimension („False-Positive-Reduktion = Glaubwürdigkeit des Detektors", #23).
**Anker-Issues:** #7, #11, #23, #24, #26, #29, #31, #34, #42, #52, #56
**Durchsetzung:** DoD-Checkliste #64 (Punkt 2: FP-Abwägung dokumentiert — auch wenn Ergebnis „kein Guard nötig") + `scripts/check_signal_dod.py` (keep_when-Heuristik) + Genre-Profile (#42) im Scorer.

### M3 — SSOT / Single-Source-of-Truth
**Beschreibung:** Eine Quelle (ontology.json), generierte Sichten, CI-Parity-Gate. Dual-Darstellung (ontology.json + Inline-Python-Konstanten) ist ein aktiver Defekt. Gilt auch für Signal-Definitionen, Lexikon-Einträge und Referenzkorpora.
**Anker-Issues:** #46, #49, #50, #54, #55, #47
**Durchsetzung:** `scripts/check_consistency.py` (Parity-Gate, läuft je Batch) + ADR-0002 (#49) + DoD-Checkliste #64 (Punkt 3).

### M4 — Feedback-/Learning-Loops
**Beschreibung:** Statische Listen altern. Jede Detektionskomponente bekommt einen Lernpfad: not-slop-Feedback-Store, Sampling-Mining, Quartals-Re-Score, Drift-Messung, Score-Trajectory-Monitoring.
**Anker-Issues:** #12, #29, #36, #47, #59, #60, #61
**Durchsetzung:** Learning-Store (`--learn`, #29, mit Escalations-Schutz) + Re-Baseline-Kalender in SCORE-GOVERNANCE.md (#67) + Signal-`status`-Feld (Lebenszyklus, Abschnitt 2).

### M5 — Empirie/Benchmark vor Ausbau (Sequencing)
**Beschreibung:** Erst Fundament (Benchmark, Tokenizer, SSOT), dann Expansion (Sprachen, Signale, Medien). „Buzzword-Listen auf kaputtem Metrik-Fundament wären wertlos" (#53).
**Anker-Issues:** #41, #43, #49, #50, #53, #54, #42
**Durchsetzung:** depends-on-Deklaration im Issue-Template #66 + FP-Gate aus #41 in DoD #64 (Punkt 5) + Benchmark-Korpus-Disziplin (ADR-0005).

### M6 — Provenance & Belegpflicht
**Beschreibung:** Jede Behauptung braucht Herkunft: claim → source → quote. Zahlen ohne Quellenreferenz sind selbst ein Signal (fabricated proof metrics, #34). Jede Issue trägt Quellen-Links; PRs zitieren Primärquellen (arXiv-Nummern wo applicable).
**Anker-Issues:** #20, #25, #34, #36, #37, #39
**Durchsetzung:** Claim-Register-Disziplin im Burn-Log (D003) + Corpus-Verweis-Tests gegen den eigenen CHANGELOG (#34, Live-Ironie-Test) + Quellen-Pflichtfeld in Templates #66.

### M7 — Prozess-Zustandsmaschine mit Eskalation / Human-in-the-loop
**Beschreibung:** Fix-/Review-Prozesse sind endliche Zustandsmaschinen mit Exit-Kriterien und garantiertem Eskalationspfad: DETECT→TRIAGE→FIX→VERIFY→EXIT-CHECK; maxIter terminiert nie als „Erfolg", sondern ESCALATE (Anomalie → Human).
**Anker-Issues:** #30, #51, #59, #61, #62
**Durchsetzung:** Loop-Design-Report (E1–E5-Exit-Checks) + Signal-Lebenszyklus-Zustandsmaschine (Abschnitt 2) + Review-Pflicht je Batch (D005).

### M8 — Determinismus vor LLM
**Beschreibung:** Deterministische Layer (Regex, AST, Statistik) sind Layer 1 — reproduzierbar, CI-fähig. LLM nur als Layer-2-Veto/Befund, nie alleiniges Abbruchkriterium, mit Bias-Gegenmaßnahmen.
**Anker-Issues:** #20, #40, #55, #57, #58
**Durchsetzung:** Evals-Architektur #68 (L1 deterministisch / L2 Judge+Human) + ADR-0006 (detect-only-Module) + Hard-Gates im Scorer (#55).

### M9 — Goodhart-Resistenz / Mehrfach-Maße
**Beschreibung:** Kein einzelner Score darf alleiniges Ziel sein: Score + qualitative Guardrails + Stabilität + Voice-Non-Regression + Trajektorien-Anomalie + Human-Eskalation. „Ein Rewriter kann den Detektor optimieren statt die Qualität."
**Anker-Issues:** #51, #56, #58, #59, #62
**Durchsetzung:** SCORE-GOVERNANCE.md (#67): Optimierungs-Freigaben je Metrik, Guardrail-Pflicht, Re-Baseline-Kalender, Change-Protokoll.

### M10 — Minimum-Intervention / Voice-Erhaltung
**Beschreibung:** Detektion/Repair darf nicht in generische Glättung münden: Minimum-Effective-Edit, Token-Budget (β=25%), positive Gegenprofile als Zielbild, Over-Sanitization selbst als Signal („zu sauber ist selbst ein Signal").
**Anker-Issues:** #21, #30, #56, #60
**Durchsetzung:** Voice-Budget als Non-Regression-Gate (#56, referenziert in SCORE-GOVERNANCE.md) + Best-of-N-Auswahl nach Voice-Ähnlichkeit (#60).

### M11 — Forschungs-Pipeline mit verifizierten Primärquellen
**Beschreibung:** Fach-Änderungen entstehen ausschließlich aus belegten Deep-Dives (Primärquellen direkt verifiziert; Fehl-Recherchen werden korrigiert, z. B. #39). Forschung → konsolidierte Gap-Analyse → Issue ist ein fixer Trichter mit Duplikat-Check.
**Anker-Issues:** #37, #39 (und die Praxis aller Bodies: Quellen-Block + research/-Pfad)
**Durchsetzung:** Pflichtfelder „Corpus Evidence" + „Prior Art" in Issue-Template #66; Quellenkorrektur-Kultur (#39).

---

## 2. Signal-Lebenszyklus

Blaupausen: Clippy-Lint-Gruppen (`nursery`), ESLint-Rule-Deprecation-Policy, SpamAssassin-MassCheck-Rescore — Detail in `research/slop-ontology-gap-2026-08-24/methoden-fundament.md` §5 (externe Quelle).

```
nursery ──(FP-Gate auf #41-Korpus bestanden)──▶ beta
beta    ──(≥2 Korpus-Rekalibrierungen überlebt; Severity #55 fixiert)──▶ stable
stable  ──(ersetzt / Modellgeneration weg; Doku markiert)──▶ deprecated
deprecated ──(aus Default-Set entfernt; replaces-Nachfolger verlinkt)──▶ retired
beta/stable ──(schwerer FP-Rückfall, Gate rot)──▶ deprecated (Rückfallpfad)
```

**Zustände:**

| Zustand | Bedeutung | Score-Wirkung |
|---|---|---|
| `nursery` | Neu, unter Entwicklung; FP-Gate noch nicht bestanden | detect-only (kein Score-Einfluss) |
| `beta` | FP-Gate auf dem Hard-Negative-Korpus (#41) bestanden | vorläufiges Gewicht |
| `stable` | ≥2 Rekalibrierungs-Zyklen überlebt; Severity fixiert | volles Gewicht |
| `deprecated` | Ersetzt oder Modellgeneration weg; Doku markiert, **keine Fixes mehr** (ESLint-Regel) | Gewicht bleibt, wird aber bei Re-Baseline abgebaut |
| `retired` | Aus Default-Set entfernt, historisch referenzierbar | kein Score-Einfluss |

**Governance-Regeln:** (1) Gewichte werden nie „gefühlt" geändert, sondern aus Korpus-Statistik abgeleitet (SpamAssassin-Analogie); (2) jede Gewichtsänderung ist ein eigenes Changeset mit Re-Score gegen eingefrorenes Korpus (#47) und Change-Protokoll (#67); (3) Community-Einreichung über Signal-Proposal-Template (#66) mit Mindestevidenz; (4) Statuswechsel werden im CHANGELOG dokumentiert.

### `status`-Feld-Spezifikation für ontology.json

Jeder Signal-Eintrag in `ontology.json → signals` bekommt ein Pflichtfeld:

```json
{
  "signal_id": {
    "status": "nursery | beta | stable | deprecated | retired",
    "status_since": "YYYY-MM-DD",
    "replaces": "<signal_id | null>"
  }
}
```

- `status` (string, Pflicht): einer der fünf Zustände oben; Default für neue Signale ist `nursery`.
- `status_since` (ISO-Datum, Pflicht): Datum des letzten Zustandswechsels — Grundlage für Halbwertszeiten-Beobachtung (#36) und Re-Baseline-Kalender (#67).
- `replaces` (string|null, optional): Signal-ID des Vorgängers bei Migration; `retired`-Signale bleiben mit `replaces`-Nachfolger referenzierbar.
- Übergänge sind nur entlang der Zustandsmaschine oben erlaubt; ein Wechsel ist ein eigenes Changeset mit CHANGELOG-Eintrag und (bei Score-Wirkung) Governance-Protokoll (#67).

---

## 3. Referenzierte Issues (Konsistenz-Liste)

Alle in diesem Dokument referenzierten Issues (`#N`) müssen in dieser Liste stehen — geprüft von `scripts/check_methodology.py`:

#1, #7, #11, #12, #17, #18, #19, #20, #21, #22, #23, #24, #25, #26, #28, #29, #30, #31, #34, #36, #37, #39, #40, #41, #42, #43, #46, #47, #49, #50, #51, #52, #53, #54, #55, #56, #57, #58, #59, #60, #61, #62, #63, #64, #65, #66, #67, #68
