---
name: ai-slop-detection
description: Detect, classify, and score AI slop in text, code, and web content using the AI Slop Ontology v1.2.0. Analyze content for syntheticity signals, quality deficits, and slop patterns across 14 detection dimensions with 100+ buzzword signals, 7 phrase categories, multilingual detection (DE/FR/ES/HI/VI/UR), and 14 slop types. Provides slop_score (0-1), risk level (Clean/Suspicious/Slop/Malicious), detection signals, and actionable recommendations. Use when: (1) evaluating web search results or fetched content for quality, (2) checking if content is AI-generated slop before citing or storing in memory, (3) scoring text for syntheticity signals, (4) reviewing content before publishing or sharing, (5) "is this slop", "check for slop", "AI slop", "quality check content", "is this AI-generated", "slop score", "slop detection", "content quality audit". NOT for: factual fact-checking (use web_search), image analysis (use image tool), or academic plagiarism detection.
---

# AI Slop Detection v2

Classify and score content for AI slop using the AI Slop Ontology v1.0.0.

## Core Concept

AI Slop is not a binary type — it is a **risk profile**. Three necessary conditions (all must be met for confirmed slop):
1. AI is the primary source
2. No human care/curation/verification
3. Unsolicited distribution (push, not pull)

## Quick Assessment (mental checklist)

Before running scripts, apply this heuristic:

- **Buzzwords?** 100+ terms across 4 tiers: delve, tapestry, realm, leverage, synergy, unlock, harness, paramount, seamless, holistic, transformative, groundbreaking, cutting-edge, state-of-the-art, game-changer, embark on a journey, whether you're a seasoned...
- **AI Phrases?** 6 categories: hedging qualifiers, generic transitions, opening formulas, closing formulas, metaphor abuse, listicle tells
- **Trailing moral?** "remember that...", "ultimately...", "what matters most..."
- **Mirrored intro/conclusion?** Conclusion restates introduction with synonyms
- **All substance, no information?** High word count, zero verifiable claims
- **Uniform sentence length?** Every sentence 20-30 words — no burstiness
- **Multilingual AI patterns?** German: "im heutigen schnelllebigen", "es gilt zu beachten"; French: "dans le paysage actuel"; Spanish: "en el paisaje actual"; Hindi: "आज की तेज़ रफ़्तार दुनिया में"; Vietnamese: "trong thế giới ngày nay"; Urdu: "آج کی تیز رفتار دنیا میں"

If 3+ apply → likely slop. Proceed to scoring.

## Detection Pipeline

### Step 1: Run the scorer

```bash
python3 scripts/slop_scorer.py "TEXT_TO_ANALYZE"
```

Returns: `slop_score` (0–1), individual dimension scores, signal breakdown with tier information.

### Step 2: Classify slop type

```bash
python3 scripts/slop_classifier.py "TEXT_TO_ANALYZE"
```

Returns: slop types (GenericSlop, SEOContentFarmSlop, AcademicSlop, LegalSlop, LinkedInSlop, etc.), signals detected, severity, and `rhetorical_patterns` (see below).

### Step 2b: Name rhetorical patterns (detect-only)

```bash
python3 scripts/rhetorical_patterns.py "TEXT_TO_ANALYZE"
```

### Step 2c: Check anchor drift between two versions (detect-only)

```bash
python3 scripts/slop_scorer.py --anchor-diff base..head
```

Compares the protected anchors (numbers incl. locale variants, direct quotes,
URLs, DOIs) of every changed text file across a git range. Reports
`anchor_lost` / `anchor_added` / `authority_shift` (a retained number whose
nearby authority carrier changed, e.g. "according to the study" →
"researchers report"). Advisory-only, never score-dominant; the module
`scripts/anchor_diff.py` exposes `anchor_diff(text_a, text_b)` directly.
Locale boundary: "3.5" → "3,5" is NOT drift.

### Step 2d: Naturalness-Guard (detect-only, #81)

