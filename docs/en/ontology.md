# AI Slop Ontology — Canonical Definition

## ⚠️ Core Paradigm: AI Slop is a Risk Profile, Not a Binary Type

**AI Slop is not simply "AI-generated content".** Slopness emerges from the **combination** of synthetic generation, low human care, mass scaling, manipulative distribution, weak provenance, and quality deficiencies. A piece of content can be AI-generated and high-quality. Conversely, human spam can be worthless. (Shaib et al. 2025, Spotify Policy)

---

## AI Slop (Working Definition)

**AI Slop** (also "Slop Content" or simply "Slop") is digital content created with generative AI (LLMs, image/video generators, etc.) that is perceived as low-effort, low-quality, generic, superficial, or meaning-poor. It is produced en masse to obtain attention (Attention Economy), clicks, ad revenue, or other monetary advantages. The term has a pejorative connotation similar to spam and was chosen as Word of the Year in 2025 by Merriam-Webster and the American Dialect Society.

**Origins:** Around 2022 with the spread of image generators (e.g., on 4chan), popularized among others by Simon Willison in 2024. Earlier terms such as "AI garbage" or "AI pollution" were displaced.

---

## Core Characteristics (Prototypical Properties)

According to academic analysis (Kommers et al., 2026), AI Slop is characterized by the following properties:

1. **Superficial Competence:** Grammatically correct, photorealistic, or structured, but lacking depth, originality, or genuine intention.
2. **Asymmetric Effort:** Minimal input (prompt) for massive output; missing human revision, research, or creativity.
3. **Mass Producibility:** Scalable for algorithms (SEO, feeds), often with clickbait elements.

**Further Dimensions:**
- **Instrumental Utility:** Purpose (Monetization → Propaganda → Art → Trolling)
- **Degree of Personalization:** Mass (generic) → Personalized (tailored)
- **Surrealism Level:** Banal-realistic to absurd (e.g., "Shrimp Jesus")

---

## Ontology Structure

### 1. Core Concept: AI Slop

| Attribute | Value Range |
|----------|-------------|
| Production Effort | Low (asymmetric) |
| Perceived Quality | Low (generic, repetitive, uncanny) |
| Intent | Monetization, Engagement Farming, Propaganda, Spam |
| Detectability | Stylistic tics, artifacts, lack of provenance |

### 2. Media Types (Classes)

#### Text Slop
Generic articles, SEO content, books, comments, memos.

| Indicator | Description |
|-----------|-------------|
| Excessive Lists | Every paragraph turns into a bullet list |
| Em-Dashes | Excessive use of "—" |
| Verbosity | Many words, little substance |
| Clichés | "In today's fast-paced world..." |
| Low Information Density | unique_words / total_words < 0.40 |

#### Image/Video Slop
Uncanny-valley images/videos (bizarre combinations, smooth textures, morphing, wrong physics).

**Examples:** Shrimp Jesus, Cat Soap Operas, Fake-Historical Photos, Veteran Birthday Signs

| Indicator | Description |
|-----------|-------------|
| Extra Limbs | Additional fingers/limbs |
| Unnatural Smoothness | Overly perfect textures |
| Distorted Text | Gibberish in the image |
| Over-Symmetry | Non-natural symmetry |

#### Audio/Music Slop
Generated voices/songs lacking emotionality.

**Examples:** Velvet Sundown (Fake Band on Spotify)

#### Hybrid/Multimodal
AI thumbnails + voiceover + text. The growing dominant form.

### 3. Taxonomy by Purpose

| Purpose | Description | Examples |
|---------|-------------|-----------|
| **Engagement/Clickbait Slop** | Viral potential | Motivational, Emotional Bait ("Veteran Birthday") |
| **SEO/Content Farm Slop** | Keyword-stuffed for ads | 10-Websites-to-Leverage-AI articles |
| **Propaganda/Disinfo Slop** | Political | Trump-AI-Images, Spamouflage (China/Russia) |
| **Monetization Slop** | Direct revenue | Facebook Bonuses, Fake Shops, Affiliate Farming |
| **Spam/Noise Slop** | Filler material | No clear purpose, slips through |

### 4. Taxonomy by Form/Quality

| Axis | Low | High |
|-------|-----|------|
| Surrealism | Banal-realistic (SEO article) | Absurd (Shrimp Jesus) |
| Personalization | Mass (generic) | Personalized (tailored) |
| Human Oversight | Pure AI | AI-assisted with minimal edits |

