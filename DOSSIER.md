# Repository-Dossier: `ai-slop-ontology`

**Erstellt:** 2026-08-27 · **Analysierter Stand:** Commit `b2a7bb0`, Branch `claude/repository-dossier-x9lpyc` (identisch mit `master`)
**Remote:** https://github.com/MakerCologne/ai-slop-ontology
**Methodik:** vollständige Datei-Inventur, Ausführung aller Test-, Benchmark- und Gate-Skripte, Auswertung von `ontology.json`, `eval/corpus.jsonl`, CHANGELOG und Doku-Korpus. Alle Zahlen in diesem Dossier sind **selbst gemessen**, nicht aus der Repo-Doku übernommen; Abweichungen zwischen Doku-Claims und Messung sind in Kapitel 12 aufgeführt.

---

## 1. Kurzprofil

| Merkmal | Wert |
|---|---|
| Zweck | Strukturierte, agenten-konsumierbare Wissensbasis + deterministische Detection-Engine für „AI Slop" |
| Typ | Hybrid: Ontologie/Wissensbasis (JSON/YAML/TTL/Markdown) **plus** Python-Toolkit (CLI, Skill, Eval-Harness) |
| Kanonische Version | **2.5.0** (2026-08-25) — Quelle: Front-Matter `AI-SLOP-ONTOLOGY.md`, gespiegelt in `ai_slop_ontology.yaml` und CHANGELOG |
| Lizenz | CC BY 4.0 (Dokumente, Daten **und** Code) |
| Sprache | Bilingual: Doku/Prozess überwiegend Deutsch, Code/Signal-IDs/Ontologie-Terme Englisch |
| Laufzeit-Abhängigkeiten | **keine** — Detektor läuft rein auf der Python-Standardbibliothek (`pyyaml` nur optional für YAML-Checks) |
| Python | `>=3.9` (CI: 3.11) |
| Dateien gesamt | 265 (ohne `.git`) |
| Python-LOC | 15.241 |
| Commits | 50 (2026-08-25 00:59 → 2026-08-25 15:25, also **ein einziger Arbeitstag**) |
| Autoren | `Hertha (BTM)` (29), `issue-burner <burner@btm.one>` (13), `hikaman` (8) |

**Charakterisierung in einem Satz:** Ein hochdiszipliniert entwickeltes, TDD-getriebenes Detektor-Repo, das seine eigene Anti-Slop-Doktrin (Belegpflicht, ehrliche Zahlen, Detect-only) auf sich selbst anwendet — mit einer ungewöhnlich dichten Governance-Schicht (ADRs, Methodik-Kodex, Signal-DoD, Score-Governance) im Verhältnis zur Codemenge.

---

## 2. Was das Repo inhaltlich behauptet

### 2.1 Kerndefinition

AI Slop ist **kein** Synonym für „KI-generierter Inhalt", sondern ein **Risikoprofil** mit drei notwendigen Bedingungen (alle müssen erfüllt sein):

1. Generative KI ist die **primäre Quelle** des Inhalts.
2. Menschliche Sorgfalt, Kuratierung oder Verifikation ist **abwesend**.
3. Der Inhalt wird **unaufgefordert distribuiert** (push, nicht pull).

Explizite Ausschlussregel: sorgfältig kuratierte, verifizierte, absichtlich publizierte KI-Ausgaben sind **kein** Slop.

