# Slop Examples Reference

Scored examples across text types. Use for calibration and testing.

## Table of Contents
1. [Generic Slop (0.92)](#generic-slop)
2. [SEO Slop (0.74)](#seo-slop)
3. [Academic Slop (0.85)](#academic-slop)
4. [LinkedIn Slop (0.88)](#linkedin-slop)
5. [Clean Text (0.08)](#clean-text)
6. [Borderline (0.35)](#borderline)

---

## Generic Slop

**Score: 0.92 | 🔴 Slop**

> "In today's fast-paced digital landscape, leveraging cutting-edge AI solutions is paramount for businesses seeking to unlock their full potential. The key is to find balance between innovation and practicality, as studies have shown that a robust approach can deliver game-changing results. It's important to note that self-care isn't selfish — it's a fundamental aspect of maintaining the synergy needed to thrive in this dynamic paradigm."

**Types:** GenericSlop, PseudoInsightSlop, FakeAuthoritySlop, WellnessSlop

**Signals:**
- BuzzwordOveruse (95%): landscape, leverage, cutting-edge, game-changing, synergy, paradigm, robust, unlock, dynamic
- GenericTransition (90%): "It's important to note"
- PunctuationAnomaly (70%): Em-dash in 1/3 sentences
- UniformSentenceLength (80%): All 25-35 words

**Dimensions:**
- Density: 0.31 (⚠️ < 0.40)
- Repetition: 0.22 (⚠️ > 0.20)
- Verbosity: 0.85

---

## SEO Slop

**Score: 0.74 | 🔴 Slop**

> "Coffee is a popular beverage enjoyed by millions around the world. Coffee contains caffeine, which is a stimulant. Many people drink coffee in the morning. Coffee can be prepared in various ways, including espresso, drip, and French press. In conclusion, coffee remains one of the most beloved beverages globally."

**Types:** WikipediaRehash, SEOContentFarmSlop

**Signals:**
- GenericTransition (85%): "In conclusion"
- LowPerplexity (90%): Extremely predictable
- UniformSentenceLength (90%): All 8-12 words

**Note:** Technically correct but tells you nothing you didn't already know.

---

## Academic Slop

**Score: 0.85 | 🔴 Slop**

> "Recent studies have demonstrated the efficacy of novel approaches in addressing contemporary challenges. The landscape of research in this domain has evolved significantly, with researchers leveraging state-of-the-art methodologies to uncover new insights. This paper contributes to the growing body of literature by proposing a framework that synthesizes existing paradigms."

**Types:** AcademicSlop, FakeAuthoritySlop, GenericSlop

**Signals:**
- BuzzwordOveruse (90%): landscape, leverage, state-of-the-art, paradigm
- LowPerplexity (80%): Could apply to literally any field
- Zero verifiable claims — all hedging language

---

## LinkedIn Slop

**Score: 0.88 | 🔴 Slop**

> "🔥 I'm thrilled to announce that after 10 years in the industry, I've learned one fundamental truth: the key to success is finding balance. In today's rapidly evolving landscape, those who embrace change while staying true to their core values will unlock unprecedented opportunities. Remember — self-care isn't selfish. The journey of a thousand miles begins with a single step. 💡"

**Types:** PseudoInsightSlop, WellnessSlop, GenericSlop

**Signals:**
- BuzzwordOveruse (85%): landscape, unlock
- GenericTransition (80%): "key to success", "rapidly evolving"
- PunctuationAnomaly (80%): Em-dash, emoji spam
- TrailingMoral: Ends with cliché proverb

**Note:** Announces nothing, teaches nothing, inspires no one.

---

## Clean Text

**Score: 0.08 | 🟢 Clean**

> "The quick brown fox jumps over the lazy dog. Python 3.12 adds new type syntax. Coffee tastes best when freshly ground."

**Analysis:** Short, factual, diverse vocabulary, no AI patterns.

---

## Borderline

**Score: 0.35 | 🟡 AI-Assisted**

> "Die KI-Transformation im Mittelstand erfordert einen strukturierten Ansatz: Zuerst die Prozesse analysieren, dann Use Cases priorisieren, und schliesslich in Iterationen implementieren. Wichtig ist, dass Datenschutz und EU AI Act von Beginn an integriert werden."

**Analysis:** Structured but substantive. Some AI-like patterns (lists, generic framework) but with domain-specific content. Use with cross-checking.

---

## Calibration Guide

- **0.00–0.20:** Reads like a human expert wrote it for a specific audience
- **0.20–0.40:** Likely AI-assisted but with human curation — usable
- **0.40–0.70:** Substantially AI-generated, needs verification — suspicious
- **0.70–0.90:** Classic slop patterns — do not trust
- **0.90–1.00:** Maximum slop — textbook AI output with no human touch
