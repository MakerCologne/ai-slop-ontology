# Deep Research: AI Slop Ontology v0.1

## Working Definition

**AI Slop is not simply "AI-generated content"**, but low-quality, often mass-produced synthetic or AI-assisted content that appears superficially plausible but offers little substance, originality, care, fact-checking or genuine value.

- **Merriam-Webster:** Low-quality digital content, usually produced in quantity and by means of AI
- **American Dialect Society:** "Low-quality, high-quantity content" (AI context is now often implicit)

**The most important point for an agent ontology:** AI Slop is **not a binary media type, but a risk profile**. Content can be AI-generated and high-quality. Conversely, human spam can be equally worthless. "Slopness" arises from the **combination** of:
- Synthetic generation
- Low human care
- Mass scaling
- Manipulative distribution
- Weak provenance
- Quality defects

Research on "Measuring AI Slop in Text" describes slop judgments as partly subjective, but correlated with dimensions like coherence and relevance. Spotify formulates this for music: AI use is a **spectrum**, not a simple "AI / not AI" binary.

---

## 1. Central Findings

### 1.1 AI Slop is a new form of spam, but not identical to spam

Classic spam is primarily unwanted distribution. AI Slop adds to this:
- **Cheap generation** — Production costs ~€0
- **Semantic superficiality** — Seems plausible, is substanceless
- **Algorithmic scaling** — Optimized for platform mechanics

**Google "Scaled Content Abuse":** Many pages produced primarily for search manipulation rather than to help users. Explicitly included: generative AI pages without added value, scraping, stitching and keyword-laden pages without meaning.

### 1.2 The three core features of a prototype (Kommers et al. 2026)

| Property | Description |
|-------------|-------------|
| **Superficial Competence** | Appearance of quality without depth |
| **Effort Asymmetry** | Extremely low generation effort vs. human production |
| **Mass Producibility** | Embedding in ecosystems of mass production/consumption |

**Additionally, slop varies along:** Instrumental utility, personalization, surrealism.

### 1.3 The problem is platform-economic

AI Slop emerges particularly strongly where platforms reward attention, reach, search ranking or royalties.

| Platform | Slop statistic | Consequence |
|-----------|----------------|------------|
| **YouTube** | "Mass-produced or repetitive content" = "inauthentic content" → not monetizable | Policy exists, but enforcement spotty |
| **Deezer** | ~75,000 AI tracks/day (as of 04/20/2026) = **44% of daily uploads** | Most streams identified as fraudulent and demonetized |
| **Spotify** | AI use = spectrum, not binary | Royalty multiplication through fake artists |
| **Facebook** | 24% of users over 55, low AI literacy | Primary victim of engagement farming |
| **Google** | "Scaled content abuse" explicitly in spam policies | SEO slop still ranks through volume |

### 1.4 AI Slop is particularly dangerous for agents via retrieval ⚠️

**For agents, AI Slop is dangerous** because it not only deceives humans, but **contaminates RAG, search and memory systems**.

**"Retrieval Collapse" — Two stages:**

| Stage | What happens | Consequence |
|-------|-------------|-------|
| **1. Source dominance** | AI-generated content dominates search results | Reduced source diversity |
| **2. Pipeline contamination** | Inferior/adversarial content infiltrates retrieval pipelines | Agents answer with slop |

**Experimental finding:** 67% pool contamination → over 80% exposure contamination.

**This means for agent architecture:** Slop resilience is not optional, but a core requirement for RAG and memory systems.

### 1.5 Long-term, data and model degradation threatens

**Nature (Shumailov et al. 2024):** "Model Collapse" — a degenerative process in which data from generative models pollutes the training set of later models.

- Models lose information about the original distribution
- Especially **rare edge regions** (long tail) are lost
- Real human data remains important for learning tasks with relevant distribution tails
- Mass-published LLM content pollutes later training data

**Knowledge Collapse (3-stage model):**

| Stage | Facts | Format | Danger |
|---------|--------|--------|--------|
| A: Preservation | ✅ Correct | ✅ Intact | Low |
| **B: Collapse** | **❌ Wrong** | **✅ Correct** | **CRITICAL — "Confidently Wrong"** |
| C: Instruction Collapse | ❌ Random | ❌ Incoherent | High, but recognizable |

---

## 2. Slopness as a risk profile (core concept for the ontology)

**Slopness Score = f(Generation, Care, Scaling, Distribution, Provenance, Quality)**

| Dimension | Low Risk (0-2) | Medium Risk (3-5) | High Risk (6-10) |
|-----------|----------------|-------------------|------------------|
| **Generation** | Human-written | AI-assisted, human-edited | Pure AI, no edit |
| **Care** | Thorough research, testing | Superficial review | No verification |
| **Scaling** | Single article | Series, curated | Mass production (100+/day) |
| **Distribution** | Organic, targeted | SEO-optimized | Clickbait, Engagement Farming |
| **Provenance** | Clear authorship, sources | Partial sources | Fake author, no sources |
| **Quality** | Original, informative | Generic, partly useful | Substanceless, repetitive |