### 5. Quality Dimensions / Slop Indicators (Shaib et al. 2025)

| Theme | Dimension | Code | Slop-Signal |
|-------|-----------|------|-------------|
| **Information Utility** | Density | IU1 | unique_words / total_words < 0.40 |
| **Information Utility** | Relevance | IU2 | Irrelevant tangents, topic drift |
| **Information Quality** | Factuality | IQ1 | Hallucinations, fabrications |
| **Information Quality** | Bias | IQ2 | Systematic skew |
| **Style Quality** | Repetition | SQ1 | Token repetition > 0.20 |
| **Style Quality** | Templatedness | SQ2 | Formulaic structure, POS pattern |
| **Style Quality** | Coherence | SQ3 | Jumps, inconsistency |
| **Style Quality** | Fluency | SQ4 | Paradox: too fluent = slop |
| **Style Quality** | Verbosity | SQ5 | Many words, little substance |
| **Style Quality** | Word Complexity | SQ6 | Unnecessarily complex vocabulary |
| **Style Quality** | Tone | SQ7 | Uniform, unnatural |

---

## Slopsquatting (Code-Slop Security Threat)

AI hallucinates package names → attackers register them → supply chain attack.

| Statistic | Value |
|-----------|------|
| Overall hallucination rate | 19.7% |
| Open-Source Models | 21.7% |
| GPT-4 Turbo | 3.59% |
| CodeLlama | >33% |
| Unique hallucinated names | 205,000+ |

**Real Incidents:**
- `huggingface-cli`: 30,000+ downloads in 3 months (empty package)
- `react-codeshift`: 237 repositories infected via AI-Agent-Skills
- `unused-imports`: Real malware, 233 downloads/week

---

## Knowledge Collapse (3-Stage Model)

| Stage | Name | Facts | Format | Danger |
|---------|------|--------|--------|--------|
| A | Knowledge Preservation | ✅ Correct | ✅ Intact | Low |
| B | Knowledge Collapse | ❌ Wrong | ✅ Correct | **CRITICAL** — "Confidently Wrong" |
| C | Instruction Collapse | ❌ Random | ❌ Incoherent | High, but detectable |

**Stage B is the "Valley of Dangerous Competence":** Surface metrics show no problems, but factual accuracy degrades invisibly.

---

## Engagement Farming (Root Cause Analysis)

AI Slop is not the cause — it is the symptom of a broken Attention Economy:

1. **Incentive System:** Content → Engagement → Revenue (independent of quality)
2. **Costs:** AI reduces production costs to nearly €0
3. **Targeting:** Older users (Facebook: 24% over 55) are the primary victims
4. **Impact:** Real creators are displaced ("put a ton of people out of business")
5. **Platform Double Standard:** Real creators are pursued for guidelines, slop slips through

---

## Normative Framings

| Framing | Core |
|---------|------|
| **Epistemic Pollution** | Pollution of the information ecosystem |
| **Automation Bias** | Humans trust AI blindly |
| **Illegitimate Reason-Giving** | AI has no epistemic standing |
| **Nonconsensual Imposition** | Unreviewed AI = unpaid labour for recipients |
| **Attention Economy Exploitation** | Content optimized for engagement, not information |
| **Consumer Fraud** | Fake products/reviews |
| **Supply Chain Attack** | Slopsquatting as security risk |
| **Democratic Harm** | Political slop undermines democracy |

### 6. Detection Red Flags

#### Text
| Red Flag | Description | Confidence |
|----------|-------------|----------|
| Overused Phrases | "delve", "tapestry", "in today's fast-paced world" | 0.8 |
| Emojis in Code | Emojis in code comments/documentation | 0.85 |
| Perfect but Soulless | Perfect structure but no human touch | 0.7 |
| Excessive Lists | Every paragraph turns into a bullet list | 0.75 |
| Trailing Morals | Ends with a generic moral/lesson | 0.8 |
| Em-Dash Overuse | Excessive use of "—" | 0.85 |
| Low Information Density | unique_words / total_words < 0.40 | 0.9 |
| Uniform Sentence Length | All sentences similar length, low burstiness | 0.7 |

#### Image/Video
| Red Flag | Description | Confidence |
|----------|-------------|----------|
| Glossy Textures | Overly perfect, shiny textures | 0.7 |
| Warped Backgrounds | Distorted backgrounds | 0.8 |
| Inconsistent Details | Details change depending on zoom | 0.85 |
| Morphing | Objects deform unnaturally | 0.8 |
| Bad Text Rendering | Gibberish in the image | 0.95 |
| Extra Limbs | Additional fingers/limbs | 0.9 |
| Frame Flicker | Flickering between video frames | 0.85 |

