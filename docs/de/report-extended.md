> Research by Goswin | zai/glm-5.1 | 2026-05-20 (Round 2 — Extended)
> Additional sources: 7 new pages fetched, 4 new searches

# AI Slop — Deep Research Report (Extended)

## Erweiterungen seit Round 1

### 8. Slopsquatting: Die akute Bedrohung (Neu)

**Definition:** Slopsquatting (auch "hallucination squatting") ist eine Supply-Chain-Attacke bei der Angreifer Paketnamen registrieren, die LLMs fälschlicherweise empfehlen. Der Begriff wurde von Seth Larson geprägt, Andrew Nesbitt amplifiziert.

**Harte Zahlen (USENIX Security 2025, "We Have a Package for You!"):**
- 16 Modelle getestet, 576.000 Code-Samples
- **19.7% aller empfohlenen Pakete existieren nicht**
- Open-Source Modelle: 21.7% Halluzinationsrate
- GPT-4 Turbo: 3.59% (bestes Ergebnis)
- CodeLlama: >33%
- **205.000+ einzigartige halluzinierte Paketnamen** beobachtet
- 43% der halluzinierten Pakete wurden in JEDEM Testlauf wiederholt
- 8.7% der halluzinierten Python-Pakete existieren als echte npm-Pakete (Cross-Ecosystem)

**"Importing Phantoms" Studie (2025):**
- Halluzinationsraten: 0.22% bis 46.15% je nach Modell/Sprache
- JavaScript: 14.73% | Python: 23.14% | Rust: 24.74%
- Größere Modelle halluzinieren generell weniger, aber Code-spezifische Modelle können SCHLIMMER sein

**Reale Vorfälle:**
1. **huggingface-cli** (Lasso Security, 2024): Lanyado lud ein leeres Paket hoch → 30.000+ Downloads in 3 Monaten. Alibaba hatte den halluzinierten Befehl in ihren README kopiert.
2. **react-codeshift** (Aikido, Jan 2026): Halluzinierter Name (Mashup aus `jscodeshift` + `react-codemod`) verbreitete sich durch 47 LLM-generierte Agent Skills → 237 Repositories. Niemand pflanzte es absichtlich — rein organische Verbreitung durch AI-Infrastruktur.
3. **unused-imports**: Echte Malware, 233 Downloads/Woche im Feb 2026. Kam durch AI-Empfehlung in Umlauf. npm hat es mittlerweile unter Security Hold.

**Angriffskette:**
1. LLM halluziniert Paketnamen (z.B. `react-auth-helper`)
2. Angreifer registriert den Namen auf npm/PyPI (kostenlos, keine Hacking-Skills nötig)
3. Post-install-Script stiehlt Credentials (API Keys, Cloud Tokens, npm Auth)
4. Fortgeschritten: URL-basierte Dependencies holen Payload von externem Server → Package sieht clean aus

**Verteidigung:**
- Jedes AI-empfohlene Paket manuell gegen Registry verifizieren
- Autonomous Package Installation als privilegierte Operation behandeln
- SCA-Scanner für full dependency tree (nicht nur package.json)
- GPT-4 Turbo und DeepSeek können ~75% ihrer eigenen Halluzinationen erkennen
- Temperatur senken, Verbose Control → weniger Halluzinationen

---

### 9. Engagement Farming: Die Politische Ökonomie des Slop (Neu)

**Mark Carrigan (Jan 2026):** "You can't understand AI slop without understanding engagement farming"

> "Rather than 'AI slop' being some exogenous factor swamping previously functional platforms, we need to see it as an outcome of existing practices of engagement farming. The political economy of social platforms has over many years inculcated a strategic orientation towards engagement."

**Kern-Argument:** AI Slop ist nicht die Ursache — es ist das Symptom. Die Ursache ist das broken Incentive-System sozialer Plattformen:
- Content = Engagement = Revenue (Meta, Google, Pinterest)
- Qualität ist irrelevant — nur Quantity + Engagement zählen
- AI senkt die Produktionskosten gegen Null → Slop ist die logische Konsequenz

