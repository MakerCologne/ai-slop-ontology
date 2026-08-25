---
title: "AI Slop Ontology"
version: "2.6.0"
date: "2026-08-25"
language: "de/en (bilingual; technical terms in English)"
intended_consumers: ["LLM agents", "quality-assurance pipelines", "content moderation", "researchers"]
license: "CC BY 4.0 (recommended)"
machine_readable_block: "see §10 (YAML)"
---

# AI Slop Ontology

Eine strukturierte, agentenkonsumierbare Wissensbasis über das Phänomen *AI Slop*. Konsolidiert aus akademischer Forschung (Shaib et al. 2025; Madsen & Puyt 2025; Shumailov et al. 2024), investigativem Journalismus (404 Media; New York Times; Guardian), Industrieforschung (NewsGuard; Pangram Labs; BetterUp/Stanford) und Lexikographie (Merriam-Webster 2025; Oxford Dictionary 2024).

---

## 1. Kerndefinition

**AI Slop** (Klasse: `Phenomenon`) bezeichnet generativ KI-erzeugte digitale Inhalte, die als geringwertig, generisch, irreführend oder ungewollt wahrgenommen werden und typischerweise in hoher Menge zur Aufmerksamkeits- oder Geldgewinnung produziert werden.

**Drei konvergente Lexikon-Definitionen:**

- *Merriam-Webster* (Word of the Year 2025): "digital content of low quality that is produced usually in quantity by means of artificial intelligence" [1].
- *Oxford Dictionary* (Shortlist Word of the Year 2024): "material produced using a large language model, which is often viewed as being low-quality or inaccurate" [2].
- *Willison-Kriterium* (operationale Heuristik): KI-Inhalt ist Slop, wenn er "mindlessly generated and thrust upon someone who didn't ask for it" ist [3].

**Notwendige Bedingungen (alle drei müssen erfüllt sein):**
1. Generative KI ist primäre Quelle des Inhalts.
2. Es fehlt menschliche Sorgfalt, Kuration oder Verifikation.
3. Der Inhalt wird unverlangt publiziert/distribuiert (Push statt Pull).

**Abgrenzung:** Nicht jeder KI-generierte Inhalt ist Slop. Sorgfältig kuratierte, geprüfte und intentional veröffentlichte KI-Hilfsoutputs fallen ausdrücklich nicht unter die Definition (Willison 2024; Shaib et al. 2025 §3).

---

## 2. Etymologie und Begriffsgeschichte

| Jahr | Ereignis | Quelle |
|------|----------|--------|
| ~1700 | "Slop" = weicher Schlamm (Englisch) | OED; [4] |
| ~1800 | Bedeutungserweiterung zu "Schweinetränke / Abfall" | [4] |
| 2022 | Erste Belege für "AI slop" online | [5] |
| Anfang 2024 | Poet/Technologe "deepfates" verwendet Begriff auf X als "term for unwanted AI generated content" | [4][6] |
| Mai 2024 | Simon Willison popularisiert auf Blog mit Spam-Analogie | [3] |
| 2024 | Oxford Dictionary Word-of-the-Year-Shortlist (+332 % Nutzung) | [2] |
| 2025 | Merriam-Webster & American Dialect Society: Word of the Year | [1] |
| 2025–2026 | Akademische Operationalisierung (Shaib et al., Madsen & Puyt, MINT Lab) | [7][8][9] |

**Historische Analoga:** Grub Street (London, 1700er-Jahre, billige Druckwerke), Pulp Fiction, Churnalism, Spam, Kitsch (München, 1860er, abwertend für massenproduzierte Kunst). Alle bezeichnen *massenproduzierten, ökonomisch motivierten, ästhetisch/epistemisch defizitären Output* einer neuen Produktionstechnologie [4][10].

---

## 3. Klassenhierarchie (Ontologie-Kern)

