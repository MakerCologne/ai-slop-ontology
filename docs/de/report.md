> Research by Goswin | zai/glm-5.1 | 2026-05-20
> Queries: "AI slop ontology taxonomy definition", "AI slop detection methods tools automated", "AI slop categories types examples", "knowledge collapse epistemic pollution", "AI slop image video audio multimodal", "Why Slop Matters Kommers"
> Pages fetched: 9 | Depth: Large (🟢)

# AI Slop — Deep Research Report

## Executive Summary

AI Slop ist ein etablierter Begriff (Merriam-Webster Word of the Year 2025) für niedrigqualitative, massenhaft produzierte KI-generierte Inhalte. Die akademische Forschung hat 2025–2026 erste formale Taxonomien entwickelt (Shaib et al., Kommers et al.), aber eine **maschinenlesbare Ontologie für Agenten** existiert noch nicht. Stefan hat bereits erhebliche Vorarbeit in seinen GitHub-Repos geleistet: `quality-agent` enthält eine 200-Zeilen Slop-Referenz, `local-ai-setup` ein vollständiges Multi-Modal-Detection-Skill mit 22 Techniken und Python-Implementierung.

---

## 1. Definitionen & Akademischer Stand

### 1.1 Kern-Definitionen

| Quelle | Definition |
|--------|------------|
| **Merriam-Webster** (Wort des Jahres 2025) | "Digital content of low quality that is produced usually in quantity by means of artificial intelligence" |
| **Simon Willison** (Prägend 05/2024) | "Mindlessly generated and thrust upon someone who didn't ask for it" — Analogie zu Spam |
| **Wikipedia** | "Digital content made with generative AI that is perceived as lacking in effort, quality, or meaning, and produced in high volume" |
| **Cambridge Dictionary** | "Content on the internet that is of very low quality, especially when it is created by artificial intelligence" |
| **Kommers et al. (2026)** | Drei prototypische Eigenschaften: Superficial Competence, Asymmetric Effort, Mass Producibility |

### 1.2 Schlüssel-Papiere

1. **Kommers et al. (Jan 2026): "Why Slop Matters"** — ACM AI Letters. Argumentiert dass Slop eine soziale Funktion erfüllt (Supply-side Lösung für kulturelle Nachfrage) und ästhetischen Wert hat. Drei Eigenschaften: Superficial Competence, Asymmetric Effort, Mass Producibility. Drei Varianz-Dimensionen: Instrumental Utility, Personalization, Surrealism. (arXiv: 2601.06060)

2. **Shaib et al. (Sep 2025, rev. Jan 2026): "Measuring AI 'Slop' in Text"** — Northeastern/Meta AI. Erstes systematisches Mess-Framework. 19 Experten-Interviews → 3 Themes × 12 Codes: Information Utility (Density, Relevance), Information Quality (Factuality, Bias), Style Quality (Repetition, Templatedness, Coherence, Fluency, Verbosity, Word Complexity, Tone). Span-Level Annotation an 150 News + 100 QA-Passagen. (arXiv: 2509.19163, GitHub: cshaib/slop)

3. **MINT Lab (März 2026): "AI Slop: Definitions and Normative Status"** — Umfassende Literaturanalyse (14 Papers). Vier normative Framings: Epistemic Pollution, Automation Bias, Illegitimate Reason-Giving, Nonconsensual Imposition. Technische Ursache: LLMs generieren Output "towards the center of the distribution" → systematische Vermeidung des Long Tail.

---

## 2. Taxonomien

### 2.1 SlopDetector.org — 5 Text-Slop-Typen

| Typ | Erkennungsphrase | Beschreibung |
|-----|------------------|-------------|
| **Generic Slop** | "In today's fast-paced world..." | Vage, generische Einleitungen ohne Substanz |
| **Pseudo-Insight Slop** | "The key is to find balance..." | Klingt tiefgründig, sagt aber nichts |
| **Fake Authority Slop** | "Studies have shown..." | Autoritärer Ton ohne echte Quellen |
| **Wikipedia Rehash** | "X is defined as..." | Umformuliertes Allgemeinwissen ohne Analyse |
| **Wellness Slop** | "Self-care isn't selfish..." | Universalisierte Selbsthilfe ohne persönliche Erfahrung |

Antidot: Specificity, Lived Experience, Cited Sources, Information Gain.

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

### 2.3 Kommers et al. — 3 Prototypische Eigenschaften + 3 Varianz-Dimensionen

**Prototypische Eigenschaften:**
- **Superficial Competence**: Wirkt kompetent, ist aber bei näherem Hinsehen substanzlos
- **Asymmetric Effort**: Erstellung erfordert unverhältnismäßig weniger Aufwand als ohne KI
- **Mass Producibility**: Teil eines digitalen Ökosystems massenhafter Produktion

**Varianz-Dimensionen:**
- **Instrumental Utility**: Warum wurde es erstellt? (Geld → Kunst → Trolling)
- **Personalization**: Ist es generisch oder auf eine Person zugeschnitten?
- **Surrealism**: Von absurdisch unplausibel bis täuschend realistisch

