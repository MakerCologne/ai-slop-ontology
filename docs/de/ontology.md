# AI Slop Ontologie — Kanonische Definition

## ⚠️ Kernparadigma: AI Slop ist ein Risikoprofil, kein binärer Typ

**AI Slop ist nicht einfach "KI-generierter Content".** Slopness entsteht aus der **Kombination** von synthetischer Erzeugung, geringer menschlicher Sorgfalt, Massenskalierung, manipulativer Distribution, schwacher Provenienz und Qualitätsmängeln. Ein Inhalt kann KI-generiert und hochwertig sein. Umgekehrt kann menschlicher Spam wertlos sein. (Shaib et al. 2025, Spotify Policy)

---

## AI Slop (Arbeitsdefinition)

**AI Slop** (auch "Slop Content" oder einfach "Slop") ist digitale Inhalte, die mit generativer KI (LLMs, Bild-/Video-Generatoren etc.) erstellt werden und als low-effort, low-quality, generisch, oberflächlich oder bedeutungsarm wahrgenommen werden. Sie werden massenhaft produziert, um Aufmerksamkeit (Attention Economy), Klicks, Werbeeinnahmen oder andere monetäre Vorteile zu erzielen. Der Begriff hat eine pejorative Konnotation ähnlich wie Spam und wurde 2025 zum Word of the Year von Merriam-Webster und der American Dialect Society gewählt.

**Ursprünge:** Um 2022 mit der Verbreitung von Bildgeneratoren (z.B. auf 4chan), popularisiert u.a. durch Simon Willison 2024. Frühere Begriffe wie "AI garbage" oder "AI pollution" wurden verdrängt.

---

## Kernmerkmale (Prototypische Eigenschaften)

Laut akademischer Analyse (Kommers et al., 2026) zeichnet sich AI Slop durch folgende Eigenschaften aus:

1. **Superficial Competence:** Grammatikalisch korrekt, photorealistisch oder strukturiert, aber ohne Tiefe, Originalität oder echte Intention.
2. **Asymmetric Effort:** Minimaler Input (Prompt) für massenhaften Output; fehlende menschliche Überarbeitung, Recherche oder Kreativität.
3. **Mass Producibility:** Skalierbar für Algorithmen (SEO, Feeds), oft mit Clickbait-Elementen.

**Weitere Dimensionen:**
- **Instrumental Utility:** Zweck (Monetization → Propaganda → Kunst → Trolling)
- **Personalisierungsgrad:** Mass (generisch) → Personalized (zugeschnitten)
- **Surrealismus-Level:** Banal-realistisch bis absurd (z.B. "Shrimp Jesus")

---

## Ontologie-Struktur

### 1. Core Concept: AI Slop

| Attribut | Wertebereich |
|----------|-------------|
| Production Effort | Low (asymmetric) |
| Perceived Quality | Low (generisch, repetitiv, uncanny) |
| Intent | Monetization, Engagement Farming, Propaganda, Spam |
| Detectability | Stylistic tics, artifacts, lack of provenance |

### 2. Media Types (Klassen)

#### Text Slop
Generische Artikel, SEO-Content, Bücher, Kommentare, Memos.

| Indikator | Beschreibung |
|-----------|-------------|
| Übermäßige Listen | Jeder Absatz wird zur Aufzählung |
| Em-Dashes | Übermäßiger Gebrauch von "—" |
| Verbosity | Viele Worte, wenig Substanz |
| Clichés | "In today's fast-paced world..." |
| Niedrige Information Density | unique_words / total_words < 0.40 |

#### Image/Video Slop
Uncanny-Valley-Bilder/Videos (bizarre Kombinationen, glatte Texturen, Morphing, falsche Physik).

**Beispiele:** Shrimp Jesus, Cat Soap Operas, Fake-Historical Photos, Veteran Birthday Signs

| Indikator | Beschreibung |
|-----------|-------------|
| Extra Limbs | Zusätzliche Finger/Gliedmaßen |
| Unnatural Smoothness | Zu perfekte Texturen |
| Distorted Text | Kauderwelsch im Bild |
| Over-Symmetry | Nicht-natürliche Symmetrie |

