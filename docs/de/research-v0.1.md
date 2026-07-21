# Deep Research: AI Slop Ontologie v0.1

## Arbeitsdefinition

**AI Slop ist nicht einfach "KI-generierter Content"**, sondern niedrigwertiger, oft massenhaft produzierter synthetischer oder KI-assistierter Content, der oberflächlich plausibel wirkt, aber wenig Substanz, Originalität, Sorgfalt, Wahrheitsprüfung oder echten Nutzen bietet.

- **Merriam-Webster:** Digitale Inhalte niedriger Qualität, meist in Menge und per KI erzeugt
- **American Dialect Society:** "Low-quality, high-quantity content" (KI-Kontext inzwischen oft implizit)

**Der wichtigste Punkt für eine Agenten-Ontologie:** AI Slop ist **kein binärer Medientyp, sondern ein Risikoprofil**. Ein Inhalt kann KI-generiert und hochwertig sein. Umgekehrt kann menschlicher Spam ebenfalls wertlos sein. "Slopness" entsteht aus der **Kombination** von:
- Synthetischer Erzeugung
- Geringer menschlicher Sorgfalt
- Massenskalierung
- Manipulativer Distribution
- Schwacher Provenienz
- Qualitätsmängeln

Forschung zu "Measuring AI Slop in Text" beschreibt Slop-Urteile als teils subjektiv, aber korreliert mit Dimensionen wie Kohärenz und Relevanz. Spotify formuliert für Musik: KI-Nutzung ist ein **Spektrum**, kein simples "AI / not AI"-Binary.

---

## 1. Zentrale Erkenntnisse

### 1.1 AI Slop ist eine neue Form von Spam, aber nicht identisch mit Spam

Klassischer Spam ist primär unerwünschte Distribution. AI Slop ergänzt das um:
- **Billige Generierung** — Produktionskosten ~0€
- **Semantische Oberflächlichkeit** — Wirkt plausibel, ist substanzlos
- **Algorithmische Skalierung** — Optimiert für Plattform-Mechaniken

**Google "Scaled Content Abuse":** Viele Seiten, die primär zur Suchmanipulation und nicht zur Nutzerhilfe erzeugt werden. Explizit eingeschlossen: generative KI-Seiten ohne Mehrwert, Scraping, Stitching und keywordhaltige Seiten ohne Sinn.

### 1.2 Die drei Kernmerkmale eines Prototyps (Kommers et al. 2026)

| Eigenschaft | Beschreibung |
|-------------|-------------|
| **Superficial Competence** | Qualitätsanmutung ohne Tiefe |
| **Effort Asymmetry** | Extrem niedriger Erzeugungsaufwand vs. menschliche Produktion |
| **Mass Producibility** | Einbettung in Ökosysteme der Massenproduktion/-konsumtion |

**Zusätzlich variiert Slop entlang:** Instrumentellem Nutzen, Personalisierung, Surrealismus.

### 1.3 Das Problem ist plattformökonomisch

AI Slop entsteht dort besonders stark, wo Plattformen Aufmerksamkeit, Reichweite, Suchranking oder Royalties belohnen.

| Plattform | Slop-Statistik | Konsequenz |
|-----------|----------------|------------|
| **YouTube** | "Mass-produced or repetitive content" = "inauthentic content" → nicht monetarisierungsfähig | Richtlinie existiert, aber Durchsetzung lückenhaft |
| **Deezer** | ~75.000 KI-Tracks/Tag (Stand 20.04.2026) = **44% der täglichen Uploads** | Die meisten Streams als betrügerisch erkannt und demonetarisiert |
| **Spotify** | KI-Nutzung = Spektrum, nicht binär | Royalty-Multiplication durch Fake-Artists |
| **Facebook** | 24% Nutzer über 55, geringe AI-Literacy | Primäres Opfer von Engagement-Farming |
| **Google** | "Scaled content abuse" explizit in Spam-Policies | SEO-Slop rankt trotzdem durch Volume |

### 1.4 AI Slop gefährdet Agenten besonders über Retrieval ⚠️

**Für Agenten ist AI Slop gefährlich**, weil sie nicht nur Menschen täuscht, sondern **RAG-, Search- und Memory-Systeme kontaminiert**.