### 2.4 SlopScan Hackathon (Mai 2026) — 8 Domänen

Code Review | Docs & KBs | Hiring & Resumes | Communications | Content & SEO | Academia | Marketplaces | Social & News

---

## 3. Medientypen & Beispiele

### 3.1 Text-Slop
- SEO-Spam-Artikel ("10 Ways to Leverage AI")
- KI-generierte LinkedIn-Posts
- Hollow PR-Beschreibungen
- Fake wissenschaftliche Papers
- AI-generierte Amazon-Reviews

### 3.2 Bild-Slop
- **Shrimp Jesus** (Facebook-Virals, bizarre KI-Kreationen)
- Fake Veteran-Bilder ("Today's my birthday, please like")
- AI-Pflanzenbilder für Fake-Samenverkauf
- Holocaust-Opfer-Fälschungen
- Politische Propaganda (Trump als Papst, Musketier etc.)

### 3.3 Video-Slop
- 278 YouTube-Kanäle mit AI-Content (63 Mrd. Views/Jahr)
- YouTube Kids: 40% AI-Slop (Alphabet-Videos mit nonsensical Content)
- AI-generierte "Cat Soap Operas", "Fruit Love Island" (TikTok)

### 3.4 Audio/Musik-Slop
- Fake Artists auf Spotify mit Millionen Listeners
- Velvet Sundown (AI-erstellte Band)

### 3.5 Code-Slop
- Hallucinierte Packages ("slopsquatting" Angriffe)
- Uniform generischer Code-Stil ohne menschliche Note
- Bulk-generierte Commits ohne Review
- Fake Review-Kommentare

---

## 4. Normative Framings (Warum Slop problematisch ist)

1. **Epistemic Pollution** — Verschmutzung des Informationsökosystems. Van Rooij (2025): "Epistemicide". Coeckelbergh (2026): "Epistemic Laziness". Peterson (2025): "Knowledge Collapse" — Gesellschaft rückt 2.3x weiter von der Wahrheit entfernt bei nur 20% KI-Content-Kosten-Nachlass.

2. **Automation Bias** — Menschen vertrauen automatisierten Outputs systematisch zu sehr. Danry et al. (2024): AI-generierte täuschende Erklärungen amplifizieren Glauben an falsche Schlagzeilen signifikant — Cognitive Reflection schützt NICHT.

3. **Illegitimate Reason-Giving** (Enoch 2012) — KI-Content präsentiert sich als informatives Testimony, aber die Erfolgsbedingungen fehlen: keine epistemische Standing, keine Accountability, keine kommunikative Intention.

4. **Nonconsensual Imposition** (Doctorow 2026) — Unreviewed AI-Output an Fremde zu senden ist "coercing a stranger into unpaid labour" (die Arbeit der Evaluierung).

---

## 5. Detection-Methoden

### 5.1 Statistische Ansätze
- **Perplexity** (DetectGPT): Human text > 100 PPL, AI text < 50 PPL
- **Burstiness**: Satzkomplexitäts-Variation (Menschen: hoch, KI: uniform)
- **N-gram Frequenz**: AI overused bestimmte Wortkombinationen
- **Watermarking**: Kryptographische Token-Partitionierung (Green/Red Lists)

### 5.2 ML-Klassifikatoren
- RoBERTa fine-tuned auf Human/AI-Korpus (90%+ AUROC kontrolliert)
- Problem: unbekannte Modelle, post-editierte Texte, kurze Snippets

### 5.3 Linguistische Patterns (Shaib et al. + SlopDetector)
- Buzzword-Frequenz: delve, realm, tapestry, leverage, synergy, robust, cutting-edge
- Punctuation-Anomalien: Em-dashes, Ellipses, excessive Exclamation
- Strukturelle Quirks: Übermäßige Listen, Trailing Morals, uniforme Absatzlängen
- Information Density: Unique Words / Total Words (< 0.40 = Slop)

### 5.4 Bestehende Tools
- **SlopDetector.org** — Web-basierter 5-Kategorien-Detektor
- **SlopScan Hackathon** (29. Mai – 1. Juni 2026) — Baut Detection-Tools
- **GPTZero, Originality.ai** — KI-Text-Detection (aber nicht Slop-spezifisch)

---

## 6. Stefans Vorarbeit auf GitHub

### 6.1 `hikaman/quality-agent`
- `docs/refinements/ai.slop.md` — Umfassende 200+ Zeilen Referenz mit allen Detection-Techniken, Code-Halluzination-Beispielen, Referenz-Tabelle
- `.skills/slop-skill/SKILL.md` — Einfacher Skill: Text-Repetition + Image-Variance
- `features/slop_detection.feature` — BDD-Feature-Definition
- Integration: AutoGen, LangGraph, MCP-Tool