#### General
| Red Flag | Description | Confidence |
|----------|-------------|----------|
| Missing Provenance | No watermarks, sources, origin | 0.6 |
| Mass Production Pattern | Same template across hundreds of pieces of content | 0.85 |
| No Author Identity | Fake authors (AI headshots, no history) | 0.8 |
| Cross-Lingual Artifacts | Hindi/other language patterns in English output | 0.7 |

---

### 7. Actors & Ecosystem

#### Producers (Slop Farmers / Sloppers)
Individuals/firms in developing countries (India, Kenya, Philippines) who scale with prompts.

**Patterns:**
- Cross-Lingual Prompts (Hindi etc.) → absurd outputs
- AI headshots for fake authors
- Identify existing viral content → AI replicates it
- 80+ AI pins/day on Pinterest

**Known Cases:**
| Name | Method | Target Group | Scaling |
|------|---------|-----------|------------|
| Jesse Cunningham | Facebook + Pinterest Slop Farming | 50+ female | 8.6M monthly views (Bonsai Mary) |
| Content Goblin Users | AI-powered listicle generator → faux blogs | All | Thousands of AI articles |

#### Platforms
| Platform | Role | Amplifier |
|-----------|-------|----------|
| **Facebook** | Primary victim (24% of users over 55) | Performance Bonus Program, Algorithm rewards engagement |
| **YouTube** | 278 AI channels, 63 billion views/year | YouTube Kids: 40% AI-Slop |
| **TikTok** | AI-Video-Slop (Cat Soap Operas) | For You Page favors novelty |
| **Pinterest** | Aspirational AI-Slop (Fake-Plants) | 8.6M Views for individual accounts |
| **Google Search** | AI Overviews amplify slop | SEO-Slop ranks through volume |
| **Spotify** | Fake Artists, millions of listeners | Royalty-Multiplication |

#### Consumers
| Consumer | Role | Vulnerability |
|----------|-------|---------------|
| **Algorithms** | Engagement signals → amplification | Volume + Engagement = quality-independent |
| **Users** | Unaware consumers | Older users, low AI literacy |
| **Advertiser** | Programmatic ads on slop inventory | Cheap inventory, but declining trust |

---

### 8. Impacts

#### Web/Search
- **Content Collapse:** Real content is displaced by slop
- **SEO Degradation:** Worse rankings for researched content
- **Model Collapse:** Training on AI output → irreversible degradation (Nature 2024)
- **Knowledge Collapse:** Facts decay, fluency remains ("Confidently Wrong")

#### Society
- **Misinfo:** AI-generated disinformation spread en masse
- **Trust Erosion:** Declining trust in digital content
- **Democracy Risks:** Political slop undermines discourse
- **Creator Displacement:** Real creators lose income ("put a ton of people out of business")

#### Economy
- **Cheap Ad Inventory:** Slop provides cheap advertising inventory
- **Declining Engagement:** Long-term decline in user engagement
- **Creator Economy:** Blogging/Food/Craft sectors affected

---

### 9. Relationships & Dynamics

| Relationship | Mechanism | Outcome |
|-----------|------------|----------|
| Slop → Algorithm | Volume + Engagement > Quality | Positive Feedback Loop |
| Slop → Human Content | Enshittification | Real creators displaced |
| Detection → Mitigation | Watermarking, Filters, HITL, Policies | Arms Race |
| Slop vs. Valuable AI | Human Oversight, Effort, Utility | **Not all AI is Slop** |

**Key Distinction:** The difference between slop and valuable AI content lies in:
- **Human Oversight** — Is human revision present?
- **Effort** — Genuine effort or just prompt→output?
- **Utility** — Real informational gain or filler material?

---

### 10. Countermeasures & Future

#### Detection
- Linguistic Patterns: Buzzword frequency, em-dash rate, sentence burstiness
- Statistical Analysis: Perplexity, Information Density, Repetition Ratio
- Watermarking: Cryptographic token partitioning (Green/Red Lists)
- Community Tools: Kagi SlopStop, SlopDetector.org, GPTZero, Originality.ai

#### Platforms
- Better automatic moderation
- Mandatory AI-content labeling
- Algorithm Adjustment: Quality signals instead of pure engagement

