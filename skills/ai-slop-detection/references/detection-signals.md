# Detection Signals Reference

Detailed detection techniques from the AI Slop Ontology. Use when deeper analysis is needed.

## Table of Contents
1. [Text Signals](#text-signals)
2. [Code Signals](#code-signals)
3. [Image Signals](#image-signals)
4. [Behavioral Signals](#behavioral-signals)
5. [Provenance Signals](#provenance-signals)
6. [Statistical/ML Methods](#statisticalml-methods)
7. [Thresholds](#thresholds)

## Text Signals

### Repetition Ratio
`most_common_token / total_tokens`
- > 0.20 → HIGH
- > 0.30 → CRITICAL

### Buzzword Detection (14 terms)
**Tier 1** (generic filler): delve, realm, tapestry, landscape, dynamic
**Tier 2** (action inflation): unleash, unlock, harness, leverage
**Tier 3** (corporate jargon): paradigm, synergy, robust
**Tier 4** (hype): cutting-edge, state-of-the-art, game-changing

≥3 hits across tiers → strong signal (confidence ≥ 0.80)

### Template Phrases
"it's important to note", "in conclusion", "to sum up", "furthermore", "moreover", "as previously mentioned", "it is worth noting", "needless to say", "in today's [X]", "let's dive in", "we will explore", "table of contents"

≥2 template phrases → signal (confidence ≥ 0.75)

### Punctuation Anomalies
- Em-dash rate > 0.5 per sentence
- Ellipsis rate > 0.3 per sentence
- Exclamation rate > 0.2 per sentence

### Information Density
`unique_words / total_words`
- < 0.40 → verbose slop
- 0.40–0.60 → borderline
- > 0.60 → healthy

### Uniform Sentence Length (Burstiness)
Standard deviation of sentence word counts:
- < 3 → highly uniform (AI-like)
- 3–5 → somewhat uniform
- > 5 → natural variation

### Trailing Moral Pattern
Text ends with: "remember that", "ultimately", "what matters most", "at the end of the day", "it's important to remember", "the key takeaway", "the bottom line is"

### Excessive Lists
>40% of lines are bullet/numbered list items → template-like structure

## Code Signals

### Hallucinated Packages
Check against: PyPI, npm, Maven registries. Known hallucinations: `super-fast-json-parser`, `ai-content-filter-pro`

### Fabricated Functions
AST-parse → verify API existence. Watch for methods that "should" exist but don't.

### Hardcoded Secrets
Regex patterns for: API keys, tokens, passwords, connection strings

### Vulnerable Patterns
- SQL injection (string concatenation in queries)
- Command injection (unsanitized shell inputs)
- Off-by-one errors in AI-generated loops

## Image Signals

- **Variance**: Pixel variance extremely low or high
- **Symmetry**: Left/right halves nearly identical (except faces/architecture)
- **Anatomical artifacts**: Finger anomalies, face distortions
- **Physical impossibility**: Wrong shadows, reflections, perspective

## Behavioral Signals

- Very high upload frequency → mass generation
- Many similar titles/thumbnails → content farm
- Cross-posting on many domains → SEO play
- Sudden topic changes → opportunism
- New accounts with high output rate → slop producer
- Clusters with mutual citations → citation inflation

## Provenance Signals

| Signal | Interpretation |
|--------|---------------|
| C2PA present | Useful but not sufficient |
| Watermark/SynthID | Useful but not complete |
| Platform AI label | Helpful but inconsistent |
| Missing authorship | Suspicious |
| False authorship | Strong suspicion |
| Disclosed AI + human review | Rather exonerating |

## Statistical/ML Methods

1. **DetectGPT** (Mitchell et al. 2023): Curvature-based probability discrimination
2. **Binoculars** (Hans et al. 2024): Zero-shot LLM detection (AUROC ~0.95)
3. **NewsGuard × Pangram Labs**: Domain-scale detection (3,000+ farms tracked)
4. **Perplexity distribution**: Unusually uniform/low perplexity = AI-generated

## Thresholds

| Score | Risk | Action |
|-------|------|--------|
| 0.00–0.24 | 🟢 Clean | Normal use |
| 0.25–0.39 | 🟡 AI-Assisted | Cross-check |
| 0.40–0.69 | 🟠 Suspicious | Not primary source |
| 0.70–0.89 | 🔴 Slop | Do not cite/store |
| 0.90–1.00 | ⚫ Malicious | Block, flag |

## Scoring Formula

```
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, sum(weights[s.severity] * s.confidence) / max(1, n))
is_slop = (slop_score >= 0.4) OR (any critical) OR (≥ 2 high severity)
```