**"Retrieval Collapse" — Zwei Stufen:**

| Stufe | Was passiert | Folge |
|-------|-------------|-------|
| **1. Quellendominanz** | KI-generierte Inhalte dominieren Suchergebnisse | Reduzierte Quellendiversität |
| **2. Pipeline-Kontamination** | Minderwertige/adversariale Inhalte dringen in Retrieval-Pipelines ein | Agenten antworten mit Slop |

**Experimenteller Befund:** 67% Pool-Kontamination → über 80% Expositionskontamination.

**Das bedeutet für Agenten-Architektur:** Slop-Resilienz ist kein Optional, sondern ein Kern-Requirement für RAG- und Memory-Systeme.

### 1.5 Langfristig droht Daten- und Modellverschlechterung

**Nature (Shumailov et al. 2024):** "Model Collapse" — degenerativer Prozess bei dem Daten generativer Modelle das Trainingsset späterer Modelle verschütten.

- Modelle verlieren Informationen über die ursprüngliche Verteilung
- Insbesondere **seltene Randbereiche** (Long Tail) gehen verloren
- Echte menschliche Daten bleiben wichtig für Lernaufgaben mit relevanten Verteilungsschwänzen
- Massenhaft veröffentlichter LLM-Content verschmutzt spätere Trainingsdaten

**Knowledge Collapse (3-Stadien-Modell):**

| Stadium | Fakten | Format | Gefahr |
|---------|--------|--------|--------|
| A: Preservation | ✅ Korrekt | ✅ Intakt | Niedrig |
| **B: Collapse** | **❌ Falsch** | **✅ Korrekt** | **KRITISCH — "Confidently Wrong"** |
| C: Instruction Collapse | ❌ Random | ❌ Incoherent | Hoch, aber erkennbar |

---

## 2. Slopness als Risikoprofil (Kernkonzept für die Ontologie)

**Slopness Score = f(Generierung, Sorgfalt, Skalierung, Distribution, Provenienz, Qualität)**

| Dimension | Low Risk (0-2) | Medium Risk (3-5) | High Risk (6-10) |
|-----------|----------------|-------------------|------------------|
| **Generierung** | Menschlich geschrieben | AI-assisted, human-edited | Reines AI, kein Edit |
| **Sorgfalt** | Gründliche Recherche, Testing | Oberflächliche Prüfung | Keine Überprüfung |
| **Skalierung** | Einzelner Artikel | Serie, kuratiert | Massenproduktion (100+/Tag) |
| **Distribution** | Organisch, zielgerichtet | SEO-optimiert | Clickbait, Engagement Farming |
| **Provenienz** | Klare Autorschaft, Quellen | Teilweise Quellen | Fake-Autor, keine Quellen |
| **Qualität** | Originell, informativ | Generisch, teils nützlich | Substanzlos, repetitiv |

**Key Insight:** Nicht alles AI ist Slop. Der Unterschied liegt in der Kombination der Dimensionen.

---

## 3. Taxonomie (erweitert)

### 3.1 Nach Purpose

| Purpose | Beschreibung | Beispiele |
|---------|-------------|-----------|
| **Engagement/Clickbait** | Virales Potenzial | Veteran Birthday, Shrimp Jesus |
| **SEO/Content Farm** | Keyword-stuffed für Ads | "10 Ways to Leverage AI" |
| **Propaganda/Disinfo** | Politisch motiviert | Trump-Papst, Spamouflage |
| **Monetization** | Direkte Revenue | Facebook Bonuses, Fake Shops |
| **Spam/Noise** | Füllmaterial | Kein klarer Zweck |
| **Supply Chain Attack** | Slopsquatting | Hallucinated packages (19.7% Rate) |

### 3.2 Nach Form

| Achse | Low | High |
|-------|-----|------|
| Surrealismus | Banal-realistisch | Absurd (Shrimp Jesus) |
| Personalisierung | Mass | Personalized |
| Human Oversight | Reines AI | AI-assisted + Edits |

### 3.3 Nach Risikoprofil für Agenten ⚠️ NEU

