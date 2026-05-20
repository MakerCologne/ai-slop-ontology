# Ontologische Grundentscheidung

## Falsches Modell ❌

```
AIContent = Slop
HumanContent = NotSlop
```

## Richtiges Modell ✅

```
ContentItem
  ├── hasGenerationMode        (human, ai_assisted, synthetic)
  ├── hasHumanOversightLevel   (full, partial, minimal, none)
  ├── hasQualityProfile        (density, coherence, originality, factuality)
  ├── hasDistributionPattern   (organic, seo_optimized, engagement_farmed, adversarial)
  ├── hasIntent                (inform, monetize, manipulate, fill)
  ├── hasProvenanceStatus      (verified, unverified, fake_author, spoofed)
  ├── hasRiskProfile           (clean, ai_assisted, suspicious, slop, malicious)
  └── hasSlopScore             (0.0 – 1.0)
```

**AI Slop als abgeleitete Klasse / Score-basierte Klassifikation:**

```
AI_Slop ≈ ContentItem
    AND synthetic_or_ai_assisted
    AND low_quality_or_low_substance
    AND low_effort_or_low_verification
    AND mass_produced_or_engagement_optimized_or_deceptively_distributed
```

---

## Top-Level-Klassen

| Klasse | Bedeutung |
|--------|-----------|
| **ContentItem** | Einzelner Inhalt: Text, Bild, Video, Audio, Code, Dokument, Listing, Kommentar |
| **SyntheticContent** | Inhalt ganz oder teilweise durch generative KI erzeugt |
| **AI_AssistedContent** | Menschlicher Inhalt mit KI-Hilfe (Recherche, Entwurf, Editing) |
| **AI_SlopCandidate** | Inhalt mit Slop-Verdacht |
| **ConfirmedAI_Slop** | Inhalt mit ausreichender Evidenz für Slop-Klassifikation |
| **LowQualityHumanContent** | Schlechter menschlicher Content, aber nicht zwingend AI Slop |
| **SpamContent** | Unerwünschter oder manipulativer Content unabhängig von KI |
| **MisinformationContent** | Inhalt mit falschen oder irreführenden Behauptungen |
| **SyntheticMedia** | Bild, Video, Audio oder multimodaler synthetischer Inhalt |
| **SlopProducer** | Account, Bot, Content Farm, SEO-Cluster, Channel, Uploader |
| **DistributionChannel** | Plattform, Suchmaschine, Feed, Marketplace, RAG-Korpus |
| **DetectionEvidence** | Hinweise: Metadaten, Artefakte, Wiederholungsmuster, Halluzinationen |
| **MitigationAction** | Labeln, Demonetarisieren, Downranken, Ausschließen, Human Review |

---

## Taxonomie nach Medium

### Text Slop
**Beispiele:** Blogartikel, LinkedIn-Posts, SEO-Seiten, Produktbeschreibungen

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Generische Struktur | Immer gleicher Aufbau: Einleitung → Liste → Fazit |
| Wenig Quellen | Keine oder nur generische Verweise |
| Floskeln | "In today's fast-paced world", "it's important to note" |
| Falsche Fakten | Hallucinations, fabriquierte Statistiken |
| Em-Dash Overuse | Übermäßige "—" Nutzung |
| Low Density | unique_words / total_words < 0.40 |

### Image Slop
**Beispiele:** Fake-Historienbilder, virale Tiere, Produktbilder

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Anatomische Fehler | Extra Limbs, verschmolzene Finger |
| Surrealer Realismus | Zu perfekt, uncanny valley |
| Kontextbruch | Elemente die nicht zusammenpassen |
| Bad Text Rendering | Kauderwelsch im Bild |
| Glossy Textures | Unnatürlich glatte Oberflächen |

### Video Slop
**Beispiele:** YouTube-Kindercontent, KI-News, Fake-Dokus

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Repetitive Szenen | Gleiche Sequenzen wiederholt |
| KI-Voiceover | Synthetische Stimme ohne emotionale Variation |
| Keine echte Dramaturgie | Ablauf ohne Spannungsbogen |
| Frame Flicker | Inkonsistenzen zwischen Frames |
| Lip-Sync Mismatch | Audio-Visual Desynchronisation |

### Audio Slop
**Beispiele:** AI-Musik, Voice-Clones, Podcast-Fakes

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Massen-Uploads | Hunderte Tracks gleichzeitig |
| Generische Komposition | Formelhafte Song-Struktur |
| Identitätsmissbrauch | Fake-Artist-Profile |

### Academic Slop ⚠️ Besonders gefährlich
**Beispiele:** Paper, Preprints, Review-Artikel

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Fake Citations | Halluzinierte Referenzen |
| Oberflächliche Literaturübersichten | Rehash ohne Analyse |
| Template-Struktur | Immer gleicher Aufbau |
| Uneditierter Prompt-Text | Direkte LLM-Outputs |

**arXiv verschärfte 2026 Regeln** gegen offensichtlich unvalidierte LLM-Inhalte wie halluzinierte Referenzen oder uneditierten Prompt-Text.

**NeurIPS-2025-Fabricated-Citations:** KI-halluzinierte Zitate nutzen verschiedene Plausibilitätsheuristiken gleichzeitig aus — besonders schwer zu erkennen.