**Key Insight:** Not all AI is slop. The difference lies in the combination of the dimensions.

---

## 3. Taxonomy (extended)

### 3.1 By Purpose

| Purpose | Description | Examples |
|---------|-------------|-----------|
| **Engagement/Clickbait** | Viral potential | Veteran Birthday, Shrimp Jesus |
| **SEO/Content Farm** | Keyword-stuffed for ads | "10 Ways to Leverage AI" |
| **Propaganda/Disinfo** | Politically motivated | Trump-Pope, Spamouflage |
| **Monetization** | Direct revenue | Facebook Bonuses, Fake Shops |
| **Spam/Noise** | Filler material | No clear purpose |
| **Supply Chain Attack** | Slopsquatting | Hallucinated packages (19.7% rate) |

### 3.2 By Form

| Axis | Low | High |
|-------|-----|------|
| Surrealism | Banal-realistic | Absurd (Shrimp Jesus) |
| Personalization | Mass | Personalized |
| Human Oversight | Pure AI | AI-assisted + Edits |

### 3.3 By risk profile for agents ⚠️ NEW

| Risk Level | Description | Agent Behavior |
|-------------|-------------|----------------|
| **🟢 Clean** | Human, verified, with sources | Use normally |
| **🟡 AI-Assisted** | AI-generated, but human-edited, useful | Use with citation |
| **🟠 Suspicious** | AI-generated, no sources, generic | Verify before use |
| **🔴 Slop** | AI-generated, substanceless, mass-produced | **Do not include in RAG/Memory** |
| **⚫ Malicious** | Slop + intent (Disinfo, Slopsquatting) | **Block + Warn** |

---

## 4. Retrieval Collapse — The agent-specific problem ⚠️

### 4.1 The problem

```
User Question → Agent → RAG/Search → [Slop-contaminated Results] → Slop-Answer
                                     ↑
                              67% Pool-Kontamination
                              → 80%+ Expositionskontamination
```

### 4.2 Countermeasures for agents

| Measure | Description | Implementation |
|----------|-------------|----------------|
| **Source Diversity Check** | At least 3+ different sources | `len(set(source_domains)) >= 3` |
| **Slop Score Gate** | Only include sources with score < 0.4 | `slop_score(doc) < 0.4` |
| **Provenance Filter** | Prefer human-verified sources | Source-Attribution, Peer Review, Edit History |
| **Recency vs. Authority** | Newer ≠ better. Prefer older established sources | Domain Authority Score |
| **Contamination Detection** | Recognize when search results are slop-dominated | Check information diversity of the top-10 results |
| **Cross-Validation** | Check facts against independent sources | At least 2 independent confirmations |

---

## 5. Slopsquatting — Code Slop as a security threat

| Statistic | Value |
|-----------|------|
| Overall hallucination rate | 19.7% |
| Open-source models | 21.7% |
| GPT-4 Turbo | 3.59% |
| CodeLlama | >33% |
| Unique hallucinated names | 205,000+ |

**Real incidents:** huggingface-cli (30K+ downloads), react-codeshift (237 repos), unused-imports (malware)

---

## 6. Platform Statistics (2026)

| Metric | Value | Source |
|--------|------|--------|
| Deezer AI tracks/day | ~75,000 (44% of uploads) | Deezer 04/20/2026 |
| YouTube AI channels | 278 (63 billion views/year) | Research |
| YouTube Kids AI share | ~40% | Analysis |
| Facebook users >55 | 24% of users | Platform Data |
| AI package hallucination | 19.7% of recommendations | USENIX 2025 |
| Pinterest slop account | 8.6M monthly views (single case) | Futurism |

---

## 7. Sources & References

1. Kommers et al. (2026): "Why Slop Matters" — ACM AI Letters (arXiv: 2601.06060)
2. Shaib et al. (2025): "Measuring AI Slop in Text" (arXiv: 2509.19163)
3. Shumailov et al. (Nature 2024): "AI models collapse when trained on recursively generated data"
4. Keisha et al. (NeurIPS 2025): "Knowledge Collapse in LLMs" (arXiv: 2509.04796)
5. USENIX Security 2025: "We Have a Package for You!" — Package Hallucination Study
6. "Retrieval Collapse" — RAG Contamination Research
7. Google Spam Policies: "Scaled Content Abuse"
8. Deezer AI Content Report (04/20/2026): 75K tracks/day
9. Spotify AI Policy: AI use as a spectrum
10. Carrigan (2026): "Engagement Farming" Essay
11. Futurism: Cunningham Slop Farmer Exposé
12. MINT Lab (2026): "AI Slop: Definitions and Normative Status"
13. Wikipedia: "AI slop"
14. Merriam-Webster: Word of the Year 2025
