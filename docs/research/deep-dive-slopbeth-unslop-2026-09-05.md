# Deep-Dive: slopbeth (ehmo/slopkit) & unslop (cursor/plugins → pstack)

**Datum:** 2026-09-05 · **Issue:** ai-slop-ontology#39 (Backlog-Sync btm-openclaw-platform#1130)
**Quellen:**
- slopbeth: `ehmo/slopkit` → `skills/slopbeth/SKILL.md` (v1.4.1, skills.sh Rang 5)
- unslop: `cursor/plugins` → `pstack/skills/unslop/SKILL.md` (8.3K Installs, skills.sh Rang 4)

**Korrektur zu Report 1.4:** Der dort ausgewertete `mshumer/unslop` war falsch zugeordnet; gemeint war das cursor/plugins-unslop (Skill-Autor pstack, Pfad `pstack/skills/unslop/SKILL.md`). Die „Cut AI tells" + Soul-Doktrin stammt aus genau diesem SKILL.md; die Soul-Substanz („Have opinions", „Vary rhythm", „Let some mess in") ist als eigenes Issue zu human-voice.md bereits abgetrennt.

---

## 1. Slopbeth (ehmo/slopkit) — Profil

**Typ:** Voll-Rewrite-Skill mit Proof-Infrastruktur (Benchmark-Scripts, Detector-Evidence-Protokoll, False-Positive-Checks). Kein Detector — Ziel ist „dense, specific writing", ausdrücklich **kein** „detector-proof" (Hard Rule: „Never claim text is permanently undetectable").

**Signale (Diagnose-Cluster, SKILL.md Schritt 5):**
| slopbeth-Cluster | Ontology-Abdeckung |
|---|---|
| Filler | ✅ phrases/filler-artige Kategorien, ImportancePuffery |
| Vague significance language | ✅ ImportancePuffery, metaphor_abuse |
| Formulaic contrast | ✅ BinaryContrast |
| Promotional inflation | ✅ puffery-Buzzwords, PromotionSlop-artige typePatterns |
| Padded lists | ✅ NumberedListOveruse, listicle_tells |
| Generic uplift | ✅ tier2_high (unlock, elevate, unleash) |
| Actorless claims | ❌ **GAP G4** |
| Summary endings | ✅ HollowKickerRecap, closing_formulas |
| Ornamental formatting | ✅ FormattingSlop |

**Sekundär-Signale (nicht im Diagnose-Cluster, aber im SKILL.md):**
- „Formula replacement": clipped aphorisms, tidy triads, dramatic fragments → ✅ ForcedTriad, RoboticRhythm, HollowKickerRecap
- Cadence: „repeated sentence lengths, polished transition stacks, repeated openers" → ✅ UniformSentenceLength, RepeatedOpenings, generic_transitions
- „Keep the skill's internal checklist shape out of final prose" (title-case sections, exhaustive caveat blocks, three-part scaffolds) → ✅ FormattingSlop (partiell)
- „Instructions about the writing are not the writing" — **Brief-Leak**: Instruktions-Sätze des Briefings landen im Artefakt → ❌ **GAP G8** (neuartig, generation-seitig, als detect-only-Signal denkbar: „Artefakt enthält Briefing-Register")
- Evidence-bound mode: erfundene Claims/Owner/Daten verhindern → verwandt mit FakeAuthoritySlop / authority_claims, aber präventiv
- Detector-Evidence-Protokoll (tool, URL, date, hash, result) → deckt sich mit unserem Provenance-Ansatz (detect-only-ADR)