Drei konvergente Lexikon-Definitionen werden als Fundament zitiert: Merriam-Webster (Word of the Year 2025), Oxford (Shortlist 2024), Willison-Kriterium („mindlessly generated and thrust upon someone who didn't ask for it").

### 2.2 Klassen- und Typen-Taxonomie

- **Top-Level-Klassenhierarchie:** `ContentItem → SyntheticContent → AI_SlopCandidate → ConfirmedAI_Slop`, insgesamt 13 Top-Level-Klassen (u. a. `LowQualityHumanContent`, `SpamContent`, `MisinformationContent`, `SlopProducer`, `DistributionChannel`, `DetectionEvidence`, `MitigationAction`).
- **Properties:** `hasGenerationMode`, `hasHumanOversightLevel`, `hasQualityProfile`, `hasDistributionPattern`, `hasIntent`, `hasProvenanceStatus`, `hasRiskProfile`, `hasSlopScore`.
- **Slop-Typen nach Medium (8 Gruppen in `ontology.json → slopTypes`):**
  - `TEXT_SLOP` (5): GenericSlop, PseudoInsightSlop, FakeAuthoritySlop, WikipediaRehash, WellnessSlop
  - `IMAGE_SLOP` (3): SurrealEngagementBait, FakePhotographSlop, FakeProductImageSlop
  - `VIDEO_SLOP` (1): AIGeneratedVideo
  - `AUDIO_SLOP` (1): FakeArtistMusic
  - `CODE_SLOP` (2): HallucinatedPackage, UniformCode
  - `DOMAIN_SLOP` (6): SEOSlop, AcademicSlop, PoliticalSlop, ReviewSlop, SecurityReportSlop, PeerReviewSlop
  - `BY_PURPOSE` (5) und `BY_FORM` (3) als quer laufende Achsen
- **Typ-Muster mit eigener Phrase-Signatur (12):** SEOContentFarmSlop, AcademicSlop, FakeAuthoritySlop, WellnessSlop, WikipediaRehash, EngagementClickbaitSlop, PropagandaDisinfoSlop, Workslop, LegalSlop, LinkedInSlop, SecurityReportSlop, PeerReviewSlop (je 4–10 Muster, Konfidenz 0.8; ≥2 Treffer eines Typs gelten als entscheidendes Indiz).
- **Intent-Taxonomie (11):** AttentionFarming, AdRevenueFarming, RoyaltyDilution, SearchManipulation, RecommendationPoisoning, AffiliateFunnel, CredentialInflation, Disinformation, CarelessSpeech, Impersonation, PlaceholderPublishing.
- **Medien-Taxonomie (8):** Text-, Image-, Video-, Audio-, Academic-, Code-, Legal-, WorkSlop.

### 2.3 Qualitäts- und Systemdimensionen

- **Shaib et al. 2025 (11 Dimensionen):** Information Utility (Density IU1, Relevance IU2), Information Quality (Factuality IQ1, Bias IQ2), Style Quality (Repetition SQ1, Templatedness SQ2, Coherence SQ3, Fluency SQ4, Verbosity SQ5, Word Complexity SQ6, Tone SQ7).
- **Madsen & Puyt 2025 — 7Vs:** Volume, Velocity, Variety, Value, Verification, Visibility, Virality.
- **Prototypische Eigenschaften (Kommers et al.):** SuperficialCompetence, AsymmetricEffort, MassProducibility.
- **Knowledge-Collapse-Stadien (Keisha et al., arXiv:2509.04796):** Stage A (Fakten korrekt), **Stage B (confidently wrong — als gefährlichste Stufe markiert)**, Stage C (inkohärenter Zusammenbruch).
- **Slopness-Scoring-Achsen (10):** syntheticity, quality_deficit, substance_deficit, verification_deficit, effort_asymmetry, mass_production, deceptiveness, distribution_manipulation, harm_potential, retrieval_risk.

### 2.4 Harms und normative Rahmungen

**12 Harm-Typen** (je mit Mechanismus und Quelle): model_collapse, epistemic_pollution, misinformation, trust_erosion, workplace_productivity_loss, creator_squeeze, harm_to_children, ad_fraud_brand_safety, cognitive_load, environmental_cost, democracy_risk, royalty_fraud.

**10 normative Framings:** EpistemicPollution, AutomationBias, IllegitimateReasonGiving, NonconsensualImposition, AttentionEconomyExploitation, ConsumerFraud, SecurityRisk, DemocraticHarm, SupplyChainAttack, EngagementFarming.

### 2.5 Empirische Schlüsselzahlen (Stand des Repos: Juli/August 2026)

| Kennzahl | Wert | Quelle laut Repo |
|---|---|---|
| KI-Content-Farm-Sites | 3.749 (23.06.2026) | NewsGuard |
| Neue Farmen/Monat | 300–500 | NewsGuard |
| KI-Anteil in Google-Ergebnissen | 19 % (Jan 2025) | Graphite |
| YouTube-Kids-Slop | ~40 % | NYT |
| Workslop-Empfänger | 40 % der Beschäftigten | HBR 2025 |
| Rework-Zeit je Workslop-Instanz | ~1 h 56 min | HBR 2025 |
| Package-Halluzinationsrate | 19,7 % | USENIX Security 2025 |
| KI-Anteil neuer Deezer-Uploads | 44 % (~75k Tracks/Tag), 1–3 % der Streams, ~85 % Fraud | Deezer Apr 2026 |
| Von Spotify entfernte Spam-Tracks | 75 Mio.+ (12 Monate bis Sep 2025) | Spotify |
| Journal-Einreichungen seit ChatGPT | +42 %, >30 % der Peer Reviews KI-beteiligt | Organization Science 2026 |
| curl-Bug-Bounty-Slop | ~20 % der Reports; Programm im Feb 2026 eingestellt | Stenberg |

---

## 3. Repository-Struktur (vollständig)

```
ai-slop-ontology/
├── README.md                     Einstieg, CLI-Übersicht, Statistiken
├── AI-SLOP-ONTOLOGY.md           Kanonisches Dokument, 14 Abschnitte, Front-Matter trägt die Version
├── ai_slop_ontology.yaml         Maschinenlesbare YAML-Sicht
├── ontology.json                 SSOT — 155 KB, 47 Top-Level-Keys, 627 Dict-Knoten
├── ontology.ttl                  RDF/Turtle-Sicht (Namespace http://btm.one/ontology/ai-slop#)
├── ONTOLOGY.md                   Menschenlesbare Taxonomie-Übersicht
├── ONTOLOGY-STRUCTURE.md         Property-basiertes Modell, Klassenhierarchie
├── REFERENCES.md                 39 nummerierte Quellen in 7 Sektionen
├── CHANGELOG.md                  55 KB, 20 Versionseinträge (1.0.0 → 2.5.0)
├── REVIEW-2026-07.md             Deep-Review-Audit (Code + Daten), Befundliste v1.0→v1.1
├── report.md / report-extended.md / RESEARCH-v0.1.md   Forschungsberichte Runde 1/2/v0.1
├── LICENSE                       CC BY 4.0
├── pyproject.toml                setuptools, Paketname `slopkit`, Entry-Point `slop`
│
├── adr/                          8 Architecture Decision Records (MADR-Format)
├── docs/                         7 Dokumente: EVALS, METHODOLOGY, SCORE-GOVERNANCE,
│                                 SIGNAL-DOD, USER-GUIDE, LEXIKON, de-coverage
├── eval/                         Benchmark-Harness + 5 Datenartefakte
├── examples/                     4 Beispiel-JSONs + Loop-Demo
├── lexikon/                      Schema-first-Glossar: entries/ (SSOT) → dist/ (Build)
├── scripts/                      9 Werkzeuge: Gates, Generatoren, CLIs
├── skills/ai-slop-detection/     Self-contained Agent-Skill (SKILL.md + 26 Module + 3 Referenzen)
├── slopkit/                      `slop`-CLI (4 Dateien, 414 LOC)
├── src/                          Zweite Engine + Loop-Runner (4 Dateien, 1.192 LOC)
├── tests/                        60 Testdateien, 540 `def test_`, 6.827 LOC
└── .github/                      CI-Workflow + 2 Issue-Templates + PR-Template
```

**Auffälligkeit:** Die Testsuite (6.827 LOC) ist größer als der gesamte Produktivcode der Detection-Module (4.896 LOC in `skills/.../scripts/`). Das Test-zu-Code-Verhältnis liegt bei etwa 1,4:1.

---

## 4. Architektur

### 4.1 Zwei-Engine-Design (bewusst dupliziert)

| Engine | Pfad | Rolle | Gemessene Leistung |
|---|---|---|---|
| **Skill-Pipeline** | `skills/ai-slop-detection/scripts/slop_scorer.py` + `slop_classifier.py` | Produktiv-Detektor, self-contained (kopierbar in Agent-Umgebungen) | **P 1.0 / R 0.995 / F1 0.998** |
| **Skill-Scorer allein** | `slop_scorer.py` | Nur Scoring ohne Klassifikator-Eskalation | P 1.0 / R 0.982 / F1 0.991 |
| **src-Klassifikator** | `src/classifier.py` + `src/scorer.py` | Bibliotheks-Engine, Basis der CLI | P 1.0 / R 0.502 / F1 0.669 |

Die Duplikation ist in `REVIEW-2026-07.md` als **bewusste Entscheidung** dokumentiert: Der Skill muss allein lauffähig sein. Verhaltensparität wird stattdessen über `tests/test_engine_sync.py` gepinnt. Der große Recall-Abstand des `src`-Klassifikators (0.502 vs. 0.995) ist eine reale, nicht explizit im README beworbene Asymmetrie — die CLI (`slopkit`) nutzt die **schwächere** Engine.

### 4.2 SSOT-Kette

```
ontology.json  (Single Source of Truth, ADR-0002)
     ├──▶ src/signal_defs_generated.py   (generiert via scripts/generate_signal_defs.py, "DO NOT EDIT")
     ├──▶ ontology.ttl / ai_slop_ontology.yaml  (Parity-Gate: scripts/check_consistency.py)
     ├──▶ skills/ai-slop-detection/scripts/*  (Inline-Konstanten, 70 registrierte Abweichungen)
     └──▶ Konsistenzprüfung: scripts/check_ssot.py (C1–C4)
```

`scripts/check_ssot.py` prüft vier Kriterien:
- **C1** — Ontology-Kopie im Skill identisch zur Wurzel
- **C2** — generierte Sicht `signal_defs_generated.py` aktuell
- **C3** — **70 Signal-Konstanten** in 12 Modulen registriert, mit 10 dokumentierten Abweichungsgruppen (Quellen-Kategorien: `ontology.json` / `corpus-calibrated` / `engine-config` / `closed-list`; Status: `synced` / `deviation` / `fixture-calibrated`)
- **C4** — DE-Phrase-Layer: 16 Kategorien × ≥6 Items gepinnt, Evidence-Regel je Phrase, Wikipedia-Namespace-Präfix-Check, Coverage-Pin ≥50 % für Doppelbelege

Die C3-Abweichungen sind **kein Defekt, sondern ein dokumentierter Zustand**: Der Scorer trägt korpus-kalibrierte Inline-Listen (17 Phrase-Kategorien, 112 Buzzwords), die absichtlich von der Ontologie (28 Kategorien, 113 Buzzwords) abweichen. Die vollständige Migration auf die generierte Sicht ist ein dokumentierter offener Follow-up.

### 4.3 Detect-only-Doktrin (ADR-0006)

Der entscheidende Architekturhebel: **Neue Signale bekommen standardmäßig keinen Score-Einfluss.** Sie melden benannte Findings mit zitierter Evidenz für menschliche Prüfung. Score-Wirkung erfordert Kalibrierung, Hard-Negative-Messung und Governance-Freigabe.

Von den 26 Skill-Modulen sind **score-wirksam** nur: `slop_scorer` und `slop_classifier` (Kern), `provenance_signals` (mit Score-Floor), `portability` (Gewicht 0.02), `fp_guards`, `genre_profiles`, `input_norm`, `learning_store`, `tokenizer` (Infrastruktur). **Alle übrigen 17 Module sind detect-only.**

---

## 5. Die Detection-Engine im Detail

### 5.1 Signaldatenbank (`ontology.json → signals`)

Gemessen über `python3 -m slopkit info`: **378 Signale**.

| Gruppe | Umfang |
|---|---|
| Buzzwords | 113 in 4 Tiers: tier1_critical 20 (conf 0.9), tier2_high 47 (0.8), tier3_moderate 27 (0.6), tier4_weak 19 (0.4) |
| Phrasen | **249 Items in 28 Kategorien** — 153 EN in 12 Kategorien, **96 DE in 16 `de_*`-Kategorien** (je 6 Items, conf 0.6, Evidence-Pflicht) |
| Strukturelle Indikatoren | 7 (ExcessiveEmDash, UniformSentenceLength, NumberedListOveruse, MirroredIntroConclusion, BalancedStructure, ExcessiveHedging, PerfectGrammarUniformTone) |
| Interpunktions-Indikatoren | 9 (EmDashExcess, EllipsisExcess, ExclamationExcess, BoldFormatting, EmojiInProfessional, TitleCaseHeadings, CurlyQuotes, HyphenatedPairRate, BoldMidSentence) |
| Typ-Muster | 12 Typen mit je 4–10 Phrasen |
| Rhetorische Muster (detect-only) | 15 |
| Mehrsprachige Marker | 6 Sprachen: DE 15, FR 8, ES 6, HI 10, VI 9, UR 8 |
| Modalitäts-Indikatoren | Image 10, Video 5, Code 6, Audio 4 |

**Die 12 EN-Phrase-Kategorien:** hedging_qualifiers (18), generic_transitions (21), opening_formulas (13), closing_formulas (14), metaphor_abuse (24), listicle_tells (16), authority_claims (8), emphasis_crutches (8), meta_commentary (8), rhetorical_setups (8), vague_declaratives (6), weasel_attribution (9).

**Die 16 DE-Kategorien** (je 6 Items): de_calque, de_ai_vocab, de_authority_floskel, de_meta_comment (aus #77) sowie de_transitions, de_recap, de_superlativ, de_symbolik, de_vague_authority, de_participle, de_binary_contrast, de_false_range, de_opening, de_closing, de_hedging, de_announcement_cleft (aus #76 Teil 2). Jede Phrase trägt ein `evidence`-Feld; 63 von 96 (65,6 %) haben ≥2 unabhängige Belege.

**Die 15 rhetorischen Muster** (detect-only, je mit `example_slop`, `example_fix`, `keep_when`): BinaryContrast (0.7), ColonReveal (0.55), SuperficialAnalysis (0.7), NegativeListingFragmentation (0.65), FakeStrongVerb (0.6), SynonymCycling (0.6), HollowKickerRecap (0.6), FormattingSlop (0.55), RoboticRhythm (0.5), ThroatClearing (0.6), FauxInsightSetup (0.65), ImportancePuffery (0.6), ForcedTriad (0.55), RepeatedOpenings (0.55), ChatbotLeftover (0.8).
Attribution im Datensatz: adaptiert von `petergyang/no-ai-slop` (MIT) und Wikipedia „Signs of AI writing".

### 5.2 Scoring-Formel

Zwei parallele Formeln im Repo:

**(a) Noisy-OR (Ontologie/`src/classifier.py`, seit v1.2.0):**
```
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, 1 − Π(1 − weights[severity] × confidence))
is_slop = (slop_score >= 0.4) OR (irgendein critical) OR (>= 2 high)
```
Begründung: Unabhängige Evidenz akkumuliert, statt im Mittelwert verwässert zu werden (Befund 6 in REVIEW-2026-07).

**(b) Gewichtete Summe (Skill-Scorer, kalibriert 2026-07 via `eval/calibrate.py`):**
17 Dimensionen mit Gewichten, die absichtlich >1 summieren (Kappung bei 1.0):
`burstiness .30 · phrases .30 · punctuation .30 · buzzwords .26 · fake_authority .18 · repetition .18 · density .15 · structural .08 · trailing_moral .06 · mirrored .05 · list_heavy .04 · verbosity .04 · multilingual .04 · portability .02` (+ adverb, copula, provenance über `weights.get`).

**Eskalationsregeln im Skill-Scorer:**
- **Provenance-Floor:** ≥1 Pipeline-Artefakt (z. B. `oaicite`, `turn0search0`) hebt den Score auf mindestens 0.40.
- **Zwei-Familien-Regel:** ≥2 starke Signalfamilien (buzz ≥0.5, phrase ≥0.5, authority ≥0.5, trailing moral, mirrored intro/conclusion, hochkonfidente Einzelkategorie, Provenance) heben ebenfalls auf 0.40.
- Beide Floors gelten **unabhängig von Genre-Anhebungen** in ihrer ursprünglichen Stärke.

### 5.3 Schwellen und Risikostufen

| Score | Skill-Risikostufe | Ontologie-Klasse | Agentenverhalten |
|---|---|---|---|
| 0.00–0.24 | 🟢 Clean | LowSlopRisk | Normale Nutzung, übliche Quellenprüfung |
| 0.25–0.39 | 🟡 AI-Assisted | ModerateSlopRisk | Nur mit Gegenprüfung |
| 0.40–0.69 | 🟠 Suspicious | HighSlopRisk | Nicht als Primärquelle, Human Review |
| 0.70–0.89 | 🔴 Slop | AISlopCandidate | Nicht zitieren, nicht als Fakt speichern |
| 0.90–1.00 | ⚫ Malicious/Severe | — | Blockieren, flaggen |
| beliebig + hoher Schaden | — | CriticalReviewRequired | Immer eskalieren (Recht, Medizin, Kinder) |

Entscheidungsschwelle **0.40** ist per `docs/SCORE-GOVERNANCE.md` **gesperrt** — Änderung nur im Re-Baseline-Zyklus mit vollständiger Vorher/Nachher-Messung.

### 5.4 False-Positive-Infrastruktur (der eigentliche Schwerpunkt)

Der FP-Schutz ist die am dichtesten ausgebaute Achse des Repos — fünf voneinander unabhängige Schichten:

1. **Quote-Exemption** (`fp_guards.py`, #23): Zitierte Passagen >40 Zeichen werden vor dem Signal-Matching entfernt. Ein Review, das ein Slop-Beispiel zitiert, erbt dessen Signale nicht. Strukturelle Dimensionen (Dichte, Burstiness, Repetition) messen weiterhin den Volltext.
2. **Kumulativregel:** Eine Phrase-Kategorie zählt erst ab 2 Treffern (`PHRASE_MIN_HITS`), generische Watchlist-Phrasen erst ab 3 (`GENERIC_PHRASE_MIN_HITS`, FU-12).
3. **Genre-Opt-in** (`genre_profiles.py`, #42/ADR-0004): 4 Profile, explizit via `--genre` — **keine Auto-Erkennung** (bewusste Entscheidung: Auto-Genre wäre selbst ein unzuverlässiges ML-Subsystem).

   | Genre | exempt_terms | zero_weights | Schwelle |
   |---|---|---|---|
   | legal | 10 (pursuant to, notwithstanding, hereinafter …) | burstiness | 0.55 |
   | academic | 7 (furthermore, moreover, it is important to note …) | burstiness, verbosity | 0.55 |
   | marketing | 8 (cutting-edge, game-changer, best-in-class …) | — | 0.50 |
   | technical | 4 (best practices, robust, scalable, seamless) | list_heavy | 0.45 |
4. **Learning-Store** (`learning_store.py`, #29): `not_slop.jsonl` mit geprüften False Positives; eine Signalfamilie wird ausgeschlossen, wenn Signal-ID **und** Sample-Hash im Store stehen. Eskalationspfade sind gegen Aushebelung geschützt.
5. **FP-Baseline-Register** (`scripts/fp_baseline.py` + `eval/fp_baseline.json`, #80): Snapshot der tolerierten Detektor-Ausgaben je Hard-Negative-Fixture (109 Fixtures, `score_tolerance` 0.02). `--check` schlägt bei Drift-Typen `signal_added`, `signal_removed`, `score_drift`, `fixture_missing`, `fixture_unknown` fehl — FP-Druck wird sichtbar, **bevor** das 0.40-Gate bricht.

Ergänzend: **Null-Edit-Contract** (`tests/test_null_edit_contract.py`, #79) als L1-Gate — Whitespace-/Reflow-Änderungen dürfen das Verdikt nicht ändern (Score-Drift ≤0.05); Grenzband-Register `eval/hardneg_borderline.json` hält die fünf riskantesten Hard Negatives (0.315–0.342) sichtbar.

### 5.5 Anti-Evasion

`input_norm.py` (#40) normalisiert **vor jeder Metrik**: Homoglyphen, Zero-Width-Zeichen, BOM, Bidi-Marker. Damit lassen sich Signale nicht durch Unicode-Obfuskation von „delve" umgehen. `tokenizer.py` (#43) liefert CJK-fähige Tokenisierung, weil Whitespace-Tokenisierung Dichte/Repetition/Burstiness bei chinesisch/japanisch/koreanischem Text bedeutungslos macht.

---

## 6. Modulinventar

### 6.1 Skill-Module (`skills/ai-slop-detection/scripts/`, 26 Dateien, 4.896 LOC)

| Modul | Issue | Score-wirksam | Funktion |
|---|---|---|---|
| `slop_scorer.py` (53 KB) | Kern | **ja** | Hauptdetektor, 17 Dimensionen, CLI mit `--diff`, `--anchor-diff`, `--json`, `--genre`, `--learn` |
| `slop_classifier.py` (16 KB) | Kern | **ja** | Typ-Klassifikation, Eskalation, Countermeasures |
| `fp_guards.py` | #23 | ja (Guard) | Quote-Exemption, Kumulativregel, zentrale Schwellen |
| `genre_profiles.py` | #42 | ja (Guard) | 4 Genre-Register, Opt-in |
| `input_norm.py` | #40 | ja (Pre) | Homoglyph-/ZWS-/Bidi-Normalisierung |
| `tokenizer.py` | #43 | ja (Pre) | CJK-fähige Tokenisierung |
| `learning_store.py` | #29 | ja (Guard) | FP-Feedback-Store |
| `provenance_signals.py` | #20 | **ja (Floor)** | Pipeline-Artefakte (`oaicite`, `turn0search0`, PUA-Unicode) |
| `portability.py` | #14 | ja (0.02) | Anteil kontextloser Sätze (keine Eigennamen/Zahlen/Zitate) |
| `rhetorical_patterns.py` (24 KB) | #17 | nein | 15 rhetorische Muster mit Evidenz + `keep_when` |
| `micro_patterns.py` | #13 | nein | Satzebene-Tics (inanimate subjects, grand endpoints, recap openers) |
| `markup_anomalies.py` | #28 | nein | 5 Markdown-Struktur-Tells |
| `quantifiers.py` | #25 | nein | Universalquantoren, Autoritätsansprüche |
| `proof_metrics.py` | #34 | nein | Fabrizierte Metriken („98 % Genauigkeit" ohne Quelle) |
| `instruction_slop.py` | #33 | nein | CLAUDE.md/AGENTS.md-Slop (nicht handlungsfähige Anweisungen) |
| `rhythm_openers.py` | #27 | nein | Prosarhythmus, Satzanfangs-Wiederholung |
| `code_slop.py` | #9 | nein | Code-Slop (halluzinierte Pakete, Secrets, Kommentar-Bloat) |
| `generated_docs.py` | #31 | nein | „Agent bootete und schrieb sofort ARCHITECTURE.md" |
| `reinventing_wheel.py` | #32 | nein | Near-Duplicate-Funktionen (Ratcliff/Obershelp >0.8) |
| `diff_mode.py` | #10 | nein | Nur geänderte Zeilen eines git-Range bewerten |
| `anchor_diff.py` | #78 | nein | Anker-Drift (Zahlen, Zitate, URLs, DOIs) zwischen Versionen; Locale-kanonisch („3.5" == „3,5") |
| `naturalness_guard.py` | #81 | nein | `register_drift`, `over_sanitized` (conf ≤0.45); `modal_particle_anomaly` = expliziter Stub |
| `de_typography.py` | #76 T1 | nein | M46–M49: falsche dt. Anführungszeichen, Title-Case-Header, EN-Zahlenformat, Genitiv-Apostroph |
| `structure_metrics.py` | #76 T2 | nein | M60 SynonymRotation, M61 Isometrie, M66 Fake-Analyse-Anhang, M71 Scheinnuance |
| `register_profile.py` (11 KB) | #74 | nein | 9-Feld-JSON-Stilkarte + `register_drift_intern` (Distanz zwischen Dokumenthälften) |
| `discourse_metrics.py` | #72 | nein (**explorativ**) | `rank_without_criterion`, `identical_enumeration` (conf ≤0.35, `exploratory: True`) |

### 6.2 Werkzeuge (`scripts/`, 9 Dateien, 1.458 LOC)

| Skript | Rolle |
|---|---|
| `check_ssot.py` (21 KB) | SSOT-Gate C1–C4 |
| `check_consistency.py` | JSON↔TTL↔YAML↔Skill-Parity (CI-Gate) |
| `check_methodology.py` | Kodex-/ADR-/Governance-/EVALS-Konsistenz |
| `check_signal_dod.py` | Signal-DoD-Report (`--strict` für CI-Gate) |
| `fp_baseline.py` | FP-Register `build` / `compare` / `drift` / `--check` |
| `generate_signal_defs.py` | Erzeugt `src/signal_defs_generated.py` aus `ontology.json` |
| `build_lexikon.py` | Lexikon-Build + `--check`-Sync-Gate |
| `code_slop_check.py` | CLI für Code-Slop-Modul |
| `deslop_loop_cli.py` | CLI für den Loop-Orchestrator |

### 6.3 `src/` und `slopkit/`

- `src/classifier.py` (24 KB): `SlopClassifier` mit `classify_text`, `classify_code`, `get_signal_stats`; Datenklassen `SignalMatch`, `DimensionResult`, `ClassificationResult`.
- `src/scorer.py` (7 KB): niedrigstufige Messfunktionen (`information_density`, `repetition_ratio`, `burstiness`, `buzzword_score`, `punctuation_anomaly_score`, `trailing_moral`, `list_heavy`) — komponierbar für eigene Pipelines.
- `src/deslop_loop.py` (14 KB): siehe Kapitel 7.
- `src/signal_defs_generated.py`: generierte, code-freie Datenprojektion.
- `slopkit/`: `cli.py` (10 KB, 9 Subcommands), `_engine.py` (komponierter Adapter über `src/classifier` + `rhetorical_patterns`), `__main__.py`, `__init__.py`. Umgebungsvariablen `SLOP_REPO_ROOT` und `SLOP_ONTOLOGY` erlauben abweichende Layouts.

---

## 7. DESLOP-LOOP-Orchestrator (#51)

Zustandsmaschine `DETECT → TRIAGE → FIX-CALLBACK → VERIFY → EXIT-CHECK` mit Rollback-Kante und garantiertem Eskalations-Terminal.

**Zentrale Designentscheidung (ADR-0001):** Der Runner **schreibt selbst nicht um**. Der FIX-Schritt ist ein injizierbarer Callback `fix(text, findings) -> candidate`. Ohne Callback läuft der Loop im Audit-Modus und eskaliert ehrlich. Der löschbasierte Demo-Fixer liegt ausschließlich in `examples/deslop_loop_demo.py`, nicht im Produktpfad.

**Exit-Checks:**

| Check | Bedingung | Verdikt |
|---|---|---|
| E1 | Score < Threshold | EXIT-OK (zusammen mit E2/E4) |
| E2 | keine kritischen Signale | EXIT-OK |
| E3 | ε-Stagnation (2 akzeptierte Iterationen mit Δ < ε) | **EXIT-ESCALATE** |
| E4 | keine inkubierten Signale (bestätigte Menge ⊆ Baseline) | EXIT-OK |
| E5 | maxIter = 5 erreicht | **EXIT-ESCALATE** |

**Parameter:** `score_threshold 0.4`, `max_iter 5`, `epsilon 0.01`, `voice_budget 0.25`, `confirm_confidence 0.9`.

**Guardrails:**
- **Voice-Budget:** Token-Diff-Rate (Multiset-Ähnlichkeit) ≤25 % pro Iteration, sonst wird der Kandidat verworfen (`rejected_budget` im Audit).
- **Signal-Bestätigung:** Ein Fund geht nur in den Fix ein, wenn er in 2 aufeinanderfolgenden DETECT-Läufen stabil ist **oder** die Konfidenz ≥0.9 beträgt.
- **Best-of-N-Rollback** zwischen aktuellem Bestwert und Kandidat.
- **Garantie-Aussagen sind maßstabsgebunden:** „slop-frei nach Maßstab des Detektors", Fixpoint ≠ Optimum. Ein Durchlauf bei maxIter zählt **nie** als stiller Erfolg.

---

## 8. Evaluations-Architektur

### 8.1 Drei-Level-Pyramide (`docs/EVALS.md`, Blaupause Hamel Husain)

| Ebene | Was | Wann | Kosten |
|---|---|---|---|
| **L1 — Unit-Assertions** | deterministische Tests je Signal: exakte Fixtures (≥1 TP + Hard Negatives), Akzeptanzschwellen, Guards | jeder Commit | sehr billig |
| **L2 — Judge + Human** | Golden Control Set als hartes FN/FP-Gate; LLM/Review nur als Veto, nie alleiniges Abbruchkriterium | jeder Signal-PR / Score-Change | mittel |
| **L3 — Quartals-Re-Score** | Re-Score des Gesamtkorpus, Drift-Messung, Rekalibrierung aus Korpus-Statistik | quartalsweise | teuer, selten |

`scripts/check_methodology.py` erzwingt, dass **jede** Datei unter `eval/` und `tests/` in dieser Zuordnung namentlich auftaucht — das Dokument kann nicht stillschweigend veralten.

### 8.2 Datenartefakte

| Datei | Umfang | Rolle |
|---|---|---|
| `eval/corpus.jsonl` (212 KB) | **330 Zeilen** — 221 slop / 109 clean | L3-Benchmark-Korpus |
| `eval/control_set.jsonl` | 10 Texte (5 slop / 5 hard negatives) | L2-Gate mit known-FN-Register |
| `eval/fp_baseline.json` | 109 Fixtures | FP-Drift-Snapshot |
| `eval/hardneg_borderline.json` | Top-5 Grenzband 0.315–0.342 + 3 handgeschriebene Fixtures 0.098–0.189 | Grenzband-Register |
| `eval/de_evidence_texts.jsonl` | 16 eigene Belegtexte (je Kategorie einer) | Zweitbelege für DE-Phrasen |
| `eval/discourse_ref.jsonl` | 8 Artefakte inkl. 2 Kontrollen | L4-Referenzkorpus für explorative Diskurs-Signale |

**Korpus-Zusammensetzung (gemessen):**
- **Sprachen:** en 313, de 7, fr 2, es 2, hi 2, vi 2, ur 2 → **95 % Englisch**
- **Genres:** generic 118, marketing 72, wiki 33, conversational 16, academic 14, technical 14, news 13, legal 12, recipe 7, code 6, nonfiction 6, config 6, lyric 6, seo 4, wellness 2, linkedin 1
- **Quellenverteilung:** 107 handcrafted, 16 `own:handwritten` (Issue #80), **207 aus Deep-Research-Artefakten** (deep/01 stop-slop 32, deep/02 no-ai-slop 36, deep/03 humanizer+Wikipedia 70, deep/04 unslop 32, deep/06 poteto 37). Belegtquote deutlich über der ADR-0005-Regel von ≥60 %.

### 8.3 Gemessene Benchmark-Ergebnisse (eigene Ausführung, 2026-08-27)

```
=== skill-pipeline (scorer+classifier), threshold 0.40, n=330 ===
  Precision 1.000 · Recall 0.995 · F1 0.998 · Accuracy 0.997
  TP=220  FP=0  TN=109  FN=1  (einziger FN: hard-slop-subtle-01, Score 0.254)
  FP-Rate je Clean-Genre: 0.0 in allen 12 Genres
  Per Sprache: de 1.0 · en 0.997 · es 1.0 · fr 1.0 · hi 1.0 · ur 1.0 · vi 1.0

=== skill-scorer allein ===  P 1.000 · R 0.982 · F1 0.991 · TP=217 FN=4
=== src-classifier ===       P 1.000 · R 0.502 · F1 0.669 · TP=111 FN=110
```

**Wichtiger Vorbehalt, den das Repo selbst dokumentiert** (SKILL.md, „Ehrlichkeitsgrenze"): Der hohe Recall ist **In-Sample-Recall** — die Phrasen aus Batch F wurden aus genau diesen FN-Texten gewonnen. Konstruierte menschliche Arbeitsprosa kann 0.400–0.556 erreichen. FP=0 gilt **korpusintern**. Diese Selbstrelativierung ist bemerkenswert und in `adr/0005` als Lehrfall verankert: Die frühere Schönwetter-Baseline F1 0.982 (53 Texte ohne Hard Negatives) wurde bewusst durch die ehrliche Zahl F1 0.476 ersetzt, bevor sie wieder auf 0.998 stieg.

### 8.4 Alle Gates — Ergebnis der eigenen Ausführung

| Gate | Kommando | Ergebnis |
|---|---|---|
| Control Set | `python3 eval/run_control_set.py` | **GATE PASSED** — 1 dokumentierter known-FN (`slop-fn-02`, 0.343) |
| Konsistenz | `python3 scripts/check_consistency.py` | **PASS** (11 Slop-Typen, 12 mustertragende Typen, 15 rhetorische Muster, 6 Sprachen) |
| SSOT | `python3 scripts/check_ssot.py` | **PASS** (C1–C4; 70 Konstanten, 10 Abweichungsgruppen, 63/96 DE-Phrasen mit ≥2 Belegen) |
| Methodik | `python3 scripts/check_methodology.py` | **PASS** |
| Signal-DoD | `python3 scripts/check_signal_dod.py` | **0 FAIL, 9 WARN** (Report-Modus, nicht blockierend) |
| FP-Baseline | `python3 scripts/fp_baseline.py --check` | **PASS**, keine Drift |
| Testsuite | `python3 -m unittest discover tests` | **420 Tests OK** — **nur mit installiertem `pytest`** (siehe 12.1) |

---

## 9. Governance-Schicht

Die auffälligste Eigenschaft des Repos: Es besitzt eine formalisierte Prozess-Verfassung, die umfangmäßig mit dem Code konkurriert.

### 9.1 Methodik-Kodex (`docs/METHODOLOGY.md`) — 11 Querprinzipien

| ID | Prinzip | Durchsetzung |
|---|---|---|
| M1 | Test-Oracle-Pflicht (Oracle **vor** Implementierung) | TDD-Red-Commit + DoD #1 + PR-Template |
| M2 | Guard-/keep_when-Systematik gegen FPs | DoD #2 + `check_signal_dod.py` + Genre-Profile |
| M3 | SSOT / Single Source of Truth | `check_consistency.py` + ADR-0002 + DoD #3 |
| M4 | Feedback-/Learning-Loops | Learning-Store + Re-Baseline-Kalender + `status`-Feld |
| M5 | Empirie/Benchmark vor Ausbau (Sequencing) | `depends-on`-Deklaration + FP-Gate + ADR-0005 |
| M6 | Provenance & Belegpflicht (claim → source → quote) | Claim-Register + Ironie-Test gegen eigenen CHANGELOG |
| M7 | Prozess-Zustandsmaschine mit Eskalation | Loop-Exit-Checks + Signal-Lebenszyklus |
| M8 | Determinismus vor LLM | L1 deterministisch, LLM nur als L2-Veto + ADR-0006 |
| M9 | Goodhart-Resistenz / Mehrfach-Maße | SCORE-GOVERNANCE.md |
| M10 | Minimum-Intervention / Voice-Erhaltung | Voice-Budget β=25 % als Non-Regression-Gate |
| M11 | Forschungs-Pipeline mit verifizierten Primärquellen | Pflichtfelder „Corpus Evidence" + „Prior Art" |

Alle referenzierten Issue-Nummern (#1–#68) müssen in einer Konsistenzliste stehen, die `check_methodology.py` prüft.

### 9.2 Signal-Lebenszyklus

```
nursery ──(FP-Gate bestanden)──▶ beta ──(≥2 Rekalibrierungen überlebt)──▶ stable
stable ──(ersetzt/Modellgeneration weg)──▶ deprecated ──▶ retired
beta/stable ──(schwerer FP-Rückfall)──▶ deprecated   [Rückfallpfad]
```

| Zustand | Score-Wirkung |
|---|---|
| `nursery` | detect-only |
| `beta` | vorläufiges Gewicht |
| `stable` | volles Gewicht |
| `deprecated` | Gewicht bleibt, wird bei Re-Baseline abgebaut; **keine Fixes mehr** |
| `retired` | kein Score-Einfluss |

Pflichtfelder je Signal: `status`, `status_since` (ISO-Datum), optional `replaces`. Blaupausen: Clippy-Lint-Gruppen (`nursery`), ESLint-Deprecation-Policy, SpamAssassin-MassCheck-Rescore.

### 9.3 Score-Governance (`docs/SCORE-GOVERNANCE.md`) — Optimierungs-Freigaben

| Größe | Optimierung erlaubt? |
|---|---|
| `slop_score` als Zielfunktion | **Nein** — Messgröße, nie Ziel |
| Precision auf Hard Negatives | **Ja, nach oben** — FP-Rate 0.0 je Genre ist geschützt, Verschlechterung blockt den Merge |
| Recall auf #41-Korpus | **Ja, nach oben**, ohne Precision-Verlust — Lücken werden Tickets, nicht durch Threshold-Senkung „gekauft" |
| Signal-Gewichte | **Nur aus Korpus-Statistik** (`eval/calibrate.py`), nie „gefühlt" |
| Threshold 0.40 | **Gesperrt** außerhalb einer Re-Baseline |
| Voice-/Stil-Metriken | **Nein** — nur Non-Regression (β=25 %) |
| Benchmark-Korpus selbst | **Nein im laufenden Loop** — eigene Changesets mit Belegtquote ≥60 % |

**Change-Protokoll-Pflicht** bei jeder Score-/Gewichts-/Threshold-Änderung: Messung vorher/nachher an Control Set **und** Benchmark, Guardrail-Beweis, CHANGELOG-Eintrag mit Messvorschrift, SSOT-Eintrag, Freigabe-Prüfung. Verstoß gegen die ersten drei Punkte = CHANGES_REQUESTED, unabhängig vom Messergebnis.

### 9.4 Signal-Definition-of-Done (`docs/SIGNAL-DOD.md`) — 8 Musts

1. Test-Oracle (Matcherspezifikation + ≥1 Positiv-/Negativ-Fixture + Schwelle) — *auto + Review*
2. FP-Abwägung dokumentiert (auch bei Ergebnis „kein Guard nötig") — *auto + Review*
3. SSOT-Eintrag in `ontology.json` inkl. `status` — *auto + Review*
4. Quellenbeleg (≥1 verifizierte Primärquelle, arXiv-Nummer wo applicable) — *Review*
5. Benchmark-Referenz (FP/FN auf Hard-Negative-Korpus) — *auto*
6. Kollisions-Check gegen Signal-Kollisions-Matrix (#46) — *Review*
7. Sequencing-Disziplin (`depends-on`) — *Review*
8. Prozess-Einbettung (Zustand, Exit-Kriterium, Eskalationspfad, Auditierbarkeit) — *Review*

Praktische Ausprägung im Code: **Jedes Signal erhält 3 Positiv-, 3 Negativ- und 2 Grenzfall-Fixtures („3/3/2")** — dieses Muster zieht sich durch alle neueren Testdateien.

### 9.5 Architecture Decision Records (8, MADR-Format)

| ADR | Entscheidung | Kernbegründung |
|---|---|---|
| 0000 | MADR-Template | Blaupause |
| 0001 | **Detector, kein Rewriter** | Goodhart-Risiko: Ein Rewriter im selben System optimiert den Detektor statt die Textqualität |
| 0002 | **`ontology.json` als SSOT** | Dual-Darstellung (JSON + Inline-Python) war aktiver Defekt |
| 0003 | **Golden Control Set als FN-Gate** | Vor Batch A gab es kein reproduzierbares FN-Gate; bekannte FNs werden dokumentiert, nicht versteckt |
| 0004 | **Genre-Opt-in statt Auto-Erkennung** | Auto-Genre wäre selbst ein unzuverlässiges ML-Subsystem mit unkontrollierbaren FP/FN-Verschiebungen |
| 0005 | **Benchmark-Disziplin & ehrliche Zahlen** | F1 0.982 auf 53 Texten ohne Hard Negatives war eine Schönwetter-Metrik |
| 0006 | **Detect-only-Module außerhalb des Scorers** | Score-Wirkung ohne Kalibrierung würde die Composite-Metrik verwässern |
| 0007 | **Git-only-Burn-Modus bei API-Ausfall** | GitHub-REST-API fiel mit 401 aus; Queue lief über reines git weiter |

`tests/test_adr.py` prüft die ADR-Pflichtfelder maschinell.

### 9.6 Templates

- `.github/PULL_REQUEST_TEMPLATE.md`: Pflichtfelder Corpus Evidence, Test-Oracle (mit Red-Commit-Hash), FP-Analyse, Prior Art, 8-Punkte-DoD-Checkliste, Governance-Abschnitt bei Score-Änderungen.
- `.github/ISSUE_TEMPLATE/signal-proposal.md`: Signal-RFC mit Pflichtfeldern; fehlende Pflichtfelder = Issue wird nicht in den Burn aufgenommen.
- `.github/ISSUE_TEMPLATE/bug.md`.

---

## 10. Das Lexikon (Pilot, #50)

Schema-first-Glossar mit strikter SSOT-Trennung:

```
lexikon/entries/*.yaml   (handgepflegt, 5 Einträge)
        │  scripts/build_lexikon.py
        ▼
lexikon/dist/            (Build-Artefakt, NIE direkt editieren)
   ├── index.md          Human-Sicht, alphabetisch, narrativ mit Belegen
   ├── lexikon.json      Agent-Sicht
   ├── llms.txt          llmstxt.org-Stil, Kurzform
   └── llms-full.txt     alle Einträge mit allen Belegzitaten
```

**Einträge:** LEX-2026-001 Throat-Clearing, -002 Provenance-Marker, -003 Binary-Contrast, -004 Marketing-CTA, -005 Human-Voice.

**Pflichtfelder je Eintrag** (`lexikon/schema/entry.schema.json`, draft-07-Subset): `id`, `term`, `definition`, `category` (signal/pattern/type/counter), `claims[]` mit je ≥1 `source` (`url`, `quote`, `accessed`), `status`, `version`. **Kein Eintrag ohne Quellenzitat** — jede faktische Aussage trägt ihren Beleg im Wikidata-Statement-Stil.

**Determinismus:** keine Timestamps, sortierte Iteration, kanonisches JSON, `content_hash` je Eintrag. Sync-Gate `tests/test_lexikon.py::test_dist_is_in_sync_with_entries` baut neu und lässt Abweichungen rot werden. Bemerkenswert: `.gitignore` enthält eigens `!lexikon/dist/`, um das Build-Artefakt trotz globalem `dist/`-Ignore zu versionieren.

---

## 11. Deutsche Sprachabdeckung (#76/#77)

Referenz-Katalog: `humanizer-de v5.22.2` mit **72 nummerierten Mustern** (M1–M72). Der im Deep-Dive genannte „82er-Katalog" wurde als Zählfehler identifiziert und korrigiert — ein Beispiel für die Claim-Register-Disziplin.

**Lizenz-Schutz (explizit dokumentiert):** Der Referenz-Katalog steht teilweise unter CC BY-SA 4.0. Das Mapping beschreibt jedes Muster **in eigenen Worten**; es wurden **keine Regexes oder Beispielsätze übernommen**. Wortgleiche Formulierungen werden der Wikipedia-Primärquelle attribuiert, Wortgleichheit mit dem Referenzkatalog allein zählt nicht als Beleg (`own:`-Belege stattdessen).

**Bilanz:**

| Status | Anzahl | Umsetzung |
|---|---|---|
| GEDECKT (bestand vorher) | 20 | sprachagnostische Struktur-/Unicode-Signale |
| GEDECKT (neu Teil 1) | 4 | M46–M49 in `de_typography.py` |
| GEDECKT (neu Teil 2) | 14 | 12 `de_*`-Phrase-Kategorien + M60/M61 in `structure_metrics.py` |
| GEDECKT (#76-Rest) | 2 | M66 Fake-Analyse-Anhang, M71 Scheinnuance |
| DE-VARIANTE (offen) | ~13 Rest | M7, M18, M26, M30, M32/33, M34, M35, M44, M54, M59, M65, M69, M70 |
| NEU (offen) | ~13 Rest | M6, M17, M29, M39, M40, M50–M52, M56, M58, M63, M68, M72 |
| Bewusster Stub | 1 | M63 Modalpartikel-Anomalie (wartet auf DE-Inventar) |

**DE-Signal-Zähler:** 22 (Master-Akzeptanzkriterium ≥20 erfüllt). **Alle DE-Signale sind detect-only** — kein Muster wird als „automatisch fixbar" behandelt (Anti-Auto-Rewrite-Disziplin).

**Evidence-Verdichtung:** 63/96 DE-Phrasen (65,6 %) mit ≥2 unabhängigen Belegen; die restlichen 33 (34,4 %) tragen einen Einzelbeleg als **dokumentierte Abweichung**. Der C4-Coverage-Pin ≥50 % lässt das SSOT-Gate bei Unterschreitung fehlschlagen.

---

## 12. Befunde: Inkonsistenzen und Risiken

Die folgenden Punkte sind eigene Messbefunde, keine Zitate aus der Repo-Doku.

### 12.1 CI-Testschritt bricht in der definierten Umgebung (hoch)

`.github/workflows/tests.yml` installiert ausschließlich `pyyaml` und ruft `python -m unittest discover tests -v` auf. Fünf Testmodule importieren jedoch `pytest` auf Modulebene:

- `tests/test_lexikon.py` (10 Tests)
- `tests/test_discourse_metrics.py` (21 Tests)
- `tests/test_de_evidence_densification.py` (6 Tests)
- `tests/test_register_profile.py` (25 Tests)
- `tests/test_deslop_loop.py` (13 Tests, nutzt zusätzlich `@pytest.fixture`)

Ohne installiertes `pytest` liefert die Suite reproduzierbar **5 Import-Errors** und einen Non-Zero-Exit; 75 Tests laufen gar nicht. Mit `pip install pytest` laufen 420 Tests grün. `pyproject.toml` deklariert weder `pytest` noch eine `dev`-Extra-Gruppe. **Fix:** `pytest` in den CI-Install-Schritt und in eine `[project.optional-dependencies] dev`-Gruppe aufnehmen — oder die fünf Module auf `unittest` portieren.

Ebenfalls: `tests/test_deslop_loop.py` mit `@pytest.fixture` ist unter `unittest`-Discovery **auch mit installiertem pytest** nicht vollwertig ausführbar; die 420 grünen Tests decken diese Fixture-basierten Fälle nicht ab.

### 12.2 README ist mehrere Versionen veraltet (mittel)

| Stelle | README-Claim | Gemessene Realität |
|---|---|---|
| `README.md:5` | „Version: 1.9.0" | **2.5.0** (Front-Matter, YAML, CHANGELOG, CLI) |
| `README.md:162` | Korpus „314 examples" | **330** |
| `README.md:167` | „Precision 1.000, Recall 0.312, F1 0.476" | **P 1.0 / R 0.995 / F1 0.998** |
| `README.md:205` | „24+ numbered references" | **39** in `REFERENCES.md` |
| README-Struktur | „examples/", „New in v1.2.0/v1.1.0" | Kein Hinweis auf `adr/`, `docs/`, `lexikon/`, `eval/`-Ausbau, Batches E–J |

Ausgerechnet ein Repo mit expliziter Claim-Register-Disziplin (M6) und einem „CHANGELOG-Ironie-Check" trägt in seiner Visitenkarte eine Recall-Zahl, die um Faktor 3 danebenliegt. Keines der Gates prüft README-Claims — `check_consistency.py` prüft YAML/TTL/JSON/Skill, nicht das README.

### 12.3 Weitere Doku-Drift (niedrig–mittel)

- `skills/.../SKILL.md:234`: Benchmark-Spiegel nennt „n=314 = 221 slop + 93 clean" — aktuell 330 = 221 + 109.
- `skills/.../SKILL.md:248`: „Full ontology (459 signals)" — `slop info` meldet **378**.
- `SKILL.md` Front-Matter beschreibt „Ontologie v1.2.0", „7 phrase categories", „14 slop types"; tatsächlich v2.5.0, 28 Phrase-Kategorien, 11+ Typen in 8 Gruppen.
- `docs/SCORE-GOVERNANCE.md` führt „aktuell F1 0.476, R 0.312" als laufende Recall-Lücke — historisch korrekt als Lehrfall, als Statusangabe veraltet.
- `pyproject.toml` verweist auf `https://github.com/hikaman/ai-slop-ontology`, der aktive Remote ist `MakerCologne/ai-slop-ontology`.
- `pyproject.toml` deklariert Version `0.1.0` für `slopkit`, entkoppelt von der Ontologie-Version 2.5.0 (vermutlich Absicht, aber nirgends dokumentiert).

### 12.4 CHANGELOG-Duplikat (niedrig)

Der Eintrag `## [2.2.0] — 2026-08-25 (Batch G — SSOT #49, Human-Voice #21, FU-Register)` erscheint **zweimal**.

### 12.5 Methodische Risiken (vom Repo teils selbst benannt)

1. **In-Sample-Recall.** R 0.995 ist gegen einen Korpus gemessen, aus dem die Signalphrasen gewonnen wurden. Das Repo benennt dies in SKILL.md ausdrücklich als „Ehrlichkeitsgrenze" — die Zahl ist damit **kein Generalisierungsbeleg**. Es existiert kein unabhängiger Holdout-Split.
2. **Sprach-Monokultur des Korpus.** 313 von 330 Texten sind Englisch; DE hat 7, alle übrigen Sprachen je 2. Der DE-Layer (96 Phrasen, 22 Signale) ist damit gegenüber einem 7-Text-Korpus validiert. Die Per-Sprache-Werte (de 1.0, fr 1.0 …) beruhen auf statistisch bedeutungslosen Stichproben.
3. **FP=0 ist korpusintern.** 109 Hard Negatives über 12 Genres sind gut kuratiert, aber die Genres sind ungleich besetzt (generic 6, technical 13, conversational 16). Das Repo dokumentiert die Grenze als FU-11/FU-13.
4. **Zwei-Engine-Divergenz.** Der `src`-Klassifikator (R 0.502) ist das Backend der öffentlich beworbenen `slop`-CLI. Nutzer der CLI bekommen die halbe Erkennungsleistung der Skill-Pipeline. Weder README noch USER-GUIDE machen diesen Unterschied explizit.
5. **Detect-only-Akkumulation.** 17 der 26 Module sind detect-only ohne Score-Pfad. Das ist governance-konform, führt aber dazu, dass ein Großteil der Detektionsarbeit für automatisierte Gates unsichtbar bleibt — der numerische Score speist sich weiterhin überwiegend aus den kalibrierten Phrase-/Buzzword-Listen.
6. **Signal-DoD: 9 WARN.** `check_signal_dod.py` meldet neun Module ohne SKILL.md-Referenz bzw. ohne `keep_when`-Dokumentation (u. a. `reinventing_wheel`, `rhythm_openers`). Der Report ist bewusst nicht blockierend (Exit 0), die Lücke damit dauerhaft tolerierbar.
7. **Regex-Satzsegmentierung.** `[.!?]+` zerlegt Abkürzungen („z. B.") falsch — in REVIEW-2026-07 als akzeptierte Heuristik-Grenze dokumentiert, wirkt sich aber auf Burstiness und alle Per-Satz-Raten aus.
8. **Ein-Tages-Entwicklungsgeschichte.** Alle 50 Commits stammen vom 25.08.2026 zwischen 00:59 und 15:25, 13 davon von einem `issue-burner`-Bot. Die Batches A–J wurden in einem intensiven automatisierten Durchlauf erzeugt. Die Governance-Dokumente sind laut eigenen ADR-Angaben teilweise **rückdokumentiert** („Datum: 2026-08-25 (rückdokumentiert)"). Es gibt keine über Zeit gewachsene Nutzungshistorie, keine externen Contributors, keine Issues/PRs im aktuellen Zugriff.

### 12.6 Was sauber ist

- Alle sechs ausführbaren Gates laufen grün.
- Der Benchmark reproduziert die im CHANGELOG behaupteten Zahlen exakt (P 1.0 / R 0.995 / F1 0.998, n=330).
- Kein Signal-Modul hat einen FAIL im DoD-Check.
- Die SSOT-Abweichungen sind vollständig registriert, nicht versteckt.
- Der bekannte FN (`slop-fn-02`) ist im Control Set namentlich, mit Begründung und Ticket-Verweis dokumentiert statt weggeschwiegen.
- Lizenzhygiene bei der Adaption fremder Kataloge (CC BY-SA-Schutz, MIT-Attribution für no-ai-slop) ist explizit ausgearbeitet.
- Alle vier Kernzitate wurden laut REVIEW-2026-07 gegen das Web verifiziert — inklusive des Falls „Keisha et al.", der wie ein Halluzinationskandidat aussah und sich als echt erwies.

---

## 13. Nutzung

### 13.1 Installation

```bash
pip install -e .          # stellt das Kommando `slop` bereit
pip install pyyaml        # optional, nur für YAML-Checks
pip install pytest        # nötig für die vollständige Testsuite (siehe 12.1)
```

### 13.2 CLI (`slop` / `python -m slopkit`)

| Kommando | Ausgabe |
|---|---|
| `slop score TEXT` | numerischer Score (0–1) + Severity |
| `slop classify --file draft.md` | Slop-Typen, gewichtete Signale, Dimensionen, Gegenmaßnahmen |
| `slop rhetoric TEXT` | Detect-only rhetorische Muster als benannte Evidenz |
| `slop check -` | `classify` + `rhetoric` in einem Durchlauf (stdin) |
| `slop code --lang python app.py` | Code-Slop (halluzinierte Pakete, Secrets, Kommentar-Bloat) |
| `slop info` | Signaldatenbank- und Ontologie-Metadaten |
| `slop benchmark` | Benchmark gegen den gelabelten Korpus |
| `slop selfcheck` | JSON/TTL/YAML/Skill-Konsistenzprüfung |

Jedes Textkommando akzeptiert positionalen String, `--file PATH` oder stdin (`-`), plus `--json`.

**Exit-Codes:** 0 Erfolg · 1 bei `--fail-over N` und Score ≥ N · 2 Ontologie nicht ladbar · Benchmark/Selfcheck propagieren ihren eigenen Code. **Ohne `--fail-over` beenden `score`/`check` immer mit 0** — sie berichten, sie gaten nicht.

**Verifizierter Beispiellauf:**
```
$ slop score --file t.txt
🔴 slop score 0.95  [███████████████████·]  slop_candidate
  top signals: CriticalBuzzword, BuzzwordOveruse, PhrasePattern

$ slop rhetoric --file t.txt
✍️  rhetorical patterns (1):
  • Binary contrast (70%) — "It's not a tool. It's"
      fix: The eval matters more than the model.
```

### 13.3 Skill-Skripte direkt

```bash
python3 skills/ai-slop-detection/scripts/slop_scorer.py --file text.txt
python3 skills/ai-slop-detection/scripts/slop_scorer.py --diff main..feature     # nur geänderte Zeilen
python3 skills/ai-slop-detection/scripts/slop_scorer.py --anchor-diff main..HEAD # Anker-Drift
python3 skills/ai-slop-detection/scripts/slop_classifier.py --file text.txt
python3 skills/ai-slop-detection/scripts/rhetorical_patterns.py --file text.txt
python3 scripts/code_slop_check.py --file src/helper.ts
python3 scripts/deslop_loop_cli.py input.txt --fix-module my_fixer.py
```

`--diff` bewertet Textdateien (`.md`/`.txt`) mit dem Textscorer und routet Codedateien an `code_slop.py`; Binärdateien und Lockfiles werden übersprungen; geänderte Zeilen erhalten ein ±3-Zeilen-Kontextfenster. Exit 1, sobald neuer Slop die Schwelle überschreitet.

### 13.4 Als Bibliothek

```python
from src.classifier import SlopClassifier
clf = SlopClassifier("ontology.json")
res = clf.classify_text(text)
res.overall_slop_score   # 0..1
res.signals_detected     # [SignalMatch(signal_id, severity, confidence, evidence), ...]
```

### 13.5 Agent-Integrationsregeln (aus SKILL.md)

- **Retrieval:** ≥0.70 → nicht als Primärquelle, unabhängige Verifikation nötig; 0.40–0.69 → nur schwaches Signal; <0.40 → normale Prüfung.
- **Memory:** Verdächtiger Slop **nie** als faktisches Wissen speichern. Erlaubte Speichertypen: `observed_claim`, `unverified_claim`, `slop_candidate`, `distribution_pattern`, `source_risk_signal`.
- **Citation:** Nicht zitieren — KI-Zusammenfassungen ohne Primärquelle, SEO-Listicles ohne Eigenrecherche, Artikel mit halluzinierten Referenzen, synthetische Social-Posts als Beleg.
- **Critical Review:** Immer eskalieren bei Recht, Medizin, Politik, Finanzen, Kindersicherheit, Identitäts-Impersonation — **unabhängig vom Score**. LegalSlop und AcademicSlop sind besonders gefährlich: professionelle Optik bei fabrizierten Zitaten.
- **Retrieval-Collapse-Abwehr:** ≥3 Quelldomänen, Score-Gate <0.4, Provenance-Filter, Recency ≠ Autorität, Kontaminationsprüfung, Cross-Validation gegen ≥2 unabhängige Bestätigungen.

---

## 14. Versionshistorie (verdichtet)

| Version | Datum | Kern |
|---|---|---|
| 1.0.0 | 2026-05-20 | Erstveröffentlichung der Ontologie |
| 1.1.0 | 2026-07-10 | SecurityReportSlop, PeerReviewSlop, HyperTypicality; Engine-Fixes (Wortgrenzen, Overlap-Dedup, Multilingual-Case, Burstiness-Neutralität); erste Tests, LICENSE, CHANGELOG |
| 1.2.0 | 2026-07-10 | Eval-Korpus + Benchmark-Runner, kalibrierte Gewichte, **Noisy-OR-Aggregation**, Hindi/Vietnamesisch/Urdu, `authority_claims`, Konsistenz-Checker in CI |
| 1.3.0–1.6.0 | 2026-08-24/25 | laufender Signalausbau |
| 1.7.0 (Batch B) | 2026-08-24 | Genre-Profile #42 |
| 1.8.0 (Batch C) | 2026-08-24 | Portability #14 u. a. |
| 1.9.0 (Batch D) | 2026-08-25 | Korpus #41 (314 Texte), Diff-Modus #10, Code-Slop #9, Tokenizer #43 |
| **2.0.0 (Batch E)** | 2026-08-25 | **Meta-Meilenstein:** METHODOLOGY #63, SIGNAL-DOD #64, ADRs #65, Templates #66, SCORE-GOVERNANCE #67, EVALS #68 |
| 2.1.0 (Batch F) | 2026-08-25 | FN-getriebener Signalausbau (Serien 0101–0606) |
| 2.2.0 (Batch G) | 2026-08-25 | SSOT #49, Human-Voice #21, FU-Register *(Eintrag doppelt im CHANGELOG)* |
| 2.3.0 (Batch H) | 2026-08-25 | DESLOP-LOOP #51, Lexikon-Pilot #50 |
| 2.4.0 (Batch I) | 2026-08-25 | Anchor-Drift #78, Null-Edit-Contract #79, FP-Baseline #80, Naturalness-Guard #81, DE-Katalog Teil 1 #76, DE-Vokabular #77 |
| **2.5.0 (Batch J)** | 2026-08-25 | DE-Katalog Teil 2 (12 Kategorien), FU-17 SSOT-C4, Genre-Menschtexte, Register-Profile #74, Diskurs-Metriken #72; Tests 440→469→539, Korpus 314→330 |

Arbeitsmuster durchgängig: **RED-Commit (`test(#N): RED — …`) vor GREEN-Commit (`feat(#N): GREEN — …`)**, gefolgt von `fix(review-X)`-Nachbesserungen und `chore(batch-X)`-Versionskonsolidierung am Batch-Ende. Jeder GREEN-Commit nennt Testzahl, Benchmark-Werte und Gate-Status.

---

## 15. Gesamteinschätzung

**Stärken**

1. **Governance-Dichte ohne Beispiel.** 8 ADRs, ein 11-Prinzipien-Kodex, eine 8-Punkte-Signal-DoD und ein Score-Governance-Regelwerk mit expliziten Optimierungs-Freigaben — für ein Repo von 15k Python-LOC ist das außergewöhnlich. Entscheidend: Die Dokumente sind **maschinell erzwungen** (`check_methodology.py` prüft, dass jede Eval-Datei im EVALS-Dokument steht; `test_adr.py` prüft ADR-Pflichtfelder).
2. **Selbstanwendung der eigenen Doktrin.** Ein Anti-Slop-Repo, das Belegpflicht, ehrliche Zahlen und Anti-Goodhart auf sich selbst anwendet — inklusive der bewussten Ersetzung einer guten Metrik (F1 0.982) durch eine schlechte, aber ehrliche (F1 0.476), als der Korpus härter wurde.
3. **FP-Infrastruktur in fünf unabhängigen Schichten.** Quote-Exemption, Kumulativregel, Genre-Opt-in, Learning-Store, FP-Baseline-Register — plus Null-Edit-Contract und Grenzband-Register. FP-Rate 0.0 in allen 12 Clean-Genres.
4. **Detect-only als Default.** Neue Signale können nicht unbemerkt den Score verändern. Das ist die wirksamste Einzelmaßnahme gegen schleichende Metrikverwässerung.
5. **Null Laufzeit-Abhängigkeiten.** Der gesamte Detektor läuft auf der Standardbibliothek — deployment- und supply-chain-freundlich, was für ein Tool, das Supply-Chain-Attacken als Harm-Typ führt, konsequent ist.
6. **Ehrliche Selbstkritik im Artefakt.** „Ehrlichkeitsgrenze", „known-FN", „dokumentierte Abweichung", „bewusster Stub" sind stehende Kategorien, nicht Ausnahmen.

**Schwächen**

1. **Der CI-Testschritt ist in der deklarierten Umgebung rot** (fehlendes `pytest`) — der wichtigste operative Defekt.
2. **Das README, die Visitenkarte des Projekts, ist drei Minor-Versionen und eine Größenordnung im Recall veraltet.** Kein Gate schützt es.
3. **Die Generalisierung ist unbelegt.** In-Sample-Recall, kein Holdout, 95 % englischer Korpus bei 22 deutschen Signalen.
4. **Die beworbene CLI nutzt die schwächere Engine** (R 0.502 statt 0.995), ohne dass das dokumentiert wäre.
5. **Ein-Tages-Genese, überwiegend automatisiert,** mit rückdokumentierten ADRs. Die Prozessdisziplin ist real im Code sichtbar, ihre gelebte Bewährung über Zeit steht noch aus.

**Reifegrad:** Technisch solide und ungewöhnlich gut abgesichert; als Wissensbasis breit und belegt; als produktiver Detektor auf englischem Text im gemessenen Rahmen sehr gut, außerhalb davon unvalidiert. Die Governance-Schicht ist der eigentliche Wert des Repos — sie ist auf andere Detektor-Projekte übertragbar.

**Empfohlene nächste Schritte (nach Priorität):**

1. `pytest` in CI-Install und `pyproject.toml`-Dev-Extra aufnehmen (behebt 12.1).
2. README auf 2.5.0 aktualisieren: Version, Korpusgröße, Benchmark-Zahlen, Referenzzahl, Struktur um `adr/`/`docs/`/`lexikon/` ergänzen.
3. Ein Konsistenz-Gate für README-/SKILL.md-Claims ergänzen (die Infrastruktur dafür existiert bereits in `check_consistency.py`) — das würde 12.2 und 12.3 dauerhaft schließen.
4. Holdout-Split oder externen Testkorpus einführen, um den In-Sample-Recall-Vorbehalt aufzulösen.
5. Engine-Divergenz adressieren: entweder `slopkit` auf die Skill-Pipeline umstellen oder den Unterschied in README/USER-GUIDE explizit machen.
6. CHANGELOG-Duplikat (2.2.0) bereinigen.

---

*Erstellt durch vollständige Inventur und Ausführung aller Test-, Benchmark- und Gate-Skripte des Repositories am 2026-08-27.*