#### Audio/Music Slop
Generierte Stimmen/Songs mit fehlender Emotionalität.

**Beispiele:** Velvet Sundown (Fake Band auf Spotify)

#### Hybrid/Multimodal
AI-Thumbnails + Voiceover + Text. Die wachsende Dominanz-Form.

### 3. Taxonomy nach Purpose

| Purpose | Beschreibung | Beispiele |
|---------|-------------|-----------|
| **Engagement/Clickbait Slop** | Virales Potenzial | Motivational, Emotional Bait ("Veteran Birthday") |
| **SEO/Content Farm Slop** | Keyword-stuffed für Ads | 10-Websites-to-Leverage-AI Artikel |
| **Propaganda/Disinfo Slop** | Politisch | Trump-AI-Images, Spamouflage (China/Russland) |
| **Monetization Slop** | Direkte Revenue | Facebook Bonuses, Fake Shops, Affiliate Farming |
| **Spam/Noise Slop** | Füllmaterial | Kein klarer Zweck, flutscht durch |

### 4. Taxonomy nach Form/Quality

| Achse | Low | High |
|-------|-----|------|
| Surrealismus | Banal-realistisch (SEO-Artikel) | Absurd (Shrimp Jesus) |
| Personalisierung | Mass (generisch) | Personalized (zugeschnitten) |
| Human Oversight | Reines AI | AI-assisted mit minimal Edits |

### 5. Quality Dimensions / Slop Indicators (Shaib et al. 2025)

| Theme | Dimension | Code | Slop-Signal |
|-------|-----------|------|-------------|
| **Information Utility** | Density | IU1 | unique_words / total_words < 0.40 |
| **Information Utility** | Relevance | IU2 | Irrelevante Tangenten, Topic Drift |
| **Information Quality** | Factuality | IQ1 | Hallucinations, fabrications |
| **Information Quality** | Bias | IQ2 | Systematische Schieflage |
| **Style Quality** | Repetition | SQ1 | Token-Wiederholung > 0.20 |
| **Style Quality** | Templatedness | SQ2 | Formelhafte Struktur, POS-Pattern |
| **Style Quality** | Coherence | SQ3 | Sprünge, Inkonsistenz |
| **Style Quality** | Fluency | SQ4 | Paradox: Zu flüssig = Slop |
| **Style Quality** | Verbosity | SQ5 | Viele Worte, wenig Substanz |
| **Style Quality** | Word Complexity | SQ6 | Unnötig komplexe Vokabular |
| **Style Quality** | Tone | SQ7 | Uniform, unnatürlich |

---

## Slopsquatting (Code-Slop Sicherheitsthreat)

AI halluziniert Paketnamen → Angreifer registrieren sie → Supply Chain Attacke.

| Statistik | Wert |
|-----------|------|
| Halluzinationsrate gesamt | 19.7% |
| Open-Source Modelle | 21.7% |
| GPT-4 Turbo | 3.59% |
| CodeLlama | >33% |
| Einzigartige halluzinierte Namen | 205,000+ |

**Reale Vorfälle:**
- `huggingface-cli`: 30,000+ Downloads in 3 Monaten (leeres Paket)
- `react-codeshift`: 237 Repositories infiziert durch AI-Agent-Skills
- `unused-imports`: Echte Malware, 233 Downloads/Woche

---

## Knowledge Collapse (3-Stadien-Modell)

| Stadium | Name | Fakten | Format | Gefahr |
|---------|------|--------|--------|--------|
| A | Knowledge Preservation | ✅ Korrekt | ✅ Intakt | Niedrig |
| B | Knowledge Collapse | ❌ Falsch | ✅ Korrekt | **KRITISCH** — "Confidently Wrong" |
| C | Instruction Collapse | ❌ Random | ❌ Incoherent | Hoch, aber erkennbar |

**Stadium B ist die "Valley of Dangerous Competence":** Oberflächliche Metriken zeigen keine Probleme, aber die faktische Richtigkeit degradiert unsichtbar.

---

## Engagement Farming (Ursachenanalyse)