### 6.2 `hikaman/local-ai-setup`
- `skills/ai-slop-detection/` — **Vollständiges Skill mit 16 Dateien**
  - `SKILL.md` (747 Zeilen, 22 Techniken) — zu groß aber comprehensive
  - `detectors.py` — Unified Multi-Modal Entry Point
  - `text_detector.py` — Text-spezifische Analyse
  - `image_detector.py` — Bildartefakt-Erkennung
  - `scoring.py` — Slop-Score-Berechnung
  - `content_quality.py` — Qualitätsmetriken
  - `analyzer_enhanced.py` — Erweiterte Analyse

### 6.3 `hikaman/skill-reviews`
- `2026-03-16/ai-slop-detection.md` — Detailliertes Review (60/100 Score)
  - P0: SKILL.md zu groß (747 Zeilen → ~120 Zeilen empfohlen)
  - P1: Kein Progressive Disclosure, Overlap mit ai-quality-assurance
  - Positiv: Detection-Methodik ist "genuinely valuable and well-implemented"

---

## 7. Empfehlung: AI Slop Ontologie für Agenten

### 7.1 Was fehlt

Die bestehenden Taxonomien sind:
- **Shaib et al.**: Akademisch, nicht maschinenlesbar
- **SlopDetector**: Web-Tool, keine API/Ontologie
- **Stefans Skills**: Implementierung-focused, keine formale Ontologie
- **Kommers et al.**: Konzeptionell, aber keine operationalisierte Form

### 7.2 Ontologie-Architektur

Siehe `ontology.ttl` (Turtle/RDF) und `ontology.json` (JSON-LD) in diesem Ordner.

**Kern-Klassen:**
1. `SlopInstance` — Eine konkrete Slop-Beobachtung
2. `SlopType` — Taxonomie der Slop-Arten (hierarchisch)
3. `SlopDimension` — Messbare Dimensionen (Density, Relevance, etc.)
4. `SlopSignal` — Erkennbare Signale/Indikatoren
5. `SlopMedium` — Text, Image, Video, Audio, Code
6. `SlopNormativeFraming` — Warum es problematisch ist
7. `SlopDetection` — Detection-Methoden und Tools
8. `SlopCountermeasure` — Was man dagegen tun kann

**Beziehungstypen:**
- `hasType`, `hasMedium`, `hasSignal`, `hasDimension`
- `measuredBy`, `detectedBy`, `counteredBy`
- `variantOf`, `overlapsWith`, `relatedTo`

### 7.3 Formate

| Format | Zweck |
|--------|-------|
| `ontology.ttl` | RDF/Turtle — Standard für semantische Ontologien |
| `ontology.json` | JSON-LD — Agenten-freundlich, direkt ladbar |
| `ontology.md` | Mensch-lesbare Dokumentation |

### 7.4 Integration mit bestehenden Skills

Die Ontologie soll Stefans `local-ai-setup/skills/ai-slop-detection/` ergänzen:
- Skill bleibt die **Implementierung** (Python-Detektoren, Scoring)
- Ontologie wird das **Wissensmodell** (Klassifikation, Beziehungen, Referenz)
- Agenten laden die Ontologie als Kontext, nutzen das Skill für Detection

---

## Sources

1. [Wikipedia: AI slop](https://en.wikipedia.org/wiki/AI_slop) — Umfassende Übersicht mit politischen/kulturellen Beispielen
2. [SlopDetector.org: Slop Taxonomy](https://slopdetector.org/slop-taxonomy) — 5 Text-Slop-Typen mit Beispielen
3. [Shaib et al. (2025): Measuring AI "Slop" in Text](https://arxiv.org/abs/2509.19163) — Erstes akademisches Mess-Framework, 12 Codes aus 19 Experten-Interviews
4. [Kommers et al. (2026): Why Slop Matters](https://arxiv.org/abs/2601.06060) — ACM AI Letters, 3 prototypische Eigenschaften
5. [MINT Lab (2026): AI Slop: Definitions and Normative Status](https://mintresearch.org/reports/ai-slop/) — Literaturanalyse, 4 normative Framings
6. [Glukhov (2025): Detecting AI Slop](https://www.glukhov.org/post/2025/12/ai-slop-detection/) — Technische Detection-Methoden mit Code
7. [SlopScan Hackathon](https://slopscan.dev/) — 8 Domänen, 72h Hackathon, Mai 2026
8. [SlopDetector.org: AI Slop Examples](https://slopdetector.org/ai-slop-examples) — 21+ dokumentierte Fälle
9. [Stefan's quality-agent: ai.slop.md](https://github.com/hikaman/quality-agent) — Vorarbeit Detection-Referenz
10. [Stefan's local-ai-setup: ai-slop-detection](https://github.com/hikaman/local-ai-setup) — 22 Techniken, Multi-Modal Python-Skill
11. [Stefan's skill-reviews: ai-slop-detection.md](https://github.com/hikaman/skill-reviews) — Review mit Verbesserungsvorschlägen