### Code Slop
**Beispiele:** AI-generierte PRs, Issues, Docs

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Kompiliert nicht | Syntaktische Fehler |
| Falsche APIs | Halluzinierte Package-Names (19.7% Rate) |
| Review-Burden | Massenhaft triviale PRs |
| Copy-Paste-Muster | Uniformer Code-Stil |
| Hardcoded Secrets | API Keys im Code |

### Legal Slop ⚠️ Besonders gefährlich
**Beispiele:** KI-generierte Schriftsätze

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Erfundene Präzedenzfälle | Halluzinierte Gerichtsurteile |
| Falsche Normen | Nicht-existente Gesetzesverweise |
| Unvalidierte Zitate | Quellen die nicht existieren |

### Work Slop
**Beispiele:** Interne Reports, Präsentationen, Memos

| Slop-Marker | Beschreibung |
|-------------|-------------|
| Sieht professionell aus | Oberflächlich überzeugend |
| Spart Senderzeit | Schnell erstellt |
| Kostet Empfängerzeit | Müsssen gelesen/evaluiert werden |

> "Gerade akademische und professionelle Varianten sind gefährlich, weil sie nicht immer 'billig' aussehen."

---

## Taxonomie nach Intent

| Intent-Klasse | Beschreibung | Gefahrenstufe |
|---------------|-------------|---------------|
| **AttentionFarming** | Reichweite, Likes, Watchtime | 🟠 Hoch |
| **AdRevenueFarming** | Monetarisierung über Ads | 🟠 Hoch |
| **RoyaltyDilution** | Streaming-Royalties durch Massenmusik | 🟠 Hoch |
| **SearchManipulation** | SEO, GEO, Ranking-Manipulation | 🔴 Kritisch |
| **RecommendationPoisoning** | Inhalte so platzieren dass KI-Antwortsysteme sie bevorzugen | 🔴 Kritisch |
| **AffiliateFunnel** | KI-Content als Traffic-Funnel | 🟡 Mittel |
| **CredentialInflation** | Paper, Zitate, Profile zur Reputationssteigerung | 🟠 Hoch |
| **Disinformation** | Absichtlich irreführender synthetischer Content | ⚫ Malicious |
| **CarelessSpeech** | Nicht zwingend bösartig, aber ungeprüft, oberflächlich, irreführend | 🟡 Mittel |
| **Impersonation** | Stimme, Stil, Name, Marke oder Person wird imitiert | 🔴 Kritisch |
| **PlaceholderPublishing** | Content wird veröffentlicht obwohl er nur Entwurf/Füllmaterial ist | 🟡 Mittel |

**Google** hat Spamregeln inzwischen auf **Manipulation generativer Suchsysteme** erweitert — betrifft Versuche, AI Overviews oder AI Mode zu beeinflussen.

---

## Klassenhierarchie (Formal)

```
ContentItem
├── hasGenerationMode → GenerationMode
│   ├── Human
│   ├── AI_Assisted
│   └── Synthetic
├── hasHumanOversightLevel → OversightLevel
│   ├── Full (gründliche Recherche + Editing)
│   ├── Partial (Review aber kein Deep-Check)
│   ├── Minimal (Flüchtiger Blick)
│   └── None (direkt veröffentlicht)
├── hasQualityProfile → QualityProfile
│   ├── hasDensity → float (0-1)
│   ├── hasCoherence → float (0-1)
│   ├── hasOriginality → float (0-1)
│   ├── hasFactuality → float (0-1)
│   └── hasUtility → float (0-1)
├── hasDistributionPattern → DistributionPattern
│   ├── Organic
│   ├── SEOOptimized
│   ├── EngagementFarmed
│   ├── Adversarial
│   └── PlatformAmplified
├── hasIntent → Intent
│   ├── Inform
│   ├── Monetize
│   ├── Manipulate
│   └── Fill
├── hasProvenanceStatus → ProvenanceStatus
│   ├── Verified (klare Autorschaft, Quellen)
│   ├── Unverified (keine klare Herkunft)
│   ├── FakeAuthor (AI-Headshot, kein History)
│   └── Spoofed (Identität gefälscht)
├── hasRiskProfile → RiskLevel
│   ├── Clean
│   ├── AI_Assisted
│   ├── Suspicious
│   ├── Slop
│   └── Malicious
└── hasSlopScore → float (0.0-1.0)

AI_SlopCandidate ≡ ContentItem ∧ (synthetic ∨ ai_assisted) ∧ slopScore > threshold
ConfirmedAI_Slop ≡ AI_SlopCandidate ∧ detectionEvidence.count ≥ 2
```

---

## Überlappungen zwischen Klassen

```
              Slop
             /    \
            /      \
     Synthetic    LowQuality
        |    \      /    |
        |     \    /     |
        |   AI_Slop     |
        |                |
   Spam ──────── Misinformation
        \                /
         \              /
          CarelessSpeech
```

**Slop kann Spam sein, aber nicht alles Slop ist Spam.**
**Slop kann Misinformation sein, aber nicht alles Slop ist absichtlich.**
**LowQualityHumanContent ist wertlos aber nicht zwingend Slop.**