AI Slop ist nicht die Ursache — es ist das Symptom einer broken Attention Economy:

1. **Incentive-System:** Content → Engagement → Revenue (unabhängig von Qualität)
2. **Kosten:** AI senkt Produktionskosten gegen ~0€
3. **Targeting:** Ältere Nutzer (Facebook: 24% über 55) sind primäres Opfer
4. **Impact:** Echte Creator werden verdrängt ("put a ton of people out of business")
5. **Plattform-Doppelmoral:** Echte Creator werden für Guidelines verfolgt, Slop läuft durch

---

## Normative Framings

| Framing | Kern |
|---------|------|
| **Epistemic Pollution** | Verschmutzung des Informationsökosystems |
| **Automation Bias** | Menschen vertrauen AI blind |
| **Illegitimate Reason-Giving** | AI hat keine epistemic standing |
| **Nonconsensual Imposition** | Unreviewed AI = unpaid labour für Empfänger |
| **Attention Economy Exploitation** | Content optimiert für Engagement, nicht Information |
| **Consumer Fraud** | Fake Produkte/Reviews |
| **Supply Chain Attack** | Slopsquatting als Security-Risiko |
| **Democratic Harm** | Politischer Slop untergräbt Demokratie |

### 6. Detection Red Flags

#### Text
| Red Flag | Beschreibung | Konfidenz |
|----------|-------------|----------|
| Overused Phrases | "delve", "tapestry", "in today's fast-paced world" | 0.8 |
| Emojis in Code | Emojis in Code-Kommentaren/-Dokumentation | 0.85 |
| Perfect but Soulless | Perfekte Struktur aber keine menschliche Note | 0.7 |
| Excessive Lists | Jeder Absatz wird zur Aufzählung | 0.75 |
| Trailing Morals | Endet mit generischer Moral/Lektion | 0.8 |
| Em-Dash Overuse | Übermäßiger Gebrauch von "—" | 0.85 |
| Low Information Density | unique_words / total_words < 0.40 | 0.9 |
| Uniform Sentence Length | Alle Sätze ähnliche Länge, niedrige Burstiness | 0.7 |

#### Bild/Video
| Red Flag | Beschreibung | Konfidenz |
|----------|-------------|----------|
| Glossy Textures | Zu perfekte, glänzende Texturen | 0.7 |
| Warped Backgrounds | Verzerrte Hintergründe | 0.8 |
| Inconsistent Details | Details ändern sich je nach Zoom | 0.85 |
| Morphing | Objekte verformen sich unnatürlich | 0.8 |
| Bad Text Rendering | Kauderwelsch im Bild | 0.95 |
| Extra Limbs | Zusätzliche Finger/Gliedmaßen | 0.9 |
| Frame Flicker | Flickern zwischen Video-Frames | 0.85 |

#### Allgemein
| Red Flag | Beschreibung | Konfidenz |
|----------|-------------|----------|
| Missing Provenance | Keine Watermarks, Quellen, Herkunft | 0.6 |
| Mass Production Pattern | Gleiche Vorlage über hunderte Inhalte | 0.85 |
| No Author Identity | Fake-Autoren (AI-Headshots, kein History) | 0.8 |
| Cross-Lingual Artifacts | Hindi/andere Sprach-Patterns im englischen Output | 0.7 |

---

### 7. Actors & Ecosystem

#### Producers (Slop Farmers / Sloppers)
Individuen/Firmen in Entwicklungsländern (Indien, Kenia, Philippinen), die mit Prompts skalieren.

**Patterns:**
- Cross-Lingual Prompts (Hindi etc.) → absurde Outputs
- AI-Headshots für Fake-Autoren
- Bestehende virale Content identifizieren → AI repliziert sie
- 80+ AI-Pins/Tag auf Pinterest

**Bekannte Fälle:**
| Name | Methode | Zielgruppe | Skalierung |
|------|---------|-----------|------------|
| Jesse Cunningham | Facebook + Pinterest Slop Farming | 50+ female | 8.6M monthly views (Bonsai Mary) |
| Content Goblin Users | AI-powered listicle generator → faux blogs | Alle | Tausende AI-Artikel |

