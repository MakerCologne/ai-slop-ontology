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
**Tier 1** (generic filler): delve, realm, tapestry, navigating the landscape, dynamic
**Tier 2** (action inflation): unleash, unlock, harness, leverage
**Tier 3** (corporate jargon): paradigm, synergy, robust
**Tier 4** (context-dependent): deep dive, future-proof, quietly

≥3 hits across tiers → strong signal (confidence ≥ 0.80)

### Template Phrases
"it's important to note", "in conclusion", "to sum up", "furthermore", "moreover", "as previously mentioned", "it is worth noting", "needless to say", "in today's [X]", "let's dive in", "we will explore"

`table of contents` wurde 2026-08-28 gestrichen (#88): es traf 0 von 330 Korpus-Texten und kommt in legitimer Fachdokumentation genauso vor wie in Content-Farmen. Ein Muster, das in beiden Klassen gleich häufig ist, trägt keine Information — und diese Liste steuert den LLM-Pfad des Skills, hätte den False Positive also weiter reproduziert.

≥2 template phrases → signal (confidence ≥ 0.75)

**Batch F (2026-08-25)** — zwei neue Kategorien aus den FN-Serien des
Benchmark-Korpus (eval/corpus.jsonl, slop-0101/slop-0504), Beleg-Disziplin
≥3 slop-Texte / 0 clean-Texte (tests/test_fn_series_signals.py):
- `marketing_cta` (conf 0.75): SaaS-CTA- und Social-Proof-Formeln —
  "start your free trial today", "book a demo", "trusted by startups and
  enterprises alike", "99.9% uptime", "ready to get started", ...
- `punchy_insight` (conf 0.75): Insight-Porn-/Throat-Clearing-Formeln —
  "the implications are significant", "here's why that matters",
  "the real challenge is not what you think", "mistakes were made along
  the way", "the window is closing", ...
- `report_hedging` (conf 0.75): Business-/Berichts-Hedging und Fake-
  Authority (Serie slop-0202) — "it is important to note",
  "industry reports suggest", "a pivotal moment", "studies show",
  "here's what nobody tells you", ...
- `wiki_promo` (conf 0.75): Wiki-/Promo-Boilerplate (Serien slop-0303/
  0403/0606) — "garnered recognition", "setting the stage for",
  "curated compilation", "plays a crucial role", "boasts a vibrant",
  "commitment to excellence", ...
- `assistant_signoff` (conf 0.75): Assistant-Sign-off- und Weasel-
  Boilerplate (Serien slop-0303/0606) — "let me know if you'd like more
  detail", "of course! here's the summary", "based on available
  information", "up to my last training update", "some critics argue", ...

**Issue #110 (2026-09-12)** — `conversational_fillers` (conf 0.70):
Konversationelle Füll-Floskeln (Hassid-Liste 4–8) — gesprochene
Gesprächs-Muster, die in Schrifttexte migrieren. Quick-Update-Floskeln
("to provide a quick update", "just a quick update", "quick update on",
...) plus zwei bewachte Spezialfälle:
- `most people` — nur satzinitial UND ohne First-Person-Quelle gezählt
  ("Most people I interviewed…" feuert nicht; Pseudo-Empirie ist das
  Signal, nicht die Quantifikation).
- `hope this helps`-Familie — positionsbasierter Guard: Treffer in den
  letzten 100 Zeichen vor einer Grußformel (echte Support-Mail) zählen
  nicht, in jeder Kategorie.
"here's the thing" bleibt in `listicle_tells` (ein Term, eine Kategorie).
Pre-2022-Cap bewusst nicht angewandt (Floskeln sind vormenschlich;
Signal ist Genre-Migration, nicht Rezenz).
**#115 (2026-09-11, ZeroSlop-Adaption)** — zwei Prosa-Kategorien mit
keep_when-Guards (fp_guards.mask_performative_stakes, wirken VOR dem
Matching):
- `performative_voice` (conf 0.55): Persoenlichkeits-Theater — "here's
  the thing nobody tells you", "nobody tells you", "i'm going to be
  honest with you", "let me be brutally honest", "i don't say this
  lightly", "unpopular opinion, but", "call me old-fashioned, but".
  Hard-Negative-Guard: kein Fire bei First-Person-Erfahrungs-Anker im
  +-120-Zeichen-Fenster ("when I ...", "in my experience",
  "I lost/spent/learned/tried/failed") — gelebte statt performte
  Stimme.
- `manufactured_stakes` (conf 0.6): Dringlichkeit ohne Sache — "in
  today's fast-paced", "the stakes have never been higher", "now more
  than ever", "at a critical juncture", "time is running out", "don't
  get left behind", "before it's too late". Hard-Negative-Guard: kein
  Fire bei konkretem Termin/Fakt im 120-Zeichen-Folgfenster ("deadline
  15 October", "by Friday", Ziffern mit Einheit) — echte statt
  dramatisierte Dringlichkeit.

  Beide Kategorien detect-only per Kumulativregel (≥ 2 Treffer).
  Fact-Gate-Invariante (ontology.json → deslopInvariants): "Deslop
  löscht keine Facts" — der Score trifft die Inszenierung, nie den
  Fakt dahinter.

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
- **UI Title Case strings (detect-only)**: `UiSlopStartCase` — ≥3 consecutive Title Case words in UI string literals (labels/buttons/i18n); see `ui-slop-signals.md`

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

## Academic-Register Signals (detect-only, #114)

Invertierbar: feuern nur ohne akademische Absicherung im Kontext.

### EpistemicMismatch
Starkes epistemisches Verb (`demonstrate`, `prove`, `confirm`, `conclusively show`) **und** Hedge (`may`, `might`, `suggest`, `appears`) im selben Satz. Inversion: Hedge ohne starkes Verb; starkes Verb mit n=/Quantifizierung.

### UnquantifiedScopeClaim
Vollständigkeitenspruch (`comprehensive analysis/survey/study`, `exhaustive …`, `all relevant studies`) ohne Zahl (n=, Anzahl, Zeitraum, %) im selben Satz. Inversion: „comprehensive survey of 214 papers (2018–2025)“.

### VagueAttribution
`the literature suggests/shows`, `studies show`, `research indicates`, `it is well established that` ohne Zitatmarker (`[12]`, `(Smith et al., 2020)`, `\cite{}`) im ±120-Zeichen-Fenster. Inversion: mit Zitat.

Quelle: cbsteh/anti-ai-writing, arXiv:2412.11385 (COLING 2025). Texte < 40 Wörter werden geprüfungsfrei ignoriert.

## Rhetorical Patterns (detect-only)

Sentence- and paragraph-level *shapes* that mark AI-assisted prose, independent
of any single buzzword. Each match is a **named pattern with a quoted line of
evidence** for a human to check — it is deliberately **not** folded into the
numeric slop score (a named pattern is evidence; a score is a guess). Every
pattern carries a `keep_when` note so genuine human voice is not flagged.

Adapted from the "No AI slop" editing skill by Peter Yang
([petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop), MIT).

| Pattern | Smells like | Keep when |
|---------|-------------|-----------|
| Binary contrast | "It's not X. It's Y." | Genuine correction of a specific misconception |
| Colon reveal | "The best part: it learns." | Colon introduces a list, label, quote, or code |
| Superficial analysis | "…, highlighting the team's commitment" | Clause states a concrete consequence |
| Negative listing / fragmentation | "Not a X. Not a Y. A Z." / "That's it." | Sparing emphasis that fits the writer's rhythm |
| Fake-strong verb | "serves as a centralized hub" | Names a literal role, no plainer verb fits |
| Synonym cycling | the agent → the assistant → the tool | The words refer to different things |
| Hollow kicker / recap | "In conclusion, …" / mic-drop aphorism | A genuine call to action or next step |
| Formatting slop | emoji headings, mid-sentence bold, em-dash clusters | Platform's native style |
| Robotic rhythm | 3+ stacked short sentences | One deliberate burst for emphasis |
| Decorative separator triad | Slogan-shaped "X \| Y \| Z" or #X #Y #Z of short items | Real breadcrumb, shortcut chain, or table row |
| Opener announcement (17.09., #230) | Praise-/Ankuendigungs-Frames am Satzanfang ('Spannender Punkt.', 'Ein weiterer Aspekt ist ...', text-initiales 'Ich denke' ohne Begrundung) | Echte Haltungsdifferenzierung mit Begrundung; Ritual-Formeln |
| Engagement comment default (17.09., #231) | LinkedIn-Kommentar-Default-Sequenz: Lob-Auftakt -> Paraphrase-Marker ('Sie schreiben', 'In Ihrem Beitrag', 'you describe') -> angekuendigte Ergaenzung -> abschliessende Engagement-Frage; feuert erst ab 3 von 4 Elementen IN REIHENFOLGE in EINEM Text | Echte FAQ-Konversation, Interview oder Moderation, in der Frage und Bezug genuine Information tragen |
| Forced triad (erweitert 15.09.) | Auch Nomen-/Verb-Triaden ("verstehen, gestalten, transformieren"), Staccato-Dreier ("Menschen. Prozesse. Technologie."), dt. "X, Y und Z" (alle drei gleiche Flexionsklasse) | Drei wirklich verschiedene, einzeln tragende Punkte |

Run: `python3 scripts/rhetorical_patterns.py "TEXT"` (or read
`result.rhetorical_patterns` from the classifier's JSON output). The nine
patterns are mirrored as data in `ontology.json` under
`signals.text.rhetoricalPatterns`.

### Circular Explanation (detect-only, #122)

A tautological definition inside a single sentence: the predicate repeats the
subject's stems instead of adding information ("The auth module validates
authentic user authentication."). Fires only with a definitional verb
(is/means/validates/ensures/…), a shared content stem (prefix ≥ 4 chars) on
both sides of the verb, and a predicate that adds ≤ 3 new stems; short
sentences are skipped. Fixed confidence 0.45, never part of the numeric
score. `keep_when`: technical reference prose ("the auth module handles
authentication tokens" — no definitional verb) and genuine definitions
(predicate introduces > 3 new stems) do not fire. Source: PRISM research
context (bhanvinayer/PRISM), adapted as a prose signal; implementation in
`scripts/circular_explanations.py`.

## Statistical/ML Methods

1. **DetectGPT** (Mitchell et al. 2023): Curvature-based probability discrimination
2. **Binoculars** (Hans et al. 2024): Zero-shot LLM detection (AUROC ~0.95)
3. **NewsGuard × Pangram Labs**: Domain-scale detection (3,000+ farms tracked)
4. **Perplexity distribution**: Unusually uniform/low perplexity = AI-generated

### Human Detection Empirie (Menschen ≈ Chance-Level)

ML-Detektoren sind das eine — die andere Hälfte der Empirie: **Menschliche Erkennungsleistung ist schlecht.** Das ist das stärkste Argument gegen „ich erkenne KI-Text schon selbst“ und für Tool-Einsatz + Checklisten-Ansatz.

| Studie | Befund |
|--------|--------|
| Cheng 2025 | Menschliche Unterscheidung LLM- vs. Menschentext **nicht besser als Zufallsniveau** |
| Fiedler 2025 (deutsche Abschlussarbeiten) | Erkennungsrate **57 % für KI-Texte**, 64 % für menschliche Texte |
| Russell 2025 (Preprint) | Schwere LLM-Nutzer: ~**90 % korrekt** — aber bei 10 markierten Seiten ≈ 1 False Positive; Wenig-Nutzer kaum über Zufall |

**Sprach-Konvergenz verschärft das Problem:** Menschliche Sprache wird von LLMs beeinflusst und ähnelt KI-Output zunehmend — nachgewiesen für gesprochene Inhalte/Podcasts (Yakura 2024) sowie weiterführend für Lexik und Semantik/Word-Choice (Geng 2025, Galpin 2025). Grundannahme „Menschentext sieht anders aus“ erodiert über Zeit; lebenslange Signaturen (eigener Stil, Belege, Provenance) werden relativ wichtiger als Oberflächen-Signale.

**Implikationen für dieses Skill:**
- Selbst-Diagnose („das liest sich menschlich“) ist kein valides Kriterium — Signal-Katalog + Scorer schlagen Intuition.
- Einzelne Signale sind hinweisend, nicht beweisend; Score-Aggregation + Schwellenentscheidung beachten.
- Russell-2025-Caveat gilt auch für Tools: ~90 % Genauigkeit ⇒ ~10 % False-Positive-Rate einkalkulieren, kritische Aktionen nie auf einen einzelnen Score stützen.

Quelle (Zugriff): [Wikipedia: Signs of AI writing — Your detection ability](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Your_detection_ability); Details Deep-Dive `research/slop-ontology-gap-2026-08-24/deep/03` (I33).
---
### Human detection (Empirie)

Humans are notoriously bad at distinguishing LLM text from human text — the
strongest argument against "I can spot AI text myself" and for tool use:

1. **Cheng 2025**: Human ability to distinguish LLM text from human text is no
   better than random chance.
2. **Fiedler 2025** (German theses): Recognition rate of only 57% for AI texts
   and 64% for human-generated texts.
3. **Russell 2025** (preprint): Heavy LLM users identified AI-generated articles
   ~90% of the time — but at ~10% false positives, i.e. 1 in 10 tags is wrong.
   Low-exposure participants performed only slightly better than chance.
4. **Sprach-Konvergenz**: Human writing converges toward LLM style (Yakura 2024 —
   significant LLM influence in spoken content; Geng 2025; Galpin 2025 —
   semantics and word choices). Signal vocabularies decay over time; see
   #47 (Kalibrierungs-Drift) for the re-scoring mandate.

Sources: [Wikipedia: Signs of AI writing — Your detection ability](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Your_detection_ability);
research `deep/03` (I33). This subsection is detect-only context — no scoring
impact.
---
### Human Detection Empirics (why tool-assisted review)

Humans are notoriously bad at distinguishing LLM text from human writing — the
strongest argument against "I can spot AI text myself" and for tool-assisted,
signal-based review instead of gut judgment:

- **Cheng et al. 2025** (Advances in Simulation 10(1):66, DOI 10.1186/s41077-025-00396-6):
  Human ability to distinguish LLM text from human text is **no better than random chance**.
- **Fiedler & Döpke 2025** (Int. Review of Economics Education 49:100321, DOI 10.1016/j.iree.2025.100321):
  German theses (DiLA study) — humans recognized only **57 % of AI texts** and **64 % of human texts**.
- **Russell, Karpinska & Iyyer 2025** (ACL 2025, arXiv:2501.15654): Heavy LLM users reach ~**90 % accuracy** —
  but that still means **~10 % false positives**; light users are barely above chance (both directions).
- **Language convergence**: LLM use shapes human writing, shrinking the gap the eye relies on —
  Yakura et al. 2024 (arXiv:2409.01754, spoken content), Geng et al. 2025 (Findings of ACL 2025),
  Galpin et al. 2025 (arXiv:2506.21817, semantic/lexical drift in scientific English).

Consequence for this reference: human judgment alone is **not** a valid detection signal —
it is the baseline the statistical/ML methods above must beat, and the reason every finding
here is phrased as a named, checkable signal rather than an impression.

Source: [Wikipedia: Signs of AI writing — "Your detection ability"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Your_detection_ability)

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
noisy_or = 1 - Π(1 - weights[s.severity] * s.confidence)        # default
d_i     = 1 - Π_(s ∈ dim_i)(1 - weights[s.severity] * s.confidence)
geometric = Π(d_i ^ w_i) ^ (1 / Σ w_i)   with w_i = max weight in dim_i
# aggregation="geometric": dimension-grouped, damps double punishment
# within one signal family (#117); complements the collision matrix
is_slop = (slop_score >= 0.4) OR (any critical) OR (≥ 2 high severity)
```

## Domain Scoping (triggered_by: domain)

Issue #35: Slop-Defaults sind domain-konditional (unslop, deep/04). Signale
mit `triggered_by: "domain"`-Binding im SSOT (`ontology.json` →
`signalDomains.signals`) feuern nur im passenden Scope:

- `SlopClassifier.classify_text(text, domain="ui_copy")` bzw.
  `deslop_loop_cli.py --domain ui_copy` filtert gebundene Signale vor dem
  Scoring aus; jede Filterentscheidung landet auditierbar in `notes`
  (`domain_filter[<domain>]: skipped <signal>`).
- Ohne `domain`-Angabe bleiben alle Signale aktiv (rückwärtskompatibel).
- Pilot-Bindings (5): `ExclamationExcess`, `TrailingMoral`, `ListHeavy`,
  `ThroatClearing`, `EllipsisExcess` — jeweils mit Begründung
  (`rationale`) und Domänenliste im SSOT.
- Vokabular: essay, blog, article, docs, social, marketing_copy, ui_copy,
  changelog, commit_message, technical_report.
