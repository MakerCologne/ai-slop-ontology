---
title: "AI Slop Ontology"
version: "1.0.0"
date: "2026-05-20"
language: "en (German translation: docs/de/ai-slop-ontology-v1.0.0.md)"
intended_consumers: ["LLM agents", "quality-assurance pipelines", "content moderation", "researchers"]
license: "CC BY 4.0 (recommended)"
machine_readable_block: "see §10 (YAML)"
---

# AI Slop Ontology

A structured, agent-consumable knowledge base on the phenomenon of *AI Slop*. Consolidated from academic research (Shaib et al. 2025; Madsen & Puyt 2025; Shumailov et al. 2024), investigative journalism (404 Media; New York Times; Guardian), industry research (NewsGuard; Pangram Labs; BetterUp/Stanford), and lexicography (Merriam-Webster 2025; Oxford Dictionary 2024).

---

## 1. Core Definition

**AI Slop** (class: `Phenomenon`) denotes generatively AI-produced digital content that is perceived as low-quality, generic, misleading, or unsolicited, and is typically produced in high volume in order to capture attention or generate revenue.

**Three convergent lexicon definitions:**

- *Merriam-Webster* (Word of the Year 2025): "digital content of low quality that is produced usually in quantity by means of artificial intelligence" [1].
- *Oxford Dictionary* (Shortlist Word of the Year 2024): "material produced using a large language model, which is often viewed as being low-quality or inaccurate" [2].
- *Willison criterion* (operational heuristic): AI content is slop if it is "mindlessly generated and thrust upon someone who didn't ask for it" [3].

**Necessary conditions (all three must be met):**
1. Generative AI is the primary source of the content.
2. Human care, curation, or verification is missing.
3. The content is published/distributed unsolicited (push rather than pull).

**Delimitation:** Not every AI-generated piece of content is slop. Carefully curated, vetted, and intentionally published AI-assisted outputs are explicitly excluded from the definition (Willison 2024; Shaib et al. 2025 §3).

---

## 2. Etymology and Conceptual History

| Year | Event | Source |
|------|-------|--------|
| ~1700 | "Slop" = soft mud (English) | OED; [4] |
| ~1800 | Semantic extension to "pig swill / refuse" | [4] |
| 2022 | First online occurrences of "AI slop" | [5] |
| Early 2024 | Poet/technologist "deepfates" uses the term on X as "term for unwanted AI generated content" | [4][6] |
| May 2024 | Simon Willison popularizes it on his blog with a spam analogy | [3] |
| 2024 | Oxford Dictionary Word-of-the-Year shortlist (+332 % usage) | [2] |
| 2025 | Merriam-Webster & American Dialect Society: Word of the Year | [1] |
| 2025–2026 | Academic operationalization (Shaib et al., Madsen & Puyt, MINT Lab) | [7][8][9] |

**Historical analogues:** Grub Street (London, 1700s, cheap printed matter), Pulp Fiction, Churnalism, Spam, Kitsch (Munich, 1860s, pejorative for mass-produced art). All denote *mass-produced, economically motivated, aesthetically/epistemically deficient output* of a new production technology [4][10].

---

## 3. Class Hierarchy (Ontology Core)

