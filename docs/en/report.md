> Research by Goswin | zai/glm-5.1 | 2026-05-20
> Queries: "AI slop ontology taxonomy definition", "AI slop detection methods tools automated", "AI slop categories types examples", "knowledge collapse epistemic pollution", "AI slop image video audio multimodal", "Why Slop Matters Kommers"
> Pages fetched: 9 | Depth: Large (🟢)

# AI Slop — Deep Research Report

## Executive Summary

AI Slop is an established term (Merriam-Webster Word of the Year 2025) for low-quality, mass-produced AI-generated content. Academic research developed the first formal taxonomies in 2025–2026 (Shaib et al., Kommers et al.), but a **machine-readable ontology for agents** does not yet exist. Stefan has already done substantial preliminary work in his GitHub repos: `quality-agent` contains a 200-line slop reference, `local-ai-setup` a complete multi-modal detection skill with 22 techniques and Python implementation.

---

## 1. Definitions & Academic State

### 1.1 Core Definitions

| Source | Definition |
|--------|------------|
| **Merriam-Webster** (Word of the Year 2025) | "Digital content of low quality that is produced usually in quantity by means of artificial intelligence" |
| **Simon Willison** (Coined 05/2024) | "Mindlessly generated and thrust upon someone who didn't ask for it" — analogy to spam |
| **Wikipedia** | "Digital content made with generative AI that is perceived as lacking in effort, quality, or meaning, and produced in high volume" |
| **Cambridge Dictionary** | "Content on the internet that is of very low quality, especially when it is created by artificial intelligence" |
| **Kommers et al. (2026)** | Three prototypical properties: Superficial Competence, Asymmetric Effort, Mass Producibility |

### 1.2 Key Papers

1. **Kommers et al. (Jan 2026): "Why Slop Matters"** — ACM AI Letters. Argues that slop fulfills a social function (supply-side solution for cultural demand) and has aesthetic value. Three properties: Superficial Competence, Asymmetric Effort, Mass Producibility. Three variance dimensions: Instrumental Utility, Personalization, Surrealism. (arXiv: 2601.06060)

2. **Shaib et al. (Sep 2025, rev. Jan 2026): "Measuring AI 'Slop' in Text"** — Northeastern/Meta AI. First systematic measurement framework. 19 expert interviews → 3 themes × 12 codes: Information Utility (Density, Relevance), Information Quality (Factuality, Bias), Style Quality (Repetition, Templatedness, Coherence, Fluency, Verbosity, Word Complexity, Tone). Span-level annotation on 150 news + 100 QA passages. (arXiv: 2509.19163, GitHub: cshaib/slop)

3. **MINT Lab (March 2026): "AI Slop: Definitions and Normative Status"** — Comprehensive literature analysis (14 papers). Four normative framings: Epistemic Pollution, Automation Bias, Illegitimate Reason-Giving, Nonconsensual Imposition. Technical cause: LLMs generate output "towards the center of the distribution" → systematic avoidance of the long tail.

---

## 2. Taxonomies

### 2.1 SlopDetector.org — 5 Text Slop Types

| Type | Recognition Phrase | Description |
|-----|------------------|-------------|
| **Generic Slop** | "In today's fast-paced world..." | Vague, generic introductions without substance |
| **Pseudo-Insight Slop** | "The key is to find balance..." | Sounds profound, but says nothing |
| **Fake Authority Slop** | "Studies have shown..." | Authoritative tone without real sources |
| **Wikipedia Rehash** | "X is defined as..." | Rephrased general knowledge without analysis |
| **Wellness Slop** | "Self-care isn't selfish..." | Universalized self-help without personal experience |

Antidote: Specificity, Lived Experience, Cited Sources, Information Gain.

### 2.2 Shaib et al. — 3 Themes × 12 Codes

```
Information Utility (IU)
├── IU1: Density (5 experts)
└── IU2: Relevance (9 experts)

Information Quality (IQ)
├── IQ1: Factuality (7 experts)
└── IQ2: Bias (2 experts)

Style Quality (SQ)
├── SQ1: Repetition (7 experts)
├── SQ2: Templatedness (2 experts)
├── SQ3: Coherence (6 experts)
├── SQ4: Fluency (4 experts)
├── SQ5: Verbosity (5 experts)
├── SQ6: Word Complexity (1 expert)
└── SQ7: Tone (3 experts)
```