#### Platforms
| Plattform | Rolle | Verstärker |
|-----------|-------|----------|
| **Facebook** | Primäres Opfer (24% Nutzer über 55) | Performance Bonus Program, Algorithm rewards engagement |
| **YouTube** | 278 AI-Kanäle, 63 Mrd. Views/Jahr | YouTube Kids: 40% AI-Slop |
| **TikTok** | AI-Video-Slop (Cat Soap Operas) | For You Page bevorzugt Novelty |
| **Pinterest** | Aspirational AI-Slop (Fake-Plants) | 8.6M Views für einzelne Accounts |
| **Google Search** | AI Overviews verstärken Slop | SEO-Slop rankt durch Volume |
| **Spotify** | Fake Artists, Millionen Listeners | Royalty-Multiplication |

#### Consumers
| Consumer | Rolle | Vulnerabilität |
|----------|-------|---------------|
| **Algorithmen** | Engagement-Signale → Amplifikation | Volume + Engagement = Quality-unabhängig |
| **Nutzer** | Unwissende Konsumenten | Ältere Nutzer, geringe AI-Literacy |
| **Advertiser** | Programmatic Ads auf Slop-Inventar | Cheap Inventory, aber sinkendes Vertrauen |

---

### 8. Impacts

#### Web/Search
- **Content Collapse:** Echte Inhalte werden von Slop verdrängt
- **SEO Degradation:** Schlechtere Rankings für recherchierte Inhalte
- **Model Collapse:** Training auf AI-Output → irreversible Degradation (Nature 2024)
- **Knowledge Collapse:** Fakten verfallen, Fluency bleibt ("Confidently Wrong")

#### Society
- **Misinfo:** AI-generierte Desinformation massenhaft verbreitet
- **Trust Erosion:** Sinkendes Vertrauen in digitale Inhalte
- **Democracy Risks:** Politischer Slop untergräbt Diskurs
- **Creator Displacement:** Echte Creator verlieren Einkommen ("put a ton of people out of business")

#### Wirtschaft
- **Cheap Ad Inventory:** Slop liefert billiges Werbeinventar
- **Declining Engagement:** Langfristig sinkendes User-Engagement
- **Creator Economy:** Blogging/Food/Handwerk-Sektoren betroffen

---

### 9. Relationships & Dynamics

| Beziehung | Mechanismus | Ergebnis |
|-----------|------------|----------|
| Slop → Algorithm | Volume + Engagement > Quality | Positive Feedback Loop |
| Slop → Human Content | Enshittification | Echte Creator verdrängt |
| Detection → Mitigation | Watermarking, Filters, HITL, Policies | Arms Race |
| Slop vs. Valuable AI | Human Oversight, Effort, Utility | **Nicht alles AI ist Slop** |

**Key Distinction:** Der Unterschied zwischen Slop und wertvollem AI-Content liegt in:
- **Human Oversight** — Menschliche Überarbeitung vorhanden?
- **Effort** — Echter Aufwand oder nur Prompt→Output?
- **Utility** — Echter Informationsgewinn oder Füllmaterial?

---

### 10. Countermeasures & Future

#### Detection
- Linguistic Patterns: Buzzword-Frequenz, Em-Dash-Rate, Sentence-Burstiness
- Statistical Analysis: Perplexity, Information Density, Repetition Ratio
- Watermarking: Kryptographische Token-Partitionierung (Green/Red Lists)
- Community Tools: Kagi SlopStop, SlopDetector.org, GPTZero, Originality.ai

#### Platforms
- Bessere automatische Moderation
- AI-Content Kennzeichnungspflicht (Labeling)
- Algorithm-Adjustment: Quality-Signals statt reiner Engagement

#### User/Agent Level
- Provenance Checks: C2PA, Watermarks, Reverse Image Search
- Quality Scoring: Slop Score berechnen (Density, Repetition, Verbosity)

#### Risiken
- **Arms Race:** Bessere Generatoren umgehen Detection — cat-and-mouse game
- **Positives Potenzial:** Sorgfältige AI-Nutzung ist KEIN Slop — Unterscheidung bleibt wichtig