```
Phenomenon: AISlop
├── ByModality
│   ├── TextSlop
│   │   ├── ArticleSlop          (content farms, UAINs)
│   │   ├── BookSlop             (Amazon AI books)
│   │   ├── RecipeSlop           (SEO recipes)
│   │   ├── AcademicSlop         (fake papers, AI reviews)
│   │   ├── ProductReviewSlop    (fake reviews)
│   │   └── Workslop             (Niederhoffer et al. 2025)
│   ├── ImageSlop
│   │   ├── EngagementBaitImage  (Shrimp Jesus, AI Christ)
│   │   ├── DeceptiveProductImage (e-commerce fake plants)
│   │   ├── PoliticalSlopImage   (Trump-Pope, deepfake endorsements)
│   │   └── ArtSlop              (generic AI posters)
│   ├── VideoSlop
│   │   ├── ChildrenContentSlop  (NYT 2026: ~40 % YouTube Kids)
│   │   ├── BrainrotVideo        (Italian brainrot, Fruit Love Island)
│   │   ├── DeepfakeVideo        (Sora abuse)
│   │   └── HistoricalSlopVideo  (oversimplified history)
│   ├── AudioSlop
│   │   ├── AIMusic              (Spotify royalty fraud, Smith 2024)
│   │   ├── VoiceCloneSlop       (AI dubbing)
│   │   └── AINarrationSlop      (Paramount/Novocaine 2025)
│   ├── CodeSlop
│   │   ├── HallucinatedPackage  (super-fast-json-parser etc.)
│   │   ├── FabricatedAPI        (nonexistent methods)
│   │   └── VulnerableAISnippet  (hardcoded secrets, SQL injection)
│   └── MultiModalSlop           (image+text+audio combined)
│
├── ByIntent
│   ├── MonetizationSlop         (creator bonus, MFA sites, ad fraud)
│   ├── PoliticalSlop            (election interference, propaganda)
│   ├── DisinformationSlop       (Russia/Iran operations)
│   ├── AccidentalSlop           (well-intentioned, poor quality)
│   ├── HumorousSlop             (meme culture, Fruit Love Island)
│   └── WorkplaceSlop            (Workslop: performance theater)
│
├── ByActor
│   ├── ContentFarm              (NewsGuard: 3,006+ sites Mar 2026)
│   ├── SoloMonetizer            (India/Philippines/Kenya creators)
│   ├── StateActor               (Storm-1516, Center for Geopolitical Expertise)
│   ├── Corporation              (Activision, Paramount, A24, Amazon)
│   ├── PoliticalCampaign        (Trump posts, Cuomo)
│   └── AutomatedBot             (bot networks, AI agents)
│
└── ByPlatform
    ├── SocialMedia              (Facebook, Instagram, TikTok, X)
    ├── SearchResult             (Google: 19 % AI share Jan 2025)
    ├── EcommerceListing         (Amazon, eBay)
    ├── StreamingService         (Spotify, YouTube, Netflix-style)
    └── EnterpriseChannel        (email, Slack, Docs → Workslop)
```

---

## 4. Quality Dimensions (Operational Taxonomy)

Consolidated from Shaib et al. 2025 (three themes, seven codes), validated on 213 news articles and 123 QA passages.

### 4.1 Information Utility (IU)
| Code | Name | Operationalization | Measurement Method |
|------|------|--------------------|--------------------|
| `IU1` | Density | Substantive information per word count | Token entropy (Meister et al. 2021); Propositional Idea Density (Brown et al. 2008) |
| `IU2` | Relevance | Match between content ↔ prompt/task | Expert annotation (Clarke & Dietz 2024) |

### 4.2 Information Quality (IQ)
| Code | Name | Operationalization | Measurement Method |
|------|------|--------------------|--------------------|
| `IQ1` | Factuality | Hallucinations, false claims | Human annotation; fact verification against sources |
| `IQ2` | Bias / Subjectivity | Over-/under-supply of subjective markers | Wiebe lexicon (2004) |

### 4.3 Style Quality (SQ)
| Code | Name | Operationalization | Measurement Method |
|------|------|--------------------|--------------------|
| `SQ1` | Repetition | Lexical repetition | Shaib et al. 2024a |
| `SQ2` | Templatedness | Syntactic POS templates | Shaib et al. 2024b |
| `SQ3` | Coherence | Logical flow, argument structure | Expert annotation (Li et al. 2024) |
| `SQ4` | Fluency | Linguistic naturalness | Human or perplexity |
| `SQ5` | Verbosity | Sentence/passage length | Zhang et al. 2024 |
| `SQ6` | Word Complexity | Unnecessarily complex vocabulary | Gunning-Fog; Flesch-Kincaid |
| `SQ7` | Tone | Over-formality, excess pathos | Fanous et al. 2025; Yang et al. 2024 |