**Jesse Cunningham (Futurism-Exposé):**
- "SEO Specialist" der AI-Slop auf Facebook/PPinterest betreibt
- Targeting: "50-plus female" → "Aunt Carol doesn't know how to use Facebook"
- Prozess: Bestehende virale Pins identifizieren → AI repliziert sie → 80 AI-Pins pro Tag
- Fake-Blog "Bonsai Mary" mit AI-Autorin "Mary Smith" (echte Vorbesitzerin: Mary C. Miller, echte Bonsai-Künstlerin)
- 8.6 Millionen Monthly Views auf Pinterest
- Impact: "It's put a ton of people out of business" (Rachel Farnsworth, Food Bloggerin)

**Ökonomische Dynamik (dig.watch Analyse):**
- Produktionskosten → ~0€ pro Content-Item
- ROI: Selbst minimales Engagement generiert positive Returns (Ads, Affiliate, Monetization)
- SEO-Automatisierung: Tausende keyword-optimierte Artikel in Stunden
- Video-Slop: Synthetic Voice-Overs + AI-Visuals für Trending Topics in Minuten
- YouTube-Doppelmoral: Echte Creator werden für Community Guidelines verfolgt, AI-Slop läuft unter dem Radar

---

### 10. Knowledge Collapse: Drei-Stadien-Modell (Neu)

**Keisha et al. (NeurIPS 2025 Workshop):** "Knowledge Collapse in LLMs"

Drei-Stadien-Phänomen bei rekursivem Training auf synthetischen Daten:

| Stadium | Name | Was passiert | Gefahr |
|---------|------|-------------|--------|
| A | Knowledge Preservation | Fakten korrekt, Instruktion-Following intakt | Niedrig |
| B | Knowledge Collapse | **"Confidently Wrong"** — Fakten falsch, aber Format korrekt | KRITISCH |
| C | Instruction-Following Collapse | Kompletter Zusammenbruch, Random Baseline (~28%) | Hoch, aber erkennbar |

**Stadium B ist das gefährlichste:** Oberflächliche Qualitätsmetriken (Fluency, Format) zeigen keine Probleme, aber faktische Richtigkeit degradiert. "The valley of dangerous competence."

**Abhängigkeit von Prompt-Format:**
- Short-Answer Prompts: Stabil bis Generation 8
- Few-Shot Prompts: Kollabieren rapide bei Generation 6
- Zero-Shot Prompts: Langsamerer Abbau

**Abhängigkeit von synthetischem Anteil:**
- 25% synthetisch: Langes Stadium A, langsamer Übergang
- 50% synthetisch: Schnellerer Übergang bei mittlerer Generation
- 100% synthetisch: Schneller Übergang, frühe Generationen

**Mitigation:** Domain-spezifisches synthetisches Training → **15× langsamere Accuracy-Degradation** verglichen mit generischem Training.

---

### 11. Regulation & Governance (Neu)

**EU Digital Services Act (DSA):**
- Richtet sich an "Very Large Online Platforms" (VLOPs)
- Kein spezifischer AI-Slop-Fokus, aber:
  - Transparenz-Pflichten für Empfehlungsalgorithmen
  - Systemic-Risk-Assessment bei Beeinträchtigung des öffentlichen Diskurses
  - Meta wehrt sich ("overreaching", "stifling innovation")

**Labeling/Watermarking:**
- OpenAI Sora: Faint Watermark (kaum sichtbar für ungeschulte Nutzer)
- C2PA Provenance Standard: Wird diskutiert aber nicht flächendeckend implementiert
- Problem: Labeling allein reicht nicht, wenn Algorithmen weiterhin Engagement priorisieren

**Der strukturelle Konflikt:**
- Plattformen verdienen an Engagement → Slop generiert Engagement
- Moderation kann mit Produktionsgeschwindigkeit nicht mithalten
- AI-Content wird schneller billiger → Enforcement-Systeme bremsen

---

### 12. Vorhersage von Slop-Genres (Neu)

**Hypogenic AI Research Project:** "Predicting Slop Before It Happens"