`scripts/naturalness_guard.py` — `register_drift` (mixed register: ≥2 formal
vs ≥2 colloquial markers outside quotes) and `over_sanitized` (≥3 distinct
expanded full forms, zero contractions; suppressed for genre=
"academic"/"legal"). Both advisory, confidence ≤0.45, never part of the
numeric score. `modal_particle_anomaly` is an explicit stub until the DE
layer lands (#76).

### Step 2e: DE-Typografie (detect-only, #76 Teil 1)

`scripts/de_typography.py` — deutsche Oberflächen-Marker: falsche
deutsche Anführungszeichen („Text”), kapitalisierte Funktionswörter in
Überschriften, englisches Dezimal-/Datumsformat (Versionen exempt),
Genitiv-Apostroph (Marken-Allowlist). DE-Sprachgate; Coverage-Mapping
aller 72 Katalog-Muster: `docs/de-coverage.md`.

### Step 2f: Struktur-Metriken (detect-only, #76 Teil 2)

`scripts/structure_metrics.py` — sprachagnostische Struktur-Signale:
`synonym_rotation` (M60: ≥3 verschiedene Bezeichnungen aus einer
Synonym-Familie für dieselbe Entität) und `isometry` (M61: ≥5
Struktureinheiten mit Wortlängen-Streuung < 1.0). Beide advisory,
Konfidenz 0.5, nie score-dominant; Schwellen fixture-kalibriert
(`tests/test_structure_metrics.py`).

### Step 2g: Register-Profile v2 (detect-only, #74)

`scripts/register_profile.py` — zwei Oberflächen: (1) `register_profile(text)`
liefert eine JSON-Stilkarte (mode, deictic_center, address, distance,
sentence_shape, word_level, paragraph_openers, particles,
punctuation_affinity) — der Scorer gibt sie unter `context` im Report aus,
ohne jeden Score-Einfluss. (2) `register_drift_intern(text, genre=)` —
Register-Distanz ZWISCHEN Dokument-Hälften (je Hälfte registerrein,
Hälften unterschiedlich), komplementär zu #81 `register_drift`
(Ganztext-Mischung; Kollisionsdisziplin: anderer Fallraum, anderes
Finding-Id). Genre-Profile (#42) werden respektiert: academic/legal/
technical suppressieren, exempt_terms zählen nicht als Marker. Advisory,
Konfidenz 0.5 (`tests/test_register_profile.py`).

### Step 2h: Diskurs-Metriken (explorativ, detect-only, #72)

`scripts/discourse_metrics.py` — `rank_without_criterion` (Rangliste mit
≥ 3 nummerierten Positionen ohne jedes Bewertungskriterium) und
`identical_enumeration` (≥ 3 Sätze mit identischem Anfangs-Frame als
rhetorische Staffage). Beide **explorativ** (`exploratory: True`,
Konfidenz ≤ 0.35, nie score-wirksam). Referenzkorpus:
`eval/discourse_ref.jsonl` (versioniert, mit Kontrollartefakten).

### DE-Phrase-Layer (#76/#77, SSOT in ontology.json)

Returns fifteen sentence-level AI writing shapes as **named patterns with quoted
evidence** (binary contrast, colon reveal, superficial analysis, negative
listing/fragmentation, fake-strong verb, synonym cycling, hollow kicker/recap,
formatting slop, robotic rhythm, plus the Wikipedia "Signs of AI writing" set:
throat-clearing openers, faux-insight setups, importance puffery, forced
triads, repeated sentence openings, chatbot leftovers). These are reported for a human to check and do
**not** change the numeric score — use them when the ask is "which AI writing
tics are in this draft?" rather than "how sloppy is it?". Each pattern has a
`keep_when` guard so genuine voice is not flagged. The formatting-slop
pattern also applies the em-dash doctrine (none in short copy under ~120
words, 1–2 allowed in long drafts, clusters always flagged) and flags
title-case headings (2+), curly double quotes in plain text, and stacked
hyphenated compound modifiers (2+ distinct, e.g. "cross-functional,
data-driven"). Data lives in `ontology.json`
under `signals.text.rhetoricalPatterns`; concept adapted from
[petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) (MIT) and
[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).

### Step 3: Interpret results

| Score Range | Risk Level | Action |
|-------------|-----------|--------|
| 0.00–0.24 | 🟢 Clean | Normal use, standard source checks |
| 0.25–0.39 | 🟡 AI-Assisted | Use with cross-checking |
| 0.40–0.69 | 🟠 Suspicious | Not as primary source, human review |
| 0.70–0.89 | 🔴 Slop | Do not cite, do not store as fact |
| 0.90–1.00 | ⚫ Malicious/Severe | Block, flag, do not use |

### Step 4: Apply agent rules

**Retrieval Rule:**
- `slop_score >= 0.70` → do NOT use as primary source, require independent verification
- `0.40 <= slop_score < 0.70` → use only as weak signal, cross-check with primary sources
- `slop_score < 0.40` → allow with normal quality checks

**Memory Rule:**
- NEVER store suspected slop as factual knowledge
- Allowed storage types: `observed_claim`, `unverified_claim`, `slop_candidate`, `distribution_pattern`, `source_risk_signal`

**Citation Rule:**
- Do NOT cite: AI-generated summaries without primary source, SEO listicles with no original reporting, articles with hallucinated references, synthetic social posts as evidence

**Critical Review Rule:**
- ALWAYS escalate (regardless of slop_score) for: legal, medical, political, financial, child safety, identity impersonation content
- **LegalSlop** and **AcademicSlop** are ESPECIALLY DANGEROUS — they look professional but contain fabricated citations

## 14 Detection Dimensions

1. **Information Density** — unique_words/total_words (< 0.40 = slop)
2. **Repetition Ratio** — most_common_token/total_tokens (> 0.20 = slop)
3. **Burstiness** — sentence length variance (std_dev < 3 = AI-like)
4. **Buzzword Score** — 100+ terms in 4 tiers (critical/high/moderate/weak)
5. **AI Phrase Patterns** — 6 categories of characteristic phrases
6. **Punctuation Anomalies** — em-dash, ellipsis, exclamation rates
7. **Trailing Moral** — generic lesson/moral at end
8. **List-Heavy Structure** — >40% list items without narrative
9. **Fake Authority Claims** — "studies have shown" without citations
10. **Verbosity** — avg sentence length > 25 words
11. **Multilingual AI Patterns** — DE/FR/ES characteristic patterns
12. **Mirrored Intro↔Conclusion** — conclusion restates intro
13. **Structural Signals** — composite of uniform structure patterns
14. **Portability** (v1.8.0) — rate of sentences with no proper names, numbers, quotes, or code (> 0.5 = low-weighted genericity signal, weight 0.02; German noun capitals conservatively block portability)

## 14 Slop Types

| Type | Telltale | Danger |
|------|----------|--------|
| GenericSlop | "In today's fast-paced..." | Low substance, high buzzword density |
| SEOContentFarmSlop | "Let's dive in...", "10 ways to..." | Search manipulation |
| AcademicSlop | "growing body of literature..." | ⚠️ Fabricated citations |
| PseudoInsightSlop | "The key is to find balance..." | Sounds profound, says nothing |
| FakeAuthoritySlop | "Studies have shown..." | No real citations |
| WellnessSlop | "Self-care isn't selfish..." | Universalized, helps no one |
| WikipediaRehash | "X is defined as..." | Zero originality |
| EngagementClickbaitSlop | "You won't believe..." | Virality over substance |
| PropagandaDisinfoSlop | "They don't want you to know..." | Deliberate manipulation |
| Workslop | "Circling back...", "Let's align..." | Shifts cost to receiver |
| LegalSlop | "Precedent clearly shows..." | ⚠️ Fake precedents |
| LinkedInSlop | "Thrilled to announce..." | Announces nothing |
| SecurityReportSlop | "could potentially allow..." | ⚠️ Wastes maintainer time; killed curl's bug bounty (Feb 2026) |
| PeerReviewSlop | "the manuscript is well written..." | ⚠️ Generic review without engaging the actual paper |

## Retrieval Collapse Defense

When evaluating content for RAG/Search/Memory:

1. **Source Diversity** — Min 3+ different source domains
2. **Slop Score Gate** — Only sources with score < 0.4
3. **Provenance Filter** — Prefer human-verified sources
4. **Recency vs Authority** — New ≠ Better. Prefer established sources
5. **Contamination Detection** — Check if search results are slop-dominated
6. **Cross-Validation** — Facts against min. 2 independent confirmations

## Knowledge Collapse Stages (Keisha et al., arXiv:2509.04796, NeurIPS 2025 Workshop)

- **Stage A:** Facts correct, instruction-following intact (low risk)
- **Stage B:** CONFIDENTLY WRONG — Facts false but format correct (CRITICAL — most harmful)
- **Stage C:** Complete breakdown, incoherent (high but detectable)

## Web Content Evaluation

For URLs and search results, check these additional signals:

- **Domain reputation** — Known content farm? (NewsGuard: 3,749 tracked, June 2026)
- **Author presence** — Named author with verifiable history?
- **Source citations** — Real, verifiable references or hollow claims?
- **Publication pattern** — Mass upload? Cross-platform repost?
- **Provenance** — C2PA metadata? Platform AI labels?

## Advanced References

### Benchmark (Spiegel des README, FU-10)

Gemessen 2026-08-28 mit `eval/run_benchmark.py --threshold 0.40`
gegen `eval/corpus.jsonl` (n=331 = 221 slop + 110 clean), Engine
`skill-scorer`:

- **P 1.0 / R 0.982 / F1 0.991** (TP 217, FN 4, FP 0)
- Ehrlichkeitsgrenze (Review F, #85): das ist durchgehend ein
  **In-sample**-Wert — `eval/calibrate.py` fittet die Dimensionsgewichte auf
  demselben Korpus, und die Batch-F-Phrasen wurden aus denselben FN-Texten
  gewonnen; konstruierte menschliche Arbeitsprosa kann 0.400–0.556 erreichen.
- **Held-out (5-fold, seed 17, 2 Coordinate-Ascent-Runden je Fold, gemessen
  2026-08-28):** Scorer **P 0.986 / R 0.982 / F1 0.984**, Pipeline
  **P 0.987 / R 0.995 / F1 0.991**. Der Abstand liegt in der **Precision**,
  nicht im Recall: gepoolt über alle fünf Folds fallen **3 der 110
  Clean-Texte** fälschlich über die Schwelle. Die viel zitierte `FP=0`
  überlebt die Kreuzvalidierung also nicht — sie ist eine Eigenschaft der
  Trainingsmenge. Reproduzieren:
  `eval/run_benchmark.py --cross-validate 5 --cv-rounds 2` (L3, rund 30 min).
- Gepinnt ist die **In-sample**-Zeile: Korpusgröße, Aufteilung, P/R/F1 und
  Konfusionsmatrix laufen gegen einen frischen Benchmark-Lauf
  (`tests/test_cross_validation.py`) — der Korpusstand hier war zuvor
  17 Clean-Texte alt, ohne dass ein Gate das bemerkt hätte. Die Held-out-Zeile
  ist ein **datierter Messwert**, kein Pin: sie kostet rund 30 Minuten und
  gehört damit in den Re-Baseline-Zyklus (s. docs/EVALS.md), nicht in CI. Wer
  den Korpus ändert, misst sie mit dem angegebenen Kommando neu.
- Control Set: `eval/run_control_set.py` — Gate grün inkl. dokumentierter
  known-FNs.

## Advanced References (continued)

- **Detection signals (22 techniques):** `references/detection-signals.md`
- **Scored examples (8 cases):** `references/slop-examples.md`
- **Full ontology (459 signals):** `../../ontology.json` (repo root)
- **Positive counter-profile (human voice):** `references/human-voice.md` (#21)

## Output Format

When reporting slop analysis to users:

```
🔍 Slop Analysis
Score: 0.XX | Level: [🟢/🟡/🟠/🔴/⚫]
Types: [SlopType1, SlopType2]
Signals: [Signal1 (tier), Signal2, ...]
Action: [recommendation]
```

For detailed reports, include dimension breakdown and specific evidence with tier information.