**Stärke des Skills:** Preservation-Checks (meaning loss, over-editing, „leave this alone" als valide Ausgabe) + Anti-Overcorrection — das ist Essay-Feedback-Philosophie, die unsere Ontology über keep_when-Felder ebenfalls fährt. Kein neuer Detektions-Mechanismus jenseits der genannten Gaps.

## 2. Unslop (cursor/plugins, Autor pstack) — Profil

**Typ:** Pattern-Liste (31 Muster in 7 Klassen) + Soul-Doktrin + 4-Schritt-Prozess mit Self-Audit. `disable-model-invocation: true` — reiner Editor-Hook. Reines Rewrite, keine Scores/Evidence.

### Muster-Abgleich gegen ontology.json

| # | unslop-Muster | Ontology |
|---|---|---|
| 1 | Puffery (pivotal moment, testament to, evolving landscape) | ✅ buzzwords tier1/tier2, metaphor_abuse |
| 2 | Name-dropping (Media-Listen ohne Kontext) | ❌ **GAP G6** (klein) |
| 3 | Superficial -ing phrases | ✅ SuperficialAnalysis (wörtlich identisch) |
| 4 | Promotional language (nestled, vibrant, breathtaking) | ✅ (nestled vorhanden; vibrant ❌ kleiner Listen-Fehler → G3-Anhang) |
| 5 | Vague attributions | ✅ authority_claims, FakeAuthoritySlop |
| 6 | Formulaic challenges („Despite challenges… thrives") | ✅ BinaryContrast-artig (partiell) |
| 7 | AI vocabulary | ✅ buzzwords (vollständig abgedeckt, inkl. delve/tapestry/underscore) |
| 8 | Fancy copula (serves as, stands as, boasts, features) | ⚠️ nur „serves as" gedeckt → **GAP G3** |
| 9 | „Not just X, but Y" | ✅ BinaryContrast |
| 10 | Rule of three | ✅ ForcedTriad |
| 11 | Synonym cycling | ✅ SynonymCycling |
| 12 | False ranges („from X to Y" ohne Skala) | ❌ **GAP G1** |
| 13 | Em dash overuse | ✅ EmDashExcess/ExcessiveEmDash |
| 14 | Colon overuse (Mid-Sentence-Connector) | ⚠️ ColonReveal deckt nur „Phrase: Reveal"-Form → **GAP G9** (Erweiterung) |
| 15 | Boldface overuse | ✅ BoldFormatting |
| 16 | Inline-header lists („**Label:** Label…") | ❌ **GAP G5** (FormattingSlop deckt bold-mid-sentence, nicht Label-Restatement) |
| 17 | Title case headings | ✅ TitleCaseHeadings |
| 18 | Decorative emojis | ✅ EmojiInProfessional |
| 19 | Curly quotes | ✅ CurlyQuotes |
| 20 | Chatbot phrases | ✅ ChatbotLeftover |
| 21 | Cutoff disclaimers | ⚠️ verwandt hedging_qualifiers; „While specific details are limited" als Trainings-Cutoff-Tell nicht explizit → Anhang G7 |
| 22 | Sycophantic tone | ✅ ChatbotLeftover („Great question!") |
| 23 | Filler phrases (in order to, due to the fact that) | ❌ **GAP G7** (klein) |
| 24 | Excessive hedging | ✅ ExcessiveHedging, hedging_qualifiers |
| 25 | Generic conclusions | ✅ closing_formulas, HollowKickerRecap |
| 26 | Abstract tech metaphor nouns (substrate, flywheel, north star, vector, bedrock, nexus, wedge, ratchet, evacuate, endgame, modality, harness…) | ❌ **GAP G2** (größte Lücke) |
| 27 | „Say what it does, not how it feels" (Fake-Feature-Prosa) | ⚠️ LowInformationDensity verwandt; unslop-Litmus „könnte unverändert in anderen Projektdocs stehen" = Portabilitäts-Test → bemerkenswert, aber eher Loop/Score-Doku |
| 28 | Dense sentences | ✅ density-Metriken (docs/metric) |
| 29 | Active voice / Passiv ohne Actor | ⚠️ → **G4** (mit slopbeth „actorless claims" konvergent) |
| 30 | Adverbs + schwache Verben („significantly improves") | ⚠️ FakeStrongVerb deckt Verb-Inflation; Adverb-Heuristik als Metrik-Anhang |
| 31 | Plain word (utilize→use) | ✅ buzzwords tier2/4 + de_phrases |

### Soul-Doktrin (unslop) vs. Ontology
„Sterile, voiceless writing is just as obvious" → deckungsgleich mit Anti-Overcorrection/keep_when-Philosophie; menschliche Voice-Merkmale (Meinung, Rhythmusvarianz, Ich-Form, „mess") gehören in human-voice.md (separates Issue), nicht in die Detektion.

## 3. Lücken-Bilanz → Issue-Vorschläge

| ID | Signal | Quelle | Vorschlag |
|---|---|---|---|
| **G1** | **FalseRange**: „from X to Y", wenn X/Y nicht auf gemeinsamer Skala liegen („from startups to enterprises" ok, „from scalability to passion" slop) | unslop #12 | Neue rhetoricalPattern (confidence ~0.6, keep_when: echte Spanne/Aufzählung) |
| **G2** | **TechMetaphorNoun**: abstrakte Tech-Metaphern-Nomen als Buzzword-Substitution (substrate, flywheel, north star, vector, bedrock, nexus, wedge, scaffolding, modality, paradigm-as-noun, ratchet, evacuate, endgame, harness) | unslop #26 | buzzwords-Erweiterung oder eigene phrase-Kategorie; Kern: Metaphorische statt konkrete Benennung. Achtung Modality/Vector sind in ML-Kontext legitim → keep_when zwingend |
| **G3** | **FancyCopula-Erweiterung**: boasts, stands as, features (neben vorhandenem „serves as") | unslop #8 | copula_rate-Liste erweitern (eine Zeile) |
| **G4** | **ActorlessClaim**: Passiv/Agens-lose Formulierung, wenn der Actor die Behauptung trägt („mistakes were made", „it has been proven" ✓ vorhanden, aber „queries are validated"-Passiv ohne Agent als strukturelles Signal) | unslop #29 + slopbeth (konvergent!) | Strukturelles Indikator oder FakeStrongVerb-Anhang; keep_when: Actor unbekannt/irrelevant |
| **G5** | **InlineHeaderRestatement**: Bold-Label + Doppelpunkt, der die Zeile wiederholt („**Performance:** Performance improved…") | unslop #16 | FormattingSlop-Erweiterung oder eigene Pattern (keep_when wie unslop: Label endet mit Punkt + bringt neue Info) |
| **G6** | **NameDropList**: Medien-/Brand-Aufzählung ohne Aussageinhalt | unslop #2 | typePatterns-Anhang (FakeAuthoritySlop verwandt) — S-Aufwand |
| **G7** | **FillerPhrase-Liste**: „in order to", „due to the fact that", „it is important to note" (letzteres ✓ vorhanden); „while specific details are limited" (Cutoff-Tell) | unslop #23/#21 | phrase-Erweiterung — trivial |
| **G8** | **BriefLeak**: Briefing-/Instruktions-Register im Artefakt („as per your request…", Meta-Anweisungen des Users abgedruckt) | slopbeth (einzigartig!) | Detect-only-Kandidat; überlappt meta_commentary → prüfen, evtl. Erweiterung von meta_commentary statt neues Signal |
| **G9** | **ColonConnector-Erweiterung**: Doppelpunkt als Mid-Sentence-Verbinder ohne Reveal-Charakter | unslop #14 | ColonReveal-keep_when/description erweitern |

**Priorisierung:** G1, G2, G4 als echte Signale (konvergent aus zwei unabhängigen Top-Marken-Skills); G3, G7 Trivial-Listen; G5, G9 Pattern-Erweiterungen; G6, G8zur Prüfung.

## 4. Markt-Einordnung (Kurz)

- Beide Skills bestätigen die ADR-0001-Positionierung: Der Markt liefert **Rewriter mit Musterlisten** (unslop: 31 Muster, keine Scoring/Evidence; slopbeth: Prozess + Scripts, aber ebenfalls rewrite-first). Die Detector-Nische mit Score+Evidence+Multi-Domain (Text+Code+UI) bleibt unbesetzt — stärkt #38/PR #151.
- slopbeth ist der intellektuell stärkste Wettbewerber: Preservation-Denken, Over-Edit-Guards, Detector-Evidence-Protokoll, Anti-Formel-Replacement. Unsere Anti-Overcorrection-Philosophie ist ebenbürtig; sein „unsummarizability"-Standard ist einen Metrik-Blick wert (→ docs/metric-Anhang, S).
- unslop ist Muster-Katalog + Soul; 26/31 Muster bereits abgedeckt (84%), davon 5 wörtlich identisch.

*Auto-Burn (Idle-Burner-Kette) — Recherche: skills.sh + GitHub raw, Ontology-Abgleich per ontology.json-Grep. Keine externen LLM-Urteile.*