| Risikostufe | Beschreibung | Agent-Verhalten |
|-------------|-------------|----------------|
| **🟢 Clean** | Menschlich, geprüft, mit Quellen | Normal verwenden |
| **🟡 AI-Assisted** | AI-generiert, aber human-edited, nützlich | Mit Quellenangabe verwenden |
| **🟠 Suspicious** | AI-generiert, keine Quellen, generisch | Verifizieren vor Verwendung |
| **🔴 Slop** | AI-generiert, substanzlos, massenhaft | **Nicht in RAG/Memory aufnehmen** |
| **⚫ Malicious** | Slop + Absicht (Disinfo, Slopsquatting) | **Blockieren + Warnen** |

---

## 4. Retrieval Collapse — Das Agenten-spezifische Problem ⚠️

### 4.1 Das Problem

```
User Question → Agent → RAG/Search → [Slop-contaminated Results] → Slop-Answer
                                     ↑
                              67% Pool-Kontamination
                              → 80%+ Expositionskontamination
```

### 4.2 Abwehrmaßnahmen für Agenten

| Maßnahme | Beschreibung | Implementierung |
|----------|-------------|----------------|
| **Source Diversity Check** | Min. 3+ unterschiedliche Quellen | `len(set(source_domains)) >= 3` |
| **Slop Score Gate** | Nur Quellen mit Score < 0.4 aufnehmen | `slop_score(doc) < 0.4` |
| **Provenance Filter** | Bevorzuge menschlich verifizierte Quellen | Source-Attribution, Peer Review, Edit History |
| **Recency vs. Authority** | Neu ≠ Besser. Ältere etablierte Quellen bevorzugen | Domain Authority Score |
| **Contamination Detection** | Erkennen wenn Suchergebnisse Slop-dominated | Information Diversity der Top-10 Ergebnisse prüfen |
| **Cross-Validation** | Facts gegen unabhängige Quellen prüfen | Min. 2 unabhängige Bestätigungen |

---

## 5. Slopsquatting — Code-Slop als Security-Threat

| Statistik | Wert |
|-----------|------|
| Halluzinationsrate gesamt | 19.7% |
| Open-Source Modelle | 21.7% |
| GPT-4 Turbo | 3.59% |
| CodeLlama | >33% |
| Einzigartige halluzinierte Namen | 205,000+ |

**Reale Vorfälle:** huggingface-cli (30K+ Downloads), react-codeshift (237 Repos), unused-imports (Malware)

---

## 6. Plattform-Statistiken (2026)

| Metrik | Wert | Quelle |
|--------|------|--------|
| Deezer AI-Tracks/Tag | ~75.000 (44% der Uploads) | Deezer 20.04.2026 |
| YouTube AI-Kanäle | 278 (63 Mrd. Views/Jahr) | Research |
| YouTube Kids AI-Anteil | ~40% | Analysis |
| Facebook Nutzer >55 | 24% der Nutzer | Platform Data |
| AI-Package-Halluzination | 19.7% der Empfehlungen | USENIX 2025 |
| Pinterest Slop-Account | 8.6M Monthly Views (Einzelfall) | Futurism |

---

## 7. Quellen & Referenzen

1. Kommers et al. (2026): "Why Slop Matters" — ACM AI Letters (arXiv: 2601.06060)
2. Shaib et al. (2025): "Measuring AI Slop in Text" (arXiv: 2509.19163)
3. Shumailov et al. (Nature 2024): "AI models collapse when trained on recursively generated data"
4. Keisha et al. (NeurIPS 2025): "Knowledge Collapse in LLMs" (arXiv: 2509.04796)
5. USENIX Security 2025: "We Have a Package for You!" — Package Hallucination Study
6. "Retrieval Collapse" — RAG Contamination Research
7. Google Spam Policies: "Scaled Content Abuse"
8. Deezer AI Content Report (20.04.2026): 75K tracks/day
9. Spotify AI Policy: KI-Nutzung als Spektrum
10. Carrigan (2026): "Engagement Farming" Essay
11. Futurism: Cunningham Slop Farmer Exposé
12. MINT Lab (2026): "AI Slop: Definitions and Normative Status"
13. Wikipedia: "AI slop"
14. Merriam-Webster: Word of the Year 2025
