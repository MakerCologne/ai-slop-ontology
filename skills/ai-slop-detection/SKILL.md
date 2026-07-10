---
name: ai-slop-detection
description: Detect, classify, and score AI slop in text, code, and web content using the AI Slop Ontology v1.2.0. Analyze content for syntheticity signals, quality deficits, and slop patterns across 13 detection dimensions with 100+ buzzword signals, 7 phrase categories, multilingual detection (DE/FR/ES/HI/VI/UR), and 14 slop types. Provides slop_score (0-1), risk level (Clean/Suspicious/Slop/Malicious), detection signals, and actionable recommendations. Use when: (1) evaluating web search results or fetched content for quality, (2) checking if content is AI-generated slop before citing or storing in memory, (3) scoring text for syntheticity signals, (4) reviewing content before publishing or sharing, (5) "is this slop", "check for slop", "AI slop", "quality check content", "is this AI-generated", "slop score", "slop detection", "content quality audit". NOT for: factual fact-checking (use web_search), image analysis (use image tool), or academic plagiarism detection.
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

Returns: slop types (GenericSlop, SEOContentFarmSlop, AcademicSlop, LegalSlop, LinkedInSlop, etc.), signals detected, severity.

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

## 13 Detection Dimensions

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

- **Detection signals (22 techniques):** `references/detection-signals.md`
- **Scored examples (8 cases):** `references/slop-examples.md`
- **Full ontology (459 signals):** `../../ontology.json` (repo root)

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