#### User/Agent Level
- Provenance Checks: C2PA, Watermarks, Reverse Image Search
- Quality Scoring: Compute Slop Score (Density, Repetition, Verbosity)

#### Risks
- **Arms Race:** Better generators evade detection — cat-and-mouse game
- **Positive Potential:** Careful AI use is NOT slop — the distinction remains important

---

### 11. Slopness as a Risk Profile

**Slopness Score = f(Generation, Care, Scaling, Distribution, Provenance, Quality)**

| Dimension | Low Risk (0-2) | Medium Risk (3-5) | High Risk (6-10) |
|-----------|----------------|-------------------|------------------|
| **Generation** | Human-written | AI-assisted, human-edited | Pure AI, no edit |
| **Care** | Thorough research, testing | Superficial check | No verification |
| **Scaling** | Single article | Series, curated | Mass production (100+/day) |
| **Distribution** | Organic, targeted | SEO-optimized | Clickbait, Engagement Farming |
| **Provenance** | Clear authorship, sources | Partial sources | Fake author, no sources |
| **Quality** | Original, informative | Generic, partly useful | Substanceless, repetitive |

### 12. Agent Risk Levels

| Level | Description | Agent Behavior |
|-------|-------------|----------------|
| 🟢 **Clean** | Human, reviewed, with sources | Use normally |
| 🟡 **AI-Assisted** | AI-generated, human-edited, useful | Use with source attribution |
| 🟠 **Suspicious** | AI-generated, no sources, generic | Verify before use |
| 🔴 **Slop** | AI-generated, substanceless, mass-produced | **DO NOT include in RAG/Memory** |
| ⚫ **Malicious** | Slop + intent (Disinfo, Slopsquatting) | **Block + warn** |

### 13. Retrieval Collapse ⚠️ (Agent-specific)

**For agents, AI Slop is particularly dangerous** because RAG, search, and memory systems become contaminated.

**Two Stages:**
1. **Source Dominance:** AI-generated content dominates search results → reduced source diversity
2. **Pipeline Contamination:** Low-quality content penetrates retrieval pipelines → agents respond with slop

**Experimentally:** 67% pool contamination → over 80% exposure contamination.

**Countermeasures:**

| Measure | Implementation |
|----------|---------------|
| Source Diversity Check | Min. 3+ different source domains |
| Slop Score Gate | Only include sources with score < 0.4 |
| Provenance Filter | Prefer human-verified sources |
| Cross-Validation | Min. 2 independent confirmations |
| Contamination Detection | Check information diversity of the top 10 |

### 14. AI Slop vs. Spam

| | Spam | AI Slop |
|---|------|--------|
| **Primary** | Unwanted distribution | Cheap generation + superficiality |
| **Mechanism** | Volume + Deception | Superficial Competence + Mass Producibility |
| **Google** | — | "Scaled Content Abuse" = search manipulation, not user help |

**Overlap:** Slop CAN be spam, but not all slop is spam and not all spam is slop.

### 15. Platform Statistics (2026)

| Metric | Value | Source |
|--------|------|--------|
| Deezer AI tracks/day | ~75,000 (44% of uploads) | Deezer 20.04.2026 |
| YouTube AI channels | 278 (63 billion views/year) | Research |
| YouTube Kids AI share | ~40% | Analysis |
| Facebook users >55 | 24% | Platform Data |
| AI package hallucination | 19.7% of recommendations | USENIX 2025 |
| Pinterest slop account | 8.6M Monthly Views | Futurism |

---

## Sources

1. Kommers et al. (2026): "Why Slop Matters" — ACM AI Letters (arXiv: 2601.06060)
2. Shaib et al. (2025): "Measuring AI 'Slop' in Text" — Northeastern/Meta AI (arXiv: 2509.19163)
3. MINT Lab (2026): "AI Slop: Definitions and Normative Status"
4. Keisha et al. (NeurIPS 2025): "Knowledge Collapse in LLMs" (arXiv: 2509.04796)
5. USENIX Security 2025: "We Have a Package for You!" — Package Hallucination Study
6. Shumailov et al. (Nature 2024): "AI models collapse when trained on recursively generated data"
7. Carrigan (2026): "Engagement Farming" Essay
8. Futurism: Cunningham Slop Farmer Exposé
9. Aikido Security: Slopsquatting Incident Reports
10. Wikipedia: "AI slop"
11. SlopDetector.org: 5-Type Taxonomy
12. Hypogenic AI: "Predicting Slop Before It Happens"