```
Phenomenon: AISlop
├── ByModality
│   ├── TextSlop
│   │   ├── ArticleSlop          (Content farms, UAINs)
│   │   ├── BookSlop             (Amazon AI-Bücher)
│   │   ├── RecipeSlop           (SEO-Recipes)
│   │   ├── AcademicSlop         (gefälschte Paper, KI-Reviews)
│   │   ├── PeerReviewSlop       (Organization Science 2026: >30 % KI-Reviews)
│   │   ├── SecurityReportSlop   (curl-Bug-Bounty-Ende Feb 2026)
│   │   ├── ProductReviewSlop    (Fake-Reviews)
│   │   └── Workslop             (Niederhoffer et al. 2025)
│   ├── ImageSlop
│   │   ├── EngagementBaitImage  (Shrimp Jesus, AI-Christus)
│   │   ├── DeceptiveProductImage (E-Commerce Fake-Pflanzen)
│   │   ├── PoliticalSlopImage   (Trump-Pope, deepfake endorsements)
│   │   └── ArtSlop              (generische AI-Poster)
│   ├── VideoSlop
│   │   ├── ChildrenContentSlop  (NYT 2026: ~40 % YouTube Kids)
│   │   ├── BrainrotVideo        (Italian brainrot, Fruit Love Island)
│   │   ├── DeepfakeVideo        (Sora-Missbrauch)
│   │   └── HistoricalSlopVideo  (vereinfachte Geschichte)
│   ├── AudioSlop
│   │   ├── AIMusic              (Spotify-Royalty-Fraud, Smith 2024)
│   │   ├── VoiceCloneSlop       (KI-Synchronisation)
│   │   └── AINarrationSlop      (Paramount/Novocaine 2025)
│   ├── CodeSlop
│   │   ├── HallucinatedPackage  (super-fast-json-parser etc.)
│   │   ├── FabricatedAPI        (nicht existierende Methoden)
│   │   └── VulnerableAISnippet  (hardcoded Secrets, SQL-Injection)
│   └── MultiModalSlop           (Bild+Text+Audio kombiniert)
│
├── ByIntent
│   ├── MonetizationSlop         (Creator-Bonus, MFA-Sites, Ad-Fraud)
│   ├── PoliticalSlop            (Wahlbeeinflussung, Propaganda)
│   ├── DisinformationSlop       (Russland/Iran-Operationen)
│   ├── AccidentalSlop           (gut gemeint, schlechte Qualität)
│   ├── HumorousSlop             (Meme-Kultur, Fruit Love Island)
│   └── WorkplaceSlop            (Workslop: Performance-Theater)
│
├── ByActor
│   ├── ContentFarm              (NewsGuard: 3.006+ Sites Mar 2026)
│   ├── SoloMonetizer            (Indien/Philippinen/Kenia-Creator)
│   ├── StateActor               (Storm-1516, Center for Geopolitical Expertise)
│   ├── Corporation              (Activision, Paramount, A24, Amazon)
│   ├── PoliticalCampaign        (Trump-Posts, Cuomo)
│   └── AutomatedBot             (Bot-Netzwerke, KI-Agenten)
│
└── ByPlatform
    ├── SocialMedia              (Facebook, Instagram, TikTok, X)
    ├── SearchResult             (Google: 19 % AI-Anteil Jan 2025)
    ├── EcommerceListing         (Amazon, eBay)
    ├── StreamingService         (Spotify, YouTube, Netflix-Stil)
    └── EnterpriseChannel        (E-Mail, Slack, Docs → Workslop)
```

---

## 4. Qualitäts-Dimensionen (operationale Taxonomie)

Konsolidiert aus Shaib et al. 2025 (drei Themen, sieben Codes), validiert mit 213 News-Artikeln und 123 QA-Passagen.

### 4.1 Information Utility (IU)
| Code | Name | Operationalisierung | Messmethode |
|------|------|---------------------|-------------|
| `IU1` | Density | Substanzielle Information pro Wortzahl | Token-Entropie (Meister et al. 2021); Propositional Idea Density (Brown et al. 2008) |
| `IU2` | Relevance | Übereinstimmung Inhalt ↔ Prompt/Task | Expert-Annotation (Clarke & Dietz 2024) |

### 4.2 Information Quality (IQ)
| Code | Name | Operationalisierung | Messmethode |
|------|------|---------------------|-------------|
| `IQ1` | Factuality | Halluzinationen, falsche Behauptungen | Human-Annotation; Fakten-Verifikation gegen Quellen |
| `IQ2` | Bias / Subjectivity | Über-/Unterausstattung mit subjektiven Markern | Wiebe-Lexikon (2004) |

