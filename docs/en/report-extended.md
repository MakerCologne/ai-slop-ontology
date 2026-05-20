> Research by Goswin | zai/glm-5.1 | 2026-05-20 (Round 2 — Extended)
> Additional sources: 7 new pages fetched, 4 new searches

# AI Slop — Deep Research Report (Extended)

## Extensions since Round 1

### 8. Slopsquatting: The acute threat (New)

**Definition:** Slopsquatting (also "hallucination squatting") is a supply-chain attack in which attackers register package names that LLMs erroneously recommend. The term was coined by Seth Larson, amplified by Andrew Nesbitt.

**Hard numbers (USENIX Security 2025, "We Have a Package for You!"):**
- 16 models tested, 576,000 code samples
- **19.7% of all recommended packages do not exist**
- Open-source models: 21.7% hallucination rate
- GPT-4 Turbo: 3.59% (best result)
- CodeLlama: >33%
- **205,000+ unique hallucinated package names** observed
- 43% of hallucinated packages were repeated in EVERY test run
- 8.7% of hallucinated Python packages exist as real npm packages (cross-ecosystem)

**"Importing Phantoms" study (2025):**
- Hallucination rates: 0.22% to 46.15% depending on model/language
- JavaScript: 14.73% | Python: 23.14% | Rust: 24.74%
- Larger models generally hallucinate less, but code-specific models can be WORSE

**Real incidents:**
1. **huggingface-cli** (Lasso Security, 2024): Lanyado uploaded an empty package → 30,000+ downloads in 3 months. Alibaba had copied the hallucinated command into their README.
2. **react-codeshift** (Aikido, Jan 2026): Hallucinated name (mashup of `jscodeshift` + `react-codemod`) spread through 47 LLM-generated agent skills → 237 repositories. Nobody planted it intentionally — purely organic spread through AI infrastructure.
3. **unused-imports**: Real malware, 233 downloads/week in Feb 2026. Entered circulation through AI recommendation. npm has since put it under security hold.

**Attack chain:**
1. LLM hallucinates package name (e.g., `react-auth-helper`)
2. Attacker registers the name on npm/PyPI (free, no hacking skills required)
3. Post-install script steals credentials (API keys, cloud tokens, npm auth)
4. Advanced: URL-based dependencies fetch payload from external server → package appears clean

**Defense:**
- Manually verify every AI-recommended package against the registry
- Treat autonomous package installation as a privileged operation
- SCA scanner for full dependency tree (not just package.json)
- GPT-4 Turbo and DeepSeek can detect ~75% of their own hallucinations
- Lower temperature, verbose control → fewer hallucinations

---

### 9. Engagement Farming: The political economy of slop (New)

**Mark Carrigan (Jan 2026):** "You can't understand AI slop without understanding engagement farming"

> "Rather than 'AI slop' being some exogenous factor swamping previously functional platforms, we need to see it as an outcome of existing practices of engagement farming. The political economy of social platforms has over many years inculcated a strategic orientation towards engagement."

**Core argument:** AI Slop is not the cause — it is the symptom. The cause is the broken incentive system of social platforms:
- Content = Engagement = Revenue (Meta, Google, Pinterest)
- Quality is irrelevant — only quantity + engagement count
- AI drives production costs to zero → slop is the logical consequence

**Jesse Cunningham (Futurism exposé):**
- "SEO Specialist" who runs AI slop on Facebook/Pinterest
- Targeting: "50-plus female" → "Aunt Carol doesn't know how to use Facebook"
- Process: Identify existing viral pins → AI replicates them → 80 AI pins per day
- Fake blog "Bonsai Mary" with AI author "Mary Smith" (real prior owner: Mary C. Miller, real bonsai artist)
- 8.6 million monthly views on Pinterest
- Impact: "It's put a ton of people out of business" (Rachel Farnsworth, food blogger)

**Economic dynamics (dig.watch analysis):**
- Production costs → ~€0 per content item
- ROI: Even minimal engagement generates positive returns (ads, affiliate, monetization)
- SEO automation: Thousands of keyword-optimized articles in hours
- Video slop: Synthetic voice-overs + AI visuals for trending topics in minutes
- YouTube double standard: Real creators are pursued for community guidelines, AI slop runs under the radar

---

### 10. Knowledge Collapse: Three-stage model (New)

**Keisha et al. (NeurIPS 2025 Workshop):** "Knowledge Collapse in LLMs"

Three-stage phenomenon in recursive training on synthetic data:

| Stage | Name | What happens | Danger |
|---------|------|-------------|--------|
| A | Knowledge Preservation | Facts correct, instruction-following intact | Low |
| B | Knowledge Collapse | **"Confidently Wrong"** — facts wrong, but format correct | CRITICAL |
| C | Instruction-Following Collapse | Complete breakdown, random baseline (~28%) | High, but recognizable |

**Stage B is the most dangerous:** Superficial quality metrics (fluency, format) show no problems, but factual correctness degrades. "The valley of dangerous competence."