### 2.3 Kommers et al. — 3 Prototypical Properties + 3 Variance Dimensions

**Prototypical Properties:**
- **Superficial Competence**: Appears competent, but is substanceless on closer inspection
- **Asymmetric Effort**: Creation requires disproportionately less effort than without AI
- **Mass Producibility**: Part of a digital ecosystem of mass production

**Variance Dimensions:**
- **Instrumental Utility**: Why was it created? (Money → Art → Trolling)
- **Personalization**: Is it generic or tailored to a person?
- **Surrealism**: From absurdly implausible to deceptively realistic

### 2.4 SlopScan Hackathon (May 2026) — 8 Domains

Code Review | Docs & KBs | Hiring & Resumes | Communications | Content & SEO | Academia | Marketplaces | Social & News

---

## 3. Media Types & Examples

### 3.1 Text Slop
- SEO spam articles ("10 Ways to Leverage AI")
- AI-generated LinkedIn posts
- Hollow PR descriptions
- Fake scientific papers
- AI-generated Amazon reviews

### 3.2 Image Slop
- **Shrimp Jesus** (Facebook virals, bizarre AI creations)
- Fake veteran images ("Today's my birthday, please like")
- AI plant images for fake seed sales
- Holocaust victim forgeries
- Political propaganda (Trump as Pope, Musketeer, etc.)

### 3.3 Video Slop
- 278 YouTube channels with AI content (63 billion views/year)
- YouTube Kids: 40% AI slop (alphabet videos with nonsensical content)
- AI-generated "Cat Soap Operas", "Fruit Love Island" (TikTok)

### 3.4 Audio/Music Slop
- Fake artists on Spotify with millions of listeners
- Velvet Sundown (AI-created band)

### 3.5 Code Slop
- Hallucinated packages ("slopsquatting" attacks)
- Uniformly generic code style without a human touch
- Bulk-generated commits without review
- Fake review comments

---

## 4. Normative Framings (Why slop is problematic)

1. **Epistemic Pollution** — Pollution of the information ecosystem. Van Rooij (2025): "Epistemicide". Coeckelbergh (2026): "Epistemic Laziness". Peterson (2025): "Knowledge Collapse" — Society moves 2.3x further from the truth with only a 20% AI content cost reduction.

2. **Automation Bias** — Humans systematically trust automated outputs too much. Danry et al. (2024): AI-generated deceptive explanations significantly amplify belief in false headlines — cognitive reflection does NOT protect.

3. **Illegitimate Reason-Giving** (Enoch 2012) — AI content presents itself as informative testimony, but the success conditions are missing: no epistemic standing, no accountability, no communicative intention.

4. **Nonconsensual Imposition** (Doctorow 2026) — Sending unreviewed AI output to strangers is "coercing a stranger into unpaid labour" (the work of evaluation).

---

## 5. Detection Methods

### 5.1 Statistical Approaches
- **Perplexity** (DetectGPT): Human text > 100 PPL, AI text < 50 PPL
- **Burstiness**: Sentence complexity variation (humans: high, AI: uniform)
- **N-gram frequency**: AI overuses certain word combinations
- **Watermarking**: Cryptographic token partitioning (Green/Red Lists)

### 5.2 ML Classifiers
- RoBERTa fine-tuned on Human/AI corpus (90%+ AUROC controlled)
- Problem: unknown models, post-edited texts, short snippets

### 5.3 Linguistic Patterns (Shaib et al. + SlopDetector)
- Buzzword frequency: delve, realm, tapestry, leverage, synergy, robust, cutting-edge
- Punctuation anomalies: em-dashes, ellipses, excessive exclamation
- Structural quirks: excessive lists, trailing morals, uniform paragraph lengths
- Information Density: Unique Words / Total Words (< 0.40 = Slop)

### 5.4 Existing Tools
- **SlopDetector.org** — Web-based 5-category detector
- **SlopScan Hackathon** (May 29 – June 1, 2026) — Builds detection tools
- **GPTZero, Originality.ai** — AI text detection (but not slop-specific)

---

## 6. Stefan's Preliminary Work on GitHub

### 6.1 `hikaman/quality-agent`
- `docs/refinements/ai.slop.md` — Comprehensive 200+ line reference with all detection techniques, code hallucination examples, reference table
- `.skills/slop-skill/SKILL.md` — Simple skill: text repetition + image variance
- `features/slop_detection.feature` — BDD feature definition
- Integration: AutoGen, LangGraph, MCP tool

