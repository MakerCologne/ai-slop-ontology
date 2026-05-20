# AI Slop Ontologie — Kanonische Definition

## AI Slop (Kernkonzept)

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