---

### 11. Slopness als Risikoprofil

**Slopness Score = f(Generierung, Sorgfalt, Skalierung, Distribution, Provenienz, Qualität)**

| Dimension | Low Risk (0-2) | Medium Risk (3-5) | High Risk (6-10) |
|-----------|----------------|-------------------|------------------|
| **Generierung** | Menschlich geschrieben | AI-assisted, human-edited | Reines AI, kein Edit |
| **Sorgfalt** | Gründliche Recherche, Testing | Oberflächliche Prüfung | Keine Überprüfung |
| **Skalierung** | Einzelner Artikel | Serie, kuratiert | Massenproduktion (100+/Tag) |
| **Distribution** | Organisch, zielgerichtet | SEO-optimiert | Clickbait, Engagement Farming |
| **Provenienz** | Klare Autorschaft, Quellen | Teilweise Quellen | Fake-Autor, keine Quellen |
| **Qualität** | Originell, informativ | Generisch, teils nützlich | Substanzlos, repetitiv |

### 12. Agent Risk Levels

| Level | Beschreibung | Agent-Verhalten |
|-------|-------------|----------------|
| 🟢 **Clean** | Menschlich, geprüft, mit Quellen | Normal verwenden |
| 🟡 **AI-Assisted** | AI-generiert, human-edited, nützlich | Mit Quellenangabe verwenden |
| 🟠 **Suspicious** | AI-generiert, keine Quellen, generisch | Verifizieren vor Verwendung |
| 🔴 **Slop** | AI-generiert, substanzlos, massenhaft | **NICHT in RAG/Memory aufnehmen** |
| ⚫ **Malicious** | Slop + Absicht (Disinfo, Slopsquatting) | **Blockieren + Warnen** |

### 13. Retrieval Collapse ⚠️ (Agenten-spezifisch)

**Für Agenten ist AI Slop besonders gefährlich**, weil RAG-, Search- und Memory-Systeme kontaminiert werden.

**Zwei Stufen:**
1. **Quellendominanz:** KI-generierte Inhalte dominieren Suchergebnisse → Reduzierte Quellendiversität
2. **Pipeline-Kontamination:** Minderwertige Inhalte dringen in Retrieval-Pipelines → Agenten antworten mit Slop

**Experimentell:** 67% Pool-Kontamination → über 80% Expositionskontamination.

**Abwehrmaßnahmen:**

| Maßnahme | Implementierung |
|----------|---------------|
| Source Diversity Check | Min. 3+ unterschiedliche Quell-Domains |
| Slop Score Gate | Nur Quellen mit Score < 0.4 aufnehmen |
| Provenance Filter | Bevorzuge menschlich verifizierte Quellen |
| Cross-Validation | Min. 2 unabhängige Bestätigungen |
| Contamination Detection | Information Diversity der Top-10 prüfen |

### 14. AI Slop vs. Spam

| | Spam | AI Slop |
|---|------|--------|
| **Primär** | Unerwünschte Distribution | Billige Generierung + Oberflächlichkeit |
| **Mechanismus** | Volume + Deception | Superficial Competence + Mass Producibility |
| **Google** | — | "Scaled Content Abuse" = Suchmanipulation, nicht Nutzerhilfe |

**Überlappung:** Slop KANN Spam sein, aber nicht alles Slop ist Spam und nicht alles Spam ist Slop.

### 15. Plattform-Statistiken (2026)

| Metrik | Wert | Quelle |
|--------|------|--------|
| Deezer AI-Tracks/Tag | ~75.000 (44% der Uploads) | Deezer 20.04.2026 |
| YouTube AI-Kanäle | 278 (63 Mrd. Views/Jahr) | Research |
| YouTube Kids AI-Anteil | ~40% | Analysis |
| Facebook Nutzer >55 | 24% | Platform Data |
| AI-Package-Halluzination | 19.7% der Empfehlungen | USENIX 2025 |
| Pinterest Slop-Account | 8.6M Monthly Views | Futurism |

---

## Quellen

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