### 6.2 `hikaman/local-ai-setup`
- `skills/ai-slop-detection/` — **Complete skill with 16 files**
  - `SKILL.md` (747 lines, 22 techniques) — too large but comprehensive
  - `detectors.py` — Unified Multi-Modal Entry Point
  - `text_detector.py` — Text-specific analysis
  - `image_detector.py` — Image artifact detection
  - `scoring.py` — Slop score calculation
  - `content_quality.py` — Quality metrics
  - `analyzer_enhanced.py` — Extended analysis

### 6.3 `hikaman/skill-reviews`
- `2026-03-16/ai-slop-detection.md` — Detailed review (60/100 score)
  - P0: SKILL.md too large (747 lines → ~120 lines recommended)
  - P1: No progressive disclosure, overlap with ai-quality-assurance
  - Positive: Detection methodology is "genuinely valuable and well-implemented"

---

## 7. Recommendation: AI Slop Ontology for Agents

### 7.1 What's missing

The existing taxonomies are:
- **Shaib et al.**: Academic, not machine-readable
- **SlopDetector**: Web tool, no API/ontology
- **Stefan's skills**: Implementation-focused, no formal ontology
- **Kommers et al.**: Conceptual, but no operationalized form

### 7.2 Ontology Architecture

See `ontology.ttl` (Turtle/RDF) and `ontology.json` (JSON-LD) in this folder.

**Core classes:**
1. `SlopInstance` — A concrete slop observation
2. `SlopType` — Taxonomy of slop types (hierarchical)
3. `SlopDimension` — Measurable dimensions (Density, Relevance, etc.)
4. `SlopSignal` — Recognizable signals/indicators
5. `SlopMedium` — Text, Image, Video, Audio, Code
6. `SlopNormativeFraming` — Why it is problematic
7. `SlopDetection` — Detection methods and tools
8. `SlopCountermeasure` — What can be done about it

**Relationship types:**
- `hasType`, `hasMedium`, `hasSignal`, `hasDimension`
- `measuredBy`, `detectedBy`, `counteredBy`
- `variantOf`, `overlapsWith`, `relatedTo`

### 7.3 Formats

| Format | Purpose |
|--------|-------|
| `ontology.ttl` | RDF/Turtle — standard for semantic ontologies |
| `ontology.json` | JSON-LD — agent-friendly, directly loadable |
| `ontology.md` | Human-readable documentation |

### 7.4 Integration with existing skills

The ontology is meant to complement Stefan's `local-ai-setup/skills/ai-slop-detection/`:
- The skill remains the **implementation** (Python detectors, scoring)
- The ontology becomes the **knowledge model** (classification, relationships, reference)
- Agents load the ontology as context, use the skill for detection

---

## Sources

1. [Wikipedia: AI slop](https://en.wikipedia.org/wiki/AI_slop) — Comprehensive overview with political/cultural examples
2. [SlopDetector.org: Slop Taxonomy](https://slopdetector.org/slop-taxonomy) — 5 text slop types with examples
3. [Shaib et al. (2025): Measuring AI "Slop" in Text](https://arxiv.org/abs/2509.19163) — First academic measurement framework, 12 codes from 19 expert interviews
4. [Kommers et al. (2026): Why Slop Matters](https://arxiv.org/abs/2601.06060) — ACM AI Letters, 3 prototypical properties
5. [MINT Lab (2026): AI Slop: Definitions and Normative Status](https://mintresearch.org/reports/ai-slop/) — Literature analysis, 4 normative framings
6. [Glukhov (2025): Detecting AI Slop](https://www.glukhov.org/post/2025/12/ai-slop-detection/) — Technical detection methods with code
7. [SlopScan Hackathon](https://slopscan.dev/) — 8 domains, 72h hackathon, May 2026
8. [SlopDetector.org: AI Slop Examples](https://slopdetector.org/ai-slop-examples) — 21+ documented cases
9. [Stefan's quality-agent: ai.slop.md](https://github.com/hikaman/quality-agent) — Preliminary detection reference
10. [Stefan's local-ai-setup: ai-slop-detection](https://github.com/hikaman/local-ai-setup) — 22 techniques, multi-modal Python skill
11. [Stefan's skill-reviews: ai-slop-detection.md](https://github.com/hikaman/skill-reviews) — Review with improvement suggestions