### 4.3 Style Quality (SQ)
| Code | Name | Operationalisierung | Messmethode |
|------|------|---------------------|-------------|
| `SQ1` | Repetition | Lexikale Wiederholung | Shaib et al. 2024a |
| `SQ2` | Templatedness | Syntaktische POS-Templates | Shaib et al. 2024b |
| `SQ3` | Coherence | Logischer Fluss, Argumentstruktur | Expert-Annotation (Li et al. 2024) |
| `SQ4` | Fluency | Sprachliche Natürlichkeit | Mensch oder Perplexity |
| `SQ5` | Verbosity | Satz-/Passagenlänge | Zhang et al. 2024 |
| `SQ6` | Word Complexity | Unnötig komplexes Vokabular | Gunning-Fog; Flesch-Kincaid |
| `SQ7` | Tone | Über-Formalität, Pathos-Übermass | Fanous et al. 2025; Yang et al. 2024 |

**Empirische Befunde (Shaib et al. 2025):**
- Stärkste Slop-Prädiktoren über alle Domänen: `IU2 Relevance` (β̂=0.06), `IU1 Density` (β̂=0.05), `SQ7 Tone` (β̂=0.05).
- News-Artikel: Kohärenz, Ton, Dichte, Relevanz, Bias dominant.
- QA-Aufgaben: Faktualität, Struktur dominant.
- Binäre Slop-Urteile haben *moderate Subjektivität* (Cohen's κ -0.15 bis 0.29); fein-granulare Codes erreichen 0.51–0.76 (AC1) für Factuality, Bias, Structure.

---

## 5. Makro-Dimensionen (7Vs nach Madsen & Puyt 2025) [8]

| Dimension | Definition | Beispiel-Metrik |
|-----------|------------|-----------------|
| `Volume` | Produktionsskala | Items pro Tag/Plattform |
| `Velocity` | Generierungs- und Zirkulationsgeschwindigkeit | Latenz Prompt → Publish |
| `Variety` | Spannweite an Formen/Genres | Modalitäts-Coverage |
| `Value` | Erosion kulturellen/epistemischen Werts | Trust-Surveys; Citation-Quality |
| `Verification` | Wahrheits- und Vertrauensproblem | Fact-Check-Rate |
| `Visibility` | Algorithmische Verstärkung | Recommendation-Anteil |
| `Virality` | Memetische Diffusion | Reproduktionsrate R |

Die 7Vs ergänzen die Qualitäts-Taxonomie (Abschnitt 4) um *Systemeigenschaften* der Slop-Ökologie statt Eigenschaften des Einzel-Inhalts.

---

## 6. Detection-Techniken (22 Verfahren)

Aus der konsolidierten AI-Slop-Detection-Heuristik (40+ Techniken; v1.0). Wichtigste Klassen:

### 6.1 Text
1. **Repetition Ratio**: `most_common_token / total_tokens` > 0.20 → HIGH; > 0.30 → CRITICAL.
2. **Buzzword Detection** (14 Begriffe): *delve, realm, tapestry, landscape, unleash, unlock, harness, leverage, paradigm, synergy, robust, cutting-edge, state-of-the-art, game-changing*.
3. **Template-Phrase-Detection**: "it's important to note", "in conclusion", "to sum up", "furthermore", "moreover", "as previously mentioned".
4. **Punctuation Anomalies**: Em-dash > 0.5/Satz, Ellipsis > 0.3/Satz, "!" > 0.2/Satz.
5. **Information Density**: `unique_words / total_words` < 0.40 → verbose Slop.
6. **Perplexity Distribution**: ungewöhnlich gleichmässige/niedrige Perplexity-Verteilung.

### 6.2 Code
7. **Hallucinated Package Check**: Abgleich gegen Registry (PyPI, npm) oder Liste bekannter Halluzinationen.
8. **Fabricated Function Detection**: AST-Parse → API-Existenz prüfen.
9. **Hardcoded Secret Patterns**: Regex auf API-Keys, Secrets, Tokens.
10. **Inverted Boolean Logic / Off-by-One**: statische Analyse.

### 6.3 Image
11. **Variance Analysis**: Pixel-Varianz extrem niedrig/hoch.
12. **Symmetry Anomaly**: Linke/rechte Hälfte ≈ identisch (ausser bei Gesichtern/Architektur).
13. **Anatomical Artifacts**: Finger-Anomalien (>5 oder fused), Gesichtsverzerrungen.
14. **Physical Impossibility**: Falsche Schatten/Reflexionen/Perspektive.

### 6.4 Multimodal
15. **Cross-Modal Consistency**: Bild ↔ Caption; Code ↔ Doku; Video ↔ Audio.
16. **Watermark Detection**: provider-spezifisch (SynthID, C2PA).

### 6.5 Statistisch / ML-basiert
17. **DetectGPT** (Mitchell et al. 2023): Curvature-basierte Wahrscheinlichkeits-Diskriminierung.
18. **Binoculars** (Hans et al. 2024): Zero-shot LLM-Detection (AUROC ~0.95).
19. **NewsGuard × Pangram Labs**: Domain-Scale Detection für Content-Farmen (3.006+ Sites identifiziert, März 2026).
20. **Pangram Labs Models**: Proprietäres Detector-Modell für ganze Websites.

### 6.6 Strukturell
21. **Lists-as-Responses**: übermässige Bullet-Strukturen ohne Substanz.
22. **Trailing-Moral / Generic-Closing Patterns**: künstliche "In summary"-Klammern.

**Slop-Score-Aggregation** (Noisy-OR über severity-gewichtete Signale; seit v1.2.0 — die frühere Mittelwert-Formel verwässerte akkumulierende Evidenz):
```
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, 1 − Π (1 − weights[s.severity] * s.confidence))
is_slop = (slop_score ≥ 0.4) OR (any critical) OR (≥ 2 high severity)
```

---

## 7. Schäden / Harms (taxonomisch)

| Schadenstyp | Mechanismus | Belegquelle |
|-------------|-------------|-------------|
| **Model Collapse** | Rekursives Training auf KI-Output → Verlust der Verteilungs-Tails, gibberish-Konvergenz | Shumailov et al. 2024 [11]; Borji 2024 [12] |
| **Epistemische Verschmutzung** | Polluierte Informationsökologie, LLMs zitieren UAINs als Quellen | NewsGuard Aug 2025 [13]; EDMO [14] |
| **Mis-/Disinformation** | Staatlich oder kommerziell gesteuerte False-Claim-Operationen | US Treasury Dec 2024; Storm-1516; Freedom House 2025 [15] |
| **Vertrauenserosion** | "Liar's dividend"; Schwierigkeit, echt von gefälscht zu trennen | Koebler 404 Media [16] |
| **Workplace-Produktivitätsverlust** | "Workslop" lädt kognitive Last auf Empfänger ab; 40 % Beschäftigte betroffen; ~1h 56min Rework pro Instanz | Niederhoffer et al. HBR 2025 [17] |
| **Creator-Squeeze** | Algorithmen unterscheiden nicht zwischen Original und Fake-Bulk → Original wird verdrängt | Scientific American [10] |
| **Schaden an Kindern** | ~40 % YouTube-Kids-Empfehlungen sind Slop (NYT Mar 2026); falsche Informationen, gefährliches Verhalten | NYT 2026 [18]; The 74 / Mother Jones |
| **Ad-Fraud / Brand Safety** | 141 Blue-Chip-Marken werben unwissentlich auf Content-Farmen | NewsGuard/AdWeek 2026 [19] |
| **Kognitive Last** | Konstante "Ist das echt?"-Überprüfung erschöpft Aufmerksamkeit | Koebler "Your AI Use Is Breaking My Brain" 2026 [20] |
| **Umweltkosten** | Strom- und Wasserverbrauch generativer Modelle | Crawford "Eating the Future" [21] |
| **Demokratie-Risiko** | Wahlbeeinflussung, deepfake-endorsements (Taylor Swift / Trump 2024) | Wikipedia [4]; Freedom on the Net 2025 |
| **Royalty-Fraud** | KI-Tracks zur Streaming-Royalty-Manipulation (Smith-Fall 2024) | DOJ; Wikipedia [4] |

---

## 8. Verwandte Konzepte (Beziehungs-Graph)

```
AISlop
├── isAnalogousTo
│   ├── Spam (E-Mail-Analog; explizit von Willison gewählt)
│   ├── Kitsch (München 1860er; ästhetisches Analog)
│   ├── GrubStreet (London 1700er; ökonomisches Analog)
│   ├── Churnalism (rewritten press releases)
│   └── Clickbait
├── isSubtypeOf
│   ├── SyntheticMedia
│   ├── DigitalPollution
│   └── EpistemicPollution
├── isCausedBy
│   ├── AttentionEconomy (Creator-Bonus-Programme)
│   ├── ZeroMarginalCostGeneration
│   ├── AlgorithmicRecommendation
│   └── LowEntryBarrier (Prompt-only Workflow)
├── coOccursWith
│   ├── ModelCollapse                       (kausal verkoppelt)
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

## 9. Empirische Schlüsselzahlen (Stand Juli 2026)

| Metrik | Wert | Quelle |
|--------|------|--------|
| Anteil AI-Inhalte in Google-Suchergebnissen | 19 % (Jan 2025); 7 % (Vorjahr) | [22] |
| Anteil AI-Footprint in neuen Web-Artikeln | > 50 % (Graphite); 74 % (Studien) | [22] |
| AI-Content-Farm-Sites (NewsGuard) | 3.749 (23. Juni 2026); 3.006 (März 2026) | [19][24] |
| AI-Musik-Anteil an Deezer-Neu-Uploads | 44 % (~75.000 Tracks/Tag, Apr 2026); nur 1–3 % der Streams, ~85 % davon als Fraud demonetarisiert | [25] |
| Spotify: entfernte Spam-Tracks | 75 Mio.+ (12 Monate bis Sep 2025) | [25] |
| Organization Science: Submissions seit ChatGPT | +42 %; Lesbarkeit −1,28 SD; >30 % der Peer-Reviews KI-beteiligt | [26] |
| curl Bug-Bounty: AI-Slop-Anteil | ~20 % der Reports (Mitte 2025); Confirmed-Rate <5 %; Programm-Ende Feb 2026 | [27] |
| Neue Content-Farm-Sites pro Monat | 300–500 | [19] |
| YouTube-Empfehlungen Slop für Neu-User | 21–33 % (Kapwing 2025) | [23] |
| YouTube-Kids Slop-Anteil | ~40 % (NYT März 2026) | [18] |
| Workslop-Empfänger | 40 % der Beschäftigten | [17] |
| Workslop-Rework-Zeit pro Instanz | ~1h 56min | [17] |
| AI-Content-Farm-Brands (Werbung) | 141 Blue-Chip-Marken (2 Monate) | [19] |
| Sprachen mit UAINs | 16 (Arabisch bis Türkisch) | [24] |

---

## 10. Machine-Readable Block (YAML)

```yaml
ontology:
  id: ai-slop-ontology
  version: 1.1.0
  date: 2026-07-10
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
      subtypes: [ArticleSlop, BookSlop, RecipeSlop, AcademicSlop, PeerReviewSlop, SecurityReportSlop, ProductReviewSlop, Workslop]
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
    aggregation: noisyOR  # slop_score = 1 - product(1 - w(sev) * conf)
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
      knownCount: 3749
      countDate: 2026-06-23
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

## 11. Anwendungs-Hooks für Agenten

```python
# Pseudo-Interface
def classify_content(content, modality) -> SlopAssessment:
    """Returns: {slop_score, is_slop, dimensions, harms, actor_hypothesis}"""

def route_by_harm(assessment) -> Action:
    """Block | Refine | Flag | Pass"""

def update_ontology(new_evidence) -> None:
    """Extend with new actor patterns, harm types, detection methods"""
```

**Empfohlene Integration:** LangGraph-Node, MCP-Tool, AutoGen-Function (vgl. Skill `ai-slop-detection` v1.0).

---

## 12. Limitationen und offene Fragen

- **Subjektivität binärer Slop-Urteile**: Cohen's κ -0.15 bis 0.29 (Shaib et al. 2025) → binäre Klassifikation ist umstritten; dimensionale Bewertung ist robuster.
- **Reflexivität**: Detection-Heuristiken werden bekannt → Producer adaptieren ("humanized" Variants).
- **Falsch-Positive bei menschlichem Text**: Texte können auch ohne KI-Beteiligung als Slop erscheinen (z. B. Templatierter Journalismus, Boilerplate-Kontent).
- **Kontextabhängigkeit**: Technische Dokumentation darf Wiederholungen für Klarheit nutzen.
- **Sprachliche Verzerrung**: Detection ist auf Englisch am stärksten trainiert; geringer in Sprachen mit weniger Trainingsdaten (Hindi, Vietnamesisch, Urdu) – just dort, wo viel Slop entsteht.
- **Sich entwickelnde Modelle**: Neue Modellgenerationen erzeugen neue Slop-Muster; Ontologie braucht regelmässige Updates.
- **Philosophische Kritik** (Puliafito; The Philosophical Salon): "Slop" beschreibt Mediokrität – aber Mediokrität ist die Basislinie aller Kulturproduktion, nicht KI-spezifisch [21].

---

## 13. Quellenverzeichnis / References

### Lexikographische Primärquellen
[1] Merriam-Webster (2025). *Word of the Year 2025: "Slop"*. Definition: "digital content of low quality that is produced usually in quantity by means of artificial intelligence." PBS News, 15 Dec 2025. https://www.pbs.org/newshour/nation/merriam-websters-word-of-the-year-for-2025-is-ais-slop

[2] Oxford University Press (2024). *Word of the Year 2024 Shortlist: "Slop"*. https://corp.oup.com/word-of-the-year/#shortlist-2024 (+332 % Nutzungswachstum).

### Etymologische / Popularisierende Quellen
[3] Willison, S. (8 May 2024). *GPT-4o, a new version of LLM and more thoughts on slop*. Personal blog. https://simonw.substack.com/p/gpt-4o-a-new-version-of-llm-and-more — kanonische Spam-Analogie.

[4] Wikipedia contributors (Stand Mai 2026). *AI slop*. https://en.wikipedia.org/wiki/AI_slop

[5] Wikipedia contributors (Stand Mai 2026). *Model collapse*. https://en.wikipedia.org/wiki/Model_collapse

[6] @deepfates (Anfang 2024). X / Twitter. "the term for unwanted AI generated content".

### Akademische Kern-Papers
[7] Shaib, C., Chakrabarty, T., Garcia-Olano, D., & Wallace, B. C. (2025/2026). *Measuring AI "Slop" in Text*. arXiv:2509.19163v2. https://arxiv.org/abs/2509.19163 — operationale Taxonomie (3 Themen, 11 Codes), 213 News-Artikel + 123 QA-Passagen, Annotation Guide & Daten: https://github.com/cshaib/slop

[8] Madsen, D. Ø., & Puyt, R. W. (2 Oct 2025). *The 7Vs of AI Slop: A Typology of Generative Waste*. SSRN 5558018. https://ssrn.com/abstract=5558018 (DOI 10.2139/ssrn.5558018)

[9] MINT Lab (Johns Hopkins / ANU, 2025/26). *AI Slop: Definitions and Normative Status*. https://mintresearch.org/reports/ai-slop/

[10] *Why Slop Matters* (Feb 2026). arXiv:2601.06060. https://arxiv.org/html/2601.06060v1 — Tasks für formale, soziologische, ethische Slop-Forschung.

### Model Collapse
[11] Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. *Nature* 631, 755–759. DOI 10.1038/s41586-024-07566-y. https://www.nature.com/articles/s41586-024-07566-y

[12] Borji, A. (Oct 2024). *A Note on Shumailov et al. (2024)*. arXiv:2410.12954. https://arxiv.org/abs/2410.12954 — KDE-basierte Verifikation, statistische Unvermeidbarkeit.

Weitere: Alemohammad et al. (2023) "Self-Consuming Generative Models Go MAD"; Gillman et al. (2024) "Self-Correction Mechanisms Stabilize Recursive Loops"; IBM (2026) *What is Model Collapse?* https://www.ibm.com/think/topics/model-collapse

### Investigativer Journalismus (Schlüsselfälle)
[13] NewsGuard AI False Claim Monitor (Aug 2025). https://www.newsguardtech.com/ai-monitor/august-2025-ai-false-claim-monitor/

[14] European Digital Media Observatory (EDMO). Reports zu KI in der Informationsökologie.

[15] Freedom House (2025). *Freedom on the Net 2025: AI and Influence Operations*. US Treasury sanctions Dec 2024 (Storm-1516).

[16] Koebler, J. (404 Media, 2023–2026). AI-Slop-Reporting-Serie:
   - *Facebook Is Being Overrun With Stolen, AI-Generated Images* (Dec 2023)
   - *Facebook Is the 'Zombie Internet'* (May 2024)
   - *Where Facebook's AI Slop Comes From* (Aug 2024). https://www.404media.co/where-facebooks-ai-slop-comes-from/
   - Tag-Übersicht: https://www.404media.co/tag/ai-slop/

[20] Koebler, J. (11 May 2026). *Your AI Use Is Breaking My Brain*. 404 Media.

### Workplace
[17] Niederhoffer, K., Rosen Kellerman, G., Lee, A., Liebscher, A., Rapuano, K., & Hancock, J. T. (22 Sep 2025). *AI-Generated "Workslop" Is Destroying Productivity*. Harvard Business Review. https://hbr.org/2025/09/ai-generated-workslop-is-destroying-productivity — n=1.150 US-Vollzeit-Beschäftigte; 40 % erhalten Workslop; ~1h 56min Rework pro Instanz.

Niederhoffer et al. (Jan 2026). *Why People Create AI "Workslop"—and How to Stop It*. HBR. https://hbr.org/2026/01/why-people-create-ai-workslop-and-how-to-stop-it

### Kinder / Vulnerable Groups
[18] New York Times Investigation (March 2026). YouTube Kids ~40 % Slop. (Berichtet in Wikipedia [4]; The 74; Mother Jones.)

### Industrie-Tracker
[19] NewsGuard × Pangram Labs (12 March 2026). *Real-time AI Content Farm Detection Datastream*. https://www.newsguardtech.com/press/newsguard-launches-real-time-ai-content-farm-detection-datastream-to-counter-onslaught-of-ai-slop-in-news/ — 3.006 Content-Farmen identifiziert; 141 Blue-Chip-Marken werben unwissentlich.

[24] NewsGuard *AI Tracking Center*. https://www.newsguardtech.com/special-reports/ai-tracking-center/ — UAINs in 16 Sprachen.

### Plattform- und Sektor-Reports
[22] Graphite Research / Entrepreneur Loop (2025/26). AI-Footprint > 50 % bei neuen Web-Artikeln. https://entrepreneurloop.com/what-is-ai-slop-growing-problem-explained/

[23] Kapwing × The Guardian (2025). YouTube-Empfehlungen 21–33 % AI/Brainrot.

### Konzeptuelle / Philosophische Kritik
[21] Crawford, K. *Eating the Future* (zitiert in The Philosophical Salon); Puliafito, A. *Slow News*. *The Idea of "AI Slop" Is Slop*, The Philosophical Salon, Dec 2025. https://thephilosophicalsalon.com/the-idea-of-ai-slop-is-slop/

### Begriffsgeschichtliche Einordnung
Scientific American (Nov 2025). *AI Slop—How Every Media Revolution Breeds Rubbish and Art*. https://www.scientificamerican.com/article/ai-slop-how-every-media-revolution-breeds-rubbish-and-art/ — Grub-Street-Analogie.

### Detection-Forschung
- Mitchell, E. et al. (2023). *DetectGPT: Zero-Shot Machine-Generated Text Detection*. ICML.
- Hans, A. et al. (2024). *Spotting LLMs With Binoculars*. ICML 2024 (AUROC ~0.95).
- Russell et al. (2025). *Indicators of AI-written text*. (Referenziert in Shaib et al. 2025.)
- Chakrabarty et al. (2024, 2025a, 2025b). Editing-Taxonomien für AI-Writing.

### Neu in v1.1.0 (Juli 2026)
[25] Deezer Newsroom (20 Apr 2026). *AI-generated tracks represent 44% of new uploaded music* (~75.000 Tracks/Tag; 1–3 % der Streams; ~85 % davon Fraud). https://newsroom-deezer.com/2026/04/ai-generated-tracks-represent-44-of-new-uploaded-music/ — Detektor für Fremdkataloge seit 11 Jun 2026 (TechCrunch). Spotify: 75 Mio.+ Spam-Tracks entfernt (12 Monate bis Sep 2025).

[26] Organization Science Editorial-Studie (2026). *More Versus Better: Artificial Intelligence, Incentives, and the Emerging Crisis in Peer Review*. https://pubsonline.informs.org/doi/10.1287/orsc.2026.ed.v37.n3 — ~7.000 Submissions / 10.000+ Reviews (2021–2026), Pangram-Detection; +42 % Submissions, Flesch Reading Ease −1,28 SD, >30 % KI-beteiligte Reviews. Vgl. Forbes (30 Apr 2026).

[27] Stenberg, D. (14 Jul 2025). *Death by a thousand slops*; (26 Jan 2026). *The end of the curl bug-bounty*. https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/ — ~20 % AI-Slop-Reports, Confirmed-Rate <5 %, HackerOne-Programm beendet Feb 2026. → Klasse `SecurityReportSlop`.

[28] Nishal, S., Sax, M., & Kieslich, K. (10 Jun 2026). *Why AI Slop Matters, but Not Like That*. arXiv:2606.12285 / ACM AI Letters. https://arxiv.org/abs/2606.12285 — soziotechnische Kritik an Kommers et al. [10]; fordert kontextuelle, kulturell verankerte Slop-Forschung.

[29] Sem-Detect (2026). *Semantic Level Detection of AI Generated Peer-Reviews*. arXiv:2605.21713. https://arxiv.org/pdf/2605.21713 — Detection-Methode für `PeerReviewSlop`.

[30] ANU / PNAS (2026). Trainierbarkeit menschlicher AI-Gesichtserkennung via Hyper-Typikalität ("more typical than real faces"); near-perfect Accuracy nach Kurztraining. Berichtet: Gizmodo. — Neues Image-Signal `HyperTypicality`.

[31] Keisha, F., Wu, Z., Wang, Z., Koshiyama, A., & Treleaven, P. (2025). *Knowledge Collapse in LLMs: When Fluency Survives but Facts Fail under Recursive Synthetic Training*. arXiv:2509.04796; NeurIPS 2025 Workshop. — 3-Stadien-Modell (A: Preservation, B: "Confidently Wrong", C: Instruction Collapse); domänenspezifisches Training verzögert Accuracy-Zerfall um 15×.

Weitere: Science-Editorial *Resisting AI slop* (2026, DOI 10.1126/science.aee8267); Ansari (SSRN 5649410) *AI Slop and Data Pollution*; NTIRE 2026 Challenge (arXiv:2604.11487) zur Robustheit von AI-Bild-Detektoren; NewsGuard AI Tracking Center (23 Jun 2026): 3.749 Content-Farmen [24].

### Quellen-Hub
- Simon Willison's `slop`-Tag-Übersicht: https://simonwillison.net/tags/slop/ — laufender Curation-Stream seit 2024.

---

## 14. Versions- und Update-Hinweise

| Version | Datum | Änderung |
|---------|-------|----------|
| 1.0.0 | 2026-05-20 | Initial release; konsolidiert Shaib et al. 2025, Madsen & Puyt 2025, Shumailov et al. 2024, 22 Detection-Techniken, 12 Harm-Klassen, 16 verwandte Konzepte. |
| 1.1.0 | 2026-07-10 | Neue Klassen `SecurityReportSlop` (curl-Fall) und `PeerReviewSlop` (Organization Science); neues Image-Signal `HyperTypicality` (PNAS 2026); Schlüsselzahlen aktualisiert (NewsGuard 3.749; Deezer 44 %; Spotify 75 Mio.); 7 neue Referenzen [25]–[31]; alle Kernzitate verifiziert (Shaib arXiv:2509.19163, Madsen & Puyt SSRN 5558018, Kommers arXiv:2601.06060, Keisha arXiv:2509.04796). |
| 1.2.0 | 2026-07-10 | Evaluations-Korpus (53 gelabelte Beispiele, 7 Sprachen) + Benchmark; Gewichts-Kalibrierung (Skill-Pipeline F1 0,47 → 0,98 bei Precision 1,0); Noisy-OR-Aggregation statt Mittelwert (Evidenz akkumuliert); neue Phrasen-Kategorie `authority_claims`; Sprachen Hindi/Vietnamesisch/Urdu ergänzt (§12-Lücke); TTL synchronisiert + Konsistenz-Checker in CI; Engine-Paritätstests. |

**Empfohlener Update-Rhythmus:** Quartal (neue Modellgenerationen → neue Slop-Patterns); ad-hoc bei grossen NewsGuard-Updates oder neuen akademischen Taxonomien.

**Contributions willkommen:** Erweiterungen zu Audio-Slop (unterforscht), nicht-westlichen Plattformen (TikTok/Douyin, KakaoTalk, WhatsApp), und systematischer Cross-modal-Detection.