**Dependence on prompt format:**
- Short-answer prompts: Stable up to generation 8
- Few-shot prompts: Collapse rapidly at generation 6
- Zero-shot prompts: Slower decline

**Dependence on synthetic share:**
- 25% synthetic: Long stage A, slow transition
- 50% synthetic: Faster transition at middle generation
- 100% synthetic: Fast transition, early generations

**Mitigation:** Domain-specific synthetic training → **15× slower accuracy degradation** compared to generic training.

---

### 11. Regulation & Governance (New)

**EU Digital Services Act (DSA):**
- Aimed at "Very Large Online Platforms" (VLOPs)
- No specific AI slop focus, but:
  - Transparency obligations for recommendation algorithms
  - Systemic risk assessment for impairment of public discourse
  - Meta resists ("overreaching", "stifling innovation")

**Labeling/Watermarking:**
- OpenAI Sora: Faint watermark (barely visible to untrained users)
- C2PA Provenance Standard: Being discussed but not widely implemented
- Problem: Labeling alone is not enough if algorithms continue to prioritize engagement

**The structural conflict:**
- Platforms earn from engagement → slop generates engagement
- Moderation cannot keep up with production speed
- AI content becomes cheaper faster → enforcement systems lag behind

---

### 12. Predicting Slop Genres (New)

**Hypogenic AI Research Project:** "Predicting Slop Before It Happens"

Investigates whether AI slop genres can be predicted BEFORE they become ubiquitous.

**Gathered resources:**
- 10 papers (incl. Why Slop Matters, Measuring AI Slop, Model Collapse, Dead Internet Theory, Generative Propaganda)
- 3 datasets: MAGE (437K AI text detection), HC3 (24K Human-vs-ChatGPT), Steam Games (124K — as proxy for genre emergence)
- 1 code repo: cshaib/slop (annotation framework, data "coming soon")

**Gap:** No existing dataset for slop genre prediction. No cross-modal slop benchmark.

**Evaluation methods:**
- Random Baseline vs. Historical Frequency Extrapolation
- Expert Surveys vs. LLM-based Genre Forecasting
- Metrics: Precision/Recall, Temporal Accuracy, Taxonomy Coverage

---

### 13. Stefan's preliminary work: Deeper insight

#### quality-agent/docs/refinements/ai.slop.md (200+ lines)
- 23 techniques in reference table with sources
- Special code slop section with examples:
  - Invented Packages (`super_fast_json_parser`, `ts-migrate-parser`)
  - Fabricated Functions (`archive_old_records_async()`)
  - Incorrect Logic (inverted `has_close_elements` implementation)
  - Security Flaws (hardcoded API keys)
- Cross-Modal: Text, Code, Images, Video
- Links to 15+ external sources

#### local-ai-setup/skills/ai-slop-detection/ (16 files)
- **SKILL.md** (747 lines) — too large per review, but comprehensive
- **detectors.py** — Unified Multi-Modal Entry Point
- **text_detector.py** — Text-specific
- **code_detector.py** — Code-specific (NEW: separate detector!)
- **image_detector.py** — Image artifacts
- **scoring.py** — Score engine
- **content_quality.py** — Quality metrics
- **analyzer_enhanced.py** — Extended analysis
- **ole_lehman_patterns.py** — Pattern library
- **performance_profile.py** — Performance optimization
- **real_world_validation.py** — Validation test
- **test_enhanced.py** — Test suite
- **examples/** — Sample data
- **reference.md** — Reference document

---

## Sources (Round 2)

12. [Aikido Security: Slopsquatting](https://www.aikido.dev/blog/slopsquatting-ai-package-hallucination-attacks) — 30K+ downloads of an empty hallucinated package, react-codeshift incident
13. [Mark Carrigan: Engagement Farming](https://markcarrigan.net/2026/01/14/you-cant-understand-ai-slop-without-understanding-engagement-farming/) — Political economy of slop
14. [Futurism: Slop Farmer Exposé](https://futurism.com/slop-farmer-ai-social-media) — Jesse Cunningham, Bonsai Mary, 8.6M Pinterest views
15. [dig.watch: AI Slop 2026](https://dig.watch/updates/ai-slop-content-social-media) — Economics, Regulation, EU DSA
16. [Keisha et al. (NeurIPS 2025): Knowledge Collapse](https://arxiv.org/abs/2509.04796) — 3-Stage Model, "Confidently Wrong", Domain-Specific Training
17. [Nature: Model Collapse](https://www.nature.com/articles/s41586-024-07566-y) — Shumailov et al., Original Paper
18. [Mend.io: Slopsquatting](https://www.mend.io/blog/the-hallucinated-package-attack-slopsquatting/) — 19.7% hallucination rate, USENIX Study
19. [Hypogenic AI: Predict Slop](https://github.com/Hypogenic-AI/predict-slop-ai-claude/blob/main/resources.md) — Genre Prediction Research, Datasets, Papers
20. [CSA: Slopsquatting Research Note](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/) — Cloud Security Alliance