Untersucht ob man AI-Slop-Genre vorhersagen kann BEVOR sie ubiquitär werden.

**Gatherierte Ressourcen:**
- 10 Paper (inkl. Why Slop Matters, Measuring AI Slop, Model Collapse, Dead Internet Theory, Generative Propaganda)
- 3 Datensets: MAGE (437K AI-Text-Detection), HC3 (24K Human-vs-ChatGPT), Steam Games (124K — als Proxy für Genre-Emergence)
- 1 Code-Repo: cshaib/slop (Annotation Framework, Data "coming soon")

**Lücke:** Kein existierendes Datenset für Slop-Genre-Prediction. Kein Cross-Modal-Slop-Benchmark.

**Bewertungsmethoden:**
- Random Baseline vs. Historical Frequency Extrapolation
- Expert Surveys vs. LLM-based Genre Forecasting
- Metrics: Precision/Recall, Temporal Accuracy, Taxonomy Coverage

---

### 13. Stefans Vorarbeit: Tieferer Einblick

#### quality-agent/docs/refinements/ai.slop.md (200+ Zeilen)
- 23 Techniken in Referenz-Tabelle mit Quellen
- Spezieller Code-Slop-Abschnitt mit Beispielen:
  - Invented Packages (`super_fast_json_parser`, `ts-migrate-parser`)
  - Fabricated Functions (`archive_old_records_async()`)
  - Incorrect Logic (invertierte `has_close_elements` Implementation)
  - Security Flaws (hardcoded API Keys)
- Cross-Modal: Text, Code, Images, Video
- Verlinkt auf 15+ externe Quellen

#### local-ai-setup/skills/ai-slop-detection/ (16 Dateien)
- **SKILL.md** (747 Zeilen) — zu groß laut Review, aber comprehensive
- **detectors.py** — Unified Multi-Modal Entry Point
- **text_detector.py** — Text-spezifisch
- **code_detector.py** — Code-spezifisch (NEU: separater Detektor!)
- **image_detector.py** — Bildartefakte
- **scoring.py** — Score-Engine
- **content_quality.py** — Qualitätsmetriken
- **analyzer_enhanced.py** — Erweiterte Analyse
- **ole_lehman_patterns.py** — Pattern-Bibliothek
- **performance_profile.py** — Performance-Optimierung
- **real_world_validation.py** — Validierungstest
- **test_enhanced.py** — Test-Suite
- **examples/** — Beispieldaten
- **reference.md** — Referenzdokument

---

## Quellen (Round 2)

12. [Aikido Security: Slopsquatting](https://www.aikido.dev/blog/slopsquatting-ai-package-hallucination-attacks) — 30K+ Downloads eines leeren halluzinierten Pakets, react-codeshift Incident
13. [Mark Carrigan: Engagement Farming](https://markcarrigan.net/2026/01/14/you-cant-understand-ai-slop-without-understanding-engagement-farming/) — Politische Ökonomie des Slop
14. [Futurism: Slop Farmer Exposé](https://futurism.com/slop-farmer-ai-social-media) — Jesse Cunningham, Bonsai Mary, 8.6M Pinterest Views
15. [dig.watch: AI Slop 2026](https://dig.watch/updates/ai-slop-content-social-media) — Economics, Regulation, EU DSA
16. [Keisha et al. (NeurIPS 2025): Knowledge Collapse](https://arxiv.org/abs/2509.04796) — 3-Stage Model, "Confidently Wrong", Domain-Specific Training
17. [Nature: Model Collapse](https://www.nature.com/articles/s41586-024-07566-y) — Shumailov et al., Original Paper
18. [Mend.io: Slopsquatting](https://www.mend.io/blog/the-hallucinated-package-attack-slopsquatting/) — 19.7% Halluzinationsrate, USENIX Study
19. [Hypogenic AI: Predict Slop](https://github.com/Hypogenic-AI/predict-slop-ai-claude/blob/main/resources.md) — Genre Prediction Research, Datasets, Papers
20. [CSA: Slopsquatting Research Note](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/) — Cloud Security Alliance