**Empirical findings (Shaib et al. 2025):**
- Strongest slop predictors across all domains: `IU2 Relevance` (β̂=0.06), `IU1 Density` (β̂=0.05), `SQ7 Tone` (β̂=0.05).
- News articles: coherence, tone, density, relevance, bias dominant.
- QA tasks: factuality, structure dominant.
- Binary slop judgments show *moderate subjectivity* (Cohen's κ -0.15 to 0.29); fine-grained codes reach 0.51–0.76 (AC1) for Factuality, Bias, Structure.

---

## 5. Macro-Dimensions (7Vs after Madsen & Puyt 2025) [8]

| Dimension | Definition | Example Metric |
|-----------|------------|----------------|
| `Volume` | Production scale | Items per day/platform |
| `Velocity` | Generation and circulation speed | Latency prompt → publish |
| `Variety` | Range of forms/genres | Modality coverage |
| `Value` | Erosion of cultural/epistemic value | Trust surveys; citation quality |
| `Verification` | Truth and trust problem | Fact-check rate |
| `Visibility` | Algorithmic amplification | Recommendation share |
| `Virality` | Memetic diffusion | Reproduction rate R |

The 7Vs complement the quality taxonomy (Section 4) by capturing *systemic properties* of the slop ecology rather than properties of the individual item.

---

## 6. Detection Techniques (22 Methods)

From the consolidated AI-Slop-Detection heuristic (40+ techniques; v1.0). Most important classes:

### 6.1 Text
1. **Repetition Ratio**: `most_common_token / total_tokens` > 0.20 → HIGH; > 0.30 → CRITICAL.
2. **Buzzword Detection** (14 terms): *delve, realm, tapestry, landscape, unleash, unlock, harness, leverage, paradigm, synergy, robust, cutting-edge, state-of-the-art, game-changing*.
3. **Template-Phrase Detection**: "it's important to note", "in conclusion", "to sum up", "furthermore", "moreover", "as previously mentioned".
4. **Punctuation Anomalies**: em-dash > 0.5/sentence, ellipsis > 0.3/sentence, "!" > 0.2/sentence.
5. **Information Density**: `unique_words / total_words` < 0.40 → verbose slop.
6. **Perplexity Distribution**: unusually uniform/low perplexity distribution.

### 6.2 Code
7. **Hallucinated Package Check**: comparison against registry (PyPI, npm) or list of known hallucinations.
8. **Fabricated Function Detection**: AST parse → verify API existence.
9. **Hardcoded Secret Patterns**: regex for API keys, secrets, tokens.
10. **Inverted Boolean Logic / Off-by-One**: static analysis.

### 6.3 Image
11. **Variance Analysis**: pixel variance extremely low/high.
12. **Symmetry Anomaly**: left/right halves ≈ identical (except for faces/architecture).
13. **Anatomical Artifacts**: finger anomalies (>5 or fused), facial distortions.
14. **Physical Impossibility**: incorrect shadows/reflections/perspective.

### 6.4 Multimodal
15. **Cross-Modal Consistency**: image ↔ caption; code ↔ docs; video ↔ audio.
16. **Watermark Detection**: provider-specific (SynthID, C2PA).

### 6.5 Statistical / ML-based
17. **DetectGPT** (Mitchell et al. 2023): curvature-based probability discrimination.
18. **Binoculars** (Hans et al. 2024): zero-shot LLM detection (AUROC ~0.95).
19. **NewsGuard × Pangram Labs**: domain-scale detection for content farms (3,006+ sites identified, March 2026).
20. **Pangram Labs Models**: proprietary detector model for entire websites.

### 6.6 Structural
21. **Lists-as-Responses**: excessive bullet structures without substance.
22. **Trailing-Moral / Generic-Closing Patterns**: artificial "In summary" brackets.

**Slop-Score aggregation** (weighted by severity):
```
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, sum(weights[s.severity] * s.confidence) / max(1, n))
is_slop = (slop_score ≥ 0.4) OR (any critical) OR (≥ 2 high severity)
```

---

## 7. Harms (Taxonomic)

| Harm Type | Mechanism | Evidence Source |
|-----------|-----------|-----------------|
| **Model Collapse** | Recursive training on AI output → loss of distribution tails, convergence to gibberish | Shumailov et al. 2024 [11]; Borji 2024 [12] |
| **Epistemic Pollution** | Polluted information ecology, LLMs cite UAINs as sources | NewsGuard Aug 2025 [13]; EDMO [14] |
| **Mis-/Disinformation** | State- or commercially-driven false-claim operations | US Treasury Dec 2024; Storm-1516; Freedom House 2025 [15] |
| **Trust Erosion** | "Liar's dividend"; difficulty separating real from fake | Koebler 404 Media [16] |
| **Workplace Productivity Loss** | "Workslop" offloads cognitive burden onto recipients; 40 % of employees affected; ~1h 56min rework per instance | Niederhoffer et al. HBR 2025 [17] |
| **Creator Squeeze** | Algorithms do not distinguish between original and fake bulk → originals get crowded out | Scientific American [10] |
| **Harm to Children** | ~40 % of YouTube Kids recommendations are slop (NYT Mar 2026); false information, dangerous behavior | NYT 2026 [18]; The 74 / Mother Jones |
| **Ad Fraud / Brand Safety** | 141 blue-chip brands unknowingly advertise on content farms | NewsGuard/AdWeek 2026 [19] |
| **Cognitive Load** | Constant "Is this real?" verification exhausts attention | Koebler "Your AI Use Is Breaking My Brain" 2026 [20] |
| **Environmental Cost** | Electricity and water consumption of generative models | Crawford "Eating the Future" [21] |
| **Democracy Risk** | Election interference, deepfake endorsements (Taylor Swift / Trump 2024) | Wikipedia [4]; Freedom on the Net 2025 |
| **Royalty Fraud** | AI tracks used to manipulate streaming royalties (Smith case 2024) | DOJ; Wikipedia [4] |

---

## 8. Related Concepts (Relationship Graph)

```
AISlop
├── isAnalogousTo
│   ├── Spam (email analogue; explicitly chosen by Willison)
│   ├── Kitsch (Munich 1860s; aesthetic analogue)
│   ├── GrubStreet (London 1700s; economic analogue)
│   ├── Churnalism (rewritten press releases)
│   └── Clickbait
├── isSubtypeOf
│   ├── SyntheticMedia
│   ├── DigitalPollution
│   └── EpistemicPollution
├── isCausedBy
│   ├── AttentionEconomy (creator bonus programs)
│   ├── ZeroMarginalCostGeneration
│   ├── AlgorithmicRecommendation
│   └── LowEntryBarrier (prompt-only workflow)
├── coOccursWith
│   ├── ModelCollapse                       (causally coupled)
│   ├── DeadInternetTheory
│   ├── ZombieInternet (Koebler)
│   └── Enshittification (Doctorow)
└── enables / specializes
    ├── Workslop (Niederhoffer et al.)
    ├── Slom (AI-Spam-Subset, Willison)
    ├── Brainrot (low-attention reward content)
    └── Necromemetics (Koebler; post-violence meme economy)
```

---

## 9. Key Empirical Figures (as of May 2026)

| Metric | Value | Source |
|--------|-------|--------|
| Share of AI content in Google search results | 19 % (Jan 2025); 7 % (prior year) | [22] |
| Share of AI footprint in new web articles | > 50 % (Graphite); 74 % (studies) | [22] |
| AI content farm sites (NewsGuard) | 3,006 (March 2026); >2x prior year | [19] |
| New content farm sites per month | 300–500 | [19] |
| YouTube recommendations slop for new users | 21–33 % (Kapwing 2025) | [23] |
| YouTube Kids slop share | ~40 % (NYT March 2026) | [18] |
| Workslop recipients | 40 % of employees | [17] |
| Workslop rework time per instance | ~1h 56min | [17] |
| AI content farm brands (advertising) | 141 blue-chip brands (2 months) | [19] |
| Languages with UAINs | 16 (Arabic to Turkish) | [24] |

---

## 10. Machine-Readable Block (YAML)

```yaml
ontology:
  id: ai-slop-ontology
  version: 1.0.0
  date: 2026-05-20
  rootClass: AISlop
  classes:
    AISlop:
      type: Phenomenon
      necessaryConditions:
        - primarySource: generativeAI
        - lacksHumanCuration: true
        - distributionMode: push  # unsolicited
      definitionSources:
        - merriamWebster2025
        - oxfordDictionary2024
        - willison2024
      subclasses: [ByModality, ByIntent, ByActor, ByPlatform]

  modalities:
    TextSlop:
      subtypes: [ArticleSlop, BookSlop, RecipeSlop, AcademicSlop, ProductReviewSlop, Workslop]
      detectionMethods: [repetitionRatio, buzzwordDetection, templatePhrases, punctuationAnomalies, informationDensity, perplexityDistribution]
    ImageSlop:
      subtypes: [EngagementBaitImage, DeceptiveProductImage, PoliticalSlopImage, ArtSlop]
      detectionMethods: [varianceAnalysis, symmetryAnomaly, anatomicalArtifacts, physicalImpossibility]
    VideoSlop:
      subtypes: [ChildrenContentSlop, BrainrotVideo, DeepfakeVideo, HistoricalSlopVideo]
    AudioSlop:
      subtypes: [AIMusic, VoiceCloneSlop, AINarrationSlop]
    CodeSlop:
      subtypes: [HallucinatedPackage, FabricatedAPI, VulnerableAISnippet]
      detectionMethods: [packageRegistryCheck, astFunctionVerification, secretsRegex]
    MultiModalSlop:
      detectionMethods: [crossModalConsistency, watermarkDetection]

  qualityDimensions:
    informationUtility:
      codes: [IU1_Density, IU2_Relevance]
    informationQuality:
      codes: [IQ1_Factuality, IQ2_Bias]
    styleQuality:
      codes: [SQ1_Repetition, SQ2_Templatedness, SQ3_Coherence, SQ4_Fluency, SQ5_Verbosity, SQ6_WordComplexity, SQ7_Tone]
    source: shaib2025

  systemicDimensions7Vs:
    - Volume
    - Velocity
    - Variety
    - Value
    - Verification
    - Visibility
    - Virality
    source: madsenPuyt2025

  detectionThresholds:
    repetition:
      high: 0.20
      critical: 0.30
    density:
      lowSlop: 0.40
      acceptable: 0.60
    punctuation:
      emDashPerSentence: 0.5
      ellipsisPerSentence: 0.3
      exclamationPerSentence: 0.2
    slopScore:
      autoPass: 0.2
      review: 0.4
      reject: 0.6
      severe: 0.8

  scoringFormula:
    weights: {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
    isSlopRule: "slop_score >= 0.4 OR any(severity==critical) OR count(severity>=high) >= 2"

  intents:
    - MonetizationSlop
    - PoliticalSlop
    - DisinformationSlop
    - AccidentalSlop
    - HumorousSlop
    - WorkplaceSlop

  actors:
    ContentFarm:
      knownCount: 3006
      countDate: 2026-03
      source: newsguard
    SoloMonetizer:
      regions: [India, Philippines, Kenya, Vietnam]
    StateActor:
      knownOperations: [Storm-1516, CenterForGeopoliticalExpertise]
    Corporation:
      examples: [Activision, Paramount, A24, Amazon]

  harms:
    - modelCollapse
    - epistemicPollution
    - misinformation
    - trustErosion
    - workplaceProductivityLoss
    - creatorSqueeze
    - harmToChildren
    - adFraud
    - cognitiveLoad
    - environmentalCost
    - democracyRisk
    - royaltyFraud

  relatedConcepts:
    analogous: [Spam, Kitsch, GrubStreet, Churnalism, Clickbait]
    superClass: [SyntheticMedia, DigitalPollution, EpistemicPollution]
    causes: [AttentionEconomy, ZeroMarginalCostGeneration, AlgorithmicRecommendation, LowEntryBarrier]
    cooccurs: [ModelCollapse, DeadInternetTheory, ZombieInternet, Enshittification]
    specializations: [Workslop, Slom, Brainrot, Necromemetics]

  decisionLogic:
    autoPass: "slop_score < 0.2 AND no critical issues"
    review: "0.2 <= slop_score < 0.4 OR 1 high issue"
    reject: "slop_score >= 0.4 OR any critical issue"
    block: "hardcoded secrets OR SQL injection OR child safety violation"
```

---

## 11. Application Hooks for Agents

```python
# Pseudo-Interface
def classify_content(content, modality) -> SlopAssessment:
    """Returns: {slop_score, is_slop, dimensions, harms, actor_hypothesis}"""

def route_by_harm(assessment) -> Action:
    """Block | Refine | Flag | Pass"""

def update_ontology(new_evidence) -> None:
    """Extend with new actor patterns, harm types, detection methods"""
```

**Recommended integration:** LangGraph node, MCP tool, AutoGen function (cf. skill `ai-slop-detection` v1.0).

---

## 12. Limitations and Open Questions

- **Subjectivity of binary slop judgments**: Cohen's κ -0.15 to 0.29 (Shaib et al. 2025) → binary classification is contested; dimensional assessment is more robust.
- **Reflexivity**: Detection heuristics become known → producers adapt ("humanized" variants).
- **False positives on human text**: Texts can appear as slop even without AI involvement (e.g., templated journalism, boilerplate content).
- **Context dependence**: Technical documentation may use repetition for clarity.
- **Linguistic bias**: Detection is most strongly trained on English; weaker in languages with less training data (Hindi, Vietnamese, Urdu) — precisely where a lot of slop originates.
- **Evolving models**: New model generations produce new slop patterns; the ontology requires regular updates.
- **Philosophical critique** (Puliafito; The Philosophical Salon): "Slop" describes mediocrity — but mediocrity is the baseline of all cultural production, not AI-specific [21].

---

## 13. References

### Lexicographic Primary Sources
[1] Merriam-Webster (2025). *Word of the Year 2025: "Slop"*. Definition: "digital content of low quality that is produced usually in quantity by means of artificial intelligence." PBS News, 15 Dec 2025. https://www.pbs.org/newshour/nation/merriam-websters-word-of-the-year-for-2025-is-ais-slop

[2] Oxford University Press (2024). *Word of the Year 2024 Shortlist: "Slop"*. https://corp.oup.com/word-of-the-year/#shortlist-2024 (+332 % usage growth).

### Etymological / Popularizing Sources
[3] Willison, S. (8 May 2024). *GPT-4o, a new version of LLM and more thoughts on slop*. Personal blog. https://simonw.substack.com/p/gpt-4o-a-new-version-of-llm-and-more — canonical spam analogy.

[4] Wikipedia contributors (as of May 2026). *AI slop*. https://en.wikipedia.org/wiki/AI_slop

[5] Wikipedia contributors (as of May 2026). *Model collapse*. https://en.wikipedia.org/wiki/Model_collapse

[6] @deepfates (early 2024). X / Twitter. "the term for unwanted AI generated content".

### Academic Core Papers
[7] Shaib, C., Chakrabarty, T., Garcia-Olano, D., & Wallace, B. C. (2025/2026). *Measuring AI "Slop" in Text*. arXiv:2509.19163v2. https://arxiv.org/abs/2509.19163 — operational taxonomy (3 themes, 11 codes), 213 news articles + 123 QA passages, annotation guide & data: https://github.com/cshaib/slop

[8] Madsen, D. Ø., & Puyt, R. W. (2 Oct 2025). *The 7Vs of AI Slop: A Typology of Generative Waste*. SSRN 5558018. https://ssrn.com/abstract=5558018 (DOI 10.2139/ssrn.5558018)

[9] MINT Lab (Johns Hopkins / ANU, 2025/26). *AI Slop: Definitions and Normative Status*. https://mintresearch.org/reports/ai-slop/

[10] *Why Slop Matters* (Feb 2026). arXiv:2601.06060. https://arxiv.org/html/2601.06060v1 — tasks for formal, sociological, ethical slop research.

### Model Collapse
[11] Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. *Nature* 631, 755–759. DOI 10.1038/s41586-024-07566-y. https://www.nature.com/articles/s41586-024-07566-y

[12] Borji, A. (Oct 2024). *A Note on Shumailov et al. (2024)*. arXiv:2410.12954. https://arxiv.org/abs/2410.12954 — KDE-based verification, statistical inevitability.

Further: Alemohammad et al. (2023) "Self-Consuming Generative Models Go MAD"; Gillman et al. (2024) "Self-Correction Mechanisms Stabilize Recursive Loops"; IBM (2026) *What is Model Collapse?* https://www.ibm.com/think/topics/model-collapse

### Investigative Journalism (Key Cases)
[13] NewsGuard AI False Claim Monitor (Aug 2025). https://www.newsguardtech.com/ai-monitor/august-2025-ai-false-claim-monitor/

[14] European Digital Media Observatory (EDMO). Reports on AI in the information ecology.

[15] Freedom House (2025). *Freedom on the Net 2025: AI and Influence Operations*. US Treasury sanctions Dec 2024 (Storm-1516).

[16] Koebler, J. (404 Media, 2023–2026). AI-slop reporting series:
   - *Facebook Is Being Overrun With Stolen, AI-Generated Images* (Dec 2023)
   - *Facebook Is the 'Zombie Internet'* (May 2024)
   - *Where Facebook's AI Slop Comes From* (Aug 2024). https://www.404media.co/where-facebooks-ai-slop-comes-from/
   - Tag overview: https://www.404media.co/tag/ai-slop/

[20] Koebler, J. (11 May 2026). *Your AI Use Is Breaking My Brain*. 404 Media.

### Workplace
[17] Niederhoffer, K., Rosen Kellerman, G., Lee, A., Liebscher, A., Rapuano, K., & Hancock, J. T. (22 Sep 2025). *AI-Generated "Workslop" Is Destroying Productivity*. Harvard Business Review. https://hbr.org/2025/09/ai-generated-workslop-is-destroying-productivity — n=1,150 US full-time employees; 40 % receive workslop; ~1h 56min rework per instance.

Niederhoffer et al. (Jan 2026). *Why People Create AI "Workslop"—and How to Stop It*. HBR. https://hbr.org/2026/01/why-people-create-ai-workslop-and-how-to-stop-it

### Children / Vulnerable Groups
[18] New York Times Investigation (March 2026). YouTube Kids ~40 % slop. (Reported in Wikipedia [4]; The 74; Mother Jones.)

### Industry Trackers
[19] NewsGuard × Pangram Labs (12 March 2026). *Real-time AI Content Farm Detection Datastream*. https://www.newsguardtech.com/press/newsguard-launches-real-time-ai-content-farm-detection-datastream-to-counter-onslaught-of-ai-slop-in-news/ — 3,006 content farms identified; 141 blue-chip brands unknowingly advertising.

[24] NewsGuard *AI Tracking Center*. https://www.newsguardtech.com/special-reports/ai-tracking-center/ — UAINs in 16 languages.

### Platform and Sector Reports
[22] Graphite Research / Entrepreneur Loop (2025/26). AI footprint > 50 % in new web articles. https://entrepreneurloop.com/what-is-ai-slop-growing-problem-explained/

[23] Kapwing × The Guardian (2025). YouTube recommendations 21–33 % AI/brainrot.

### Conceptual / Philosophical Critique
[21] Crawford, K. *Eating the Future* (cited in The Philosophical Salon); Puliafito, A. *Slow News*. *The Idea of "AI Slop" Is Slop*, The Philosophical Salon, Dec 2025. https://thephilosophicalsalon.com/the-idea-of-ai-slop-is-slop/

### Conceptual-Historical Context
Scientific American (Nov 2025). *AI Slop—How Every Media Revolution Breeds Rubbish and Art*. https://www.scientificamerican.com/article/ai-slop-how-every-media-revolution-breeds-rubbish-and-art/ — Grub Street analogy.

### Detection Research
- Mitchell, E. et al. (2023). *DetectGPT: Zero-Shot Machine-Generated Text Detection*. ICML.
- Hans, A. et al. (2024). *Spotting LLMs With Binoculars*. ICML 2024 (AUROC ~0.95).
- Russell et al. (2025). *Indicators of AI-written text*. (Referenced in Shaib et al. 2025.)
- Chakrabarty et al. (2024, 2025a, 2025b). Editing taxonomies for AI writing.

### Source Hub
- Simon Willison's `slop` tag overview: https://simonwillison.net/tags/slop/ — ongoing curation stream since 2024.

---

## 14. Versioning and Update Notes

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-05-20 | Initial release; consolidates Shaib et al. 2025, Madsen & Puyt 2025, Shumailov et al. 2024, 22 detection techniques, 12 harm classes, 16 related concepts. |

**Recommended update cadence:** quarterly (new model generations → new slop patterns); ad hoc on major NewsGuard updates or new academic taxonomies.

**Contributions welcome:** extensions on audio slop (under-researched), non-Western platforms (TikTok/Douyin, KakaoTalk, WhatsApp), and systematic cross-modal detection.
