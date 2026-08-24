#!/usr/bin/env python3
"""
AI Slop Scorer v2.1 — Extended signal database from AI Slop Ontology v1.1.0.

v2.1: word-boundary matching, overlap deduplication (longest match wins),
case-insensitive multilingual matching, burstiness neutral for short texts.

Usage:
    python3 slop_scorer.py --file text.txt          # preferred
    python3 slop_scorer.py text.txt                 # existing path auto-detected
    echo "text" | python3 slop_scorer.py -
    python3 slop_scorer.py "inline text"            # deprecated, warns

Returns slop_score (0-1) with dimension breakdown.
"""

import json
import os
import re
import sys
from collections import Counter
from typing import Optional

import fp_guards
import genre_profiles
import provenance_signals

# Single source of truth for the decision threshold (issue #23): guards and
# risk levels share fp_guards.THRESHOLDS instead of scattered magic numbers.
DECISION_THRESHOLD = fp_guards.THRESHOLDS["DECISION_THRESHOLD"]

# --- Extended Signal Database (from ontology.json v1.0.0) ---

BUZZWORD_TIERS = {
    "tier1_critical": {
        "confidence": 0.9,
        "words": [
            "delve", "delving", "tapestry", "rich tapestry", "realm", "the realm of",
            "navigating the landscape", "in today's rapidly evolving", "in today's ever-changing",
            "it's worth noting that", "serves as a testament", "paints a vivid picture",
            "a testament to", "at its core", "delve deeper", "let's dive in",
            "embark on a journey", "whether you're a seasoned", "game-changer", "game changing"
        ]
    },
    "tier2_high": {
        "confidence": 0.8,
        "words": [
            "unlock", "unleash", "harness", "leverage", "leverage the power of",
            "elevate", "elevating", "empower", "empowering", "foster", "fostering",
            "spearhead", "spearheading", "cultivate", "cultivating", "catalyst",
            "a catalyst for", "cornerstone", "beacon", "a beacon of", "pivotal",
            "paramount", "indispensable", "imperative", "multifaceted", "nuanced",
            "robust", "seamless", "comprehensive", "holistic", "transformative",
            "revolutionary", "groundbreaking", "innovative", "cutting-edge",
            "state-of-the-art", "the power of", "at the end of the day",
            "in the grand scheme of things", "not only... but also",
            "it's important to remember", "it's crucial to understand",
            # Original tier1-4 retained
            "landscape", "dynamic",
            # issue #16: no-ai-slop banned-word gap fill
            "utilize", "meticulous", "supercharge", "supercharged", "nestled",
        ]
    },
    "tier3_moderate": {
        "confidence": 0.6,
        "words": [
            "synergy", "paradigm", "paradigm shift", "ecosystem", "in this space",
            "optimize", "streamline", "agile", "disrupt", "disruption", "scalable",
            "sustainable", "leveraging AI", "the intersection of", "bridging the gap",
            "tip of the iceberg", "silver bullet", "one-size-fits-all",
            "punching above its weight", "sweet spot", "the elephant in the room",
            "leveling the playing field", "moving the needle", "doubling down"
        ]
    },
    "tier4_weak": {
        "confidence": 0.4,
        "words": [
            "innovate", "innovation", "efficient", "effective", "strategic",
            "proactive", "best practices", "value proposition", "stakeholder",
            "value-added", "results-driven", "forward-thinking", "future-proof",
            "next-generation", "mission-critical", "actionable insights",
            "deep dive", "deep-dive",
            # issue #16: context-dependent no-ai-slop banned word
            "quietly",
        ]
    }
}

PHRASE_CATEGORIES = {
    "hedging_qualifiers": {
        "confidence": 0.75,
        "phrases": [
            "it's worth noting", "it's important to note", "it's important to remember",
            "it's crucial to understand", "it's essential to recognize", "while this may vary",
            "it's safe to say", "needless to say", "worth mentioning",
            "it goes without saying", "one thing is certain", "it's no secret that",
            "it's no surprise that", "an important consideration", "it bears repeating",
            "notably", "importantly", "crucially"
        ]
    },
    "generic_transitions": {
        "confidence": 0.7,
        "phrases": [
            "in conclusion", "to sum up", "to summarize", "as previously mentioned",
            "furthermore", "moreover", "additionally", "in addition",
            "on the other hand", "by the same token", "with that in mind",
            "that being said", "having said that", "at the end of the day",
            "when all is said and done", "taking a step back", "with that said",
            "as we've explored", "as we've seen", "in this article, we've",
            "in this blog post, we've"
        ]
    },
    "opening_formulas": {
        "confidence": 0.8,
        "phrases": [
            "in today's rapidly evolving landscape", "in today's ever-changing world",
            "in today's digital age", "in an increasingly interconnected world",
            "as the digital landscape continues to evolve",
            "in recent years,", "in the age of", "welcome to the world of",
            "whether you're a seasoned", "have you ever wondered", "imagine a world where",
            "picture this"
        ]
    },
    "closing_formulas": {
        "confidence": 0.8,
        "phrases": [
            "in conclusion,", "to wrap things up,", "as we look to the future,",
            "the future of", "only time will tell", "one thing is for certain",
            "the possibilities are endless", "the bottom line is",
            "as we move forward", "embrace the future",
            "stay ahead of the curve", "the journey doesn't end here", "until next time"
        ]
    },
    "metaphor_abuse": {
        "confidence": 0.75,
        "phrases": [
            "rich tapestry", "navigating the landscape", "serves as a testament",
            "paints a vivid picture", "tip of the iceberg", "spearheading a revolution",
            "bridging the gap between", "the holy grail of", "the elephant in the room",
            "a double-edged sword", "the perfect storm", "a perfect blend of",
            "a delicate balance", "a harmonious blend", "the backbone of",
            "the cornerstone of", "the lifeblood of", "the driving force behind",
            "at the heart of", "a world of difference", "a beacon of hope",
            "a sea of"
        ]
    },
    "listicle_tells": {
        "confidence": 0.7,
        "phrases": [
            "let's explore", "let's dive into", "let's break it down",
            "here are", "top reasons", "things you need to know",
            "you might be wondering", "the short answer is", "the long answer is",
            "but wait, there's more", "here's the thing", "here's the kicker",
            "pro tip:", "fun fact:", "key takeaway:", "bottom line:"
        ]
    },
    # --- Editor tells (issue #8): daily-driver tics beyond essay/SEO slop ---
    "emphasis_crutches": {
        "confidence": 0.7,
        "phrases": [
            "let that sink in", "full stop", "end of story", "no pun intended",
            "make no mistake", "simply put", "read that again", "mic drop"
        ]
    },
    "meta_commentary": {
        "confidence": 0.7,
        "phrases": [
            "the rest of this essay", "the remainder of this document",
            "in this section, we will", "in the next section",
            "as we'll see later", "throughout this article",
            "without further ado", "in the following paragraphs"
        ]
    },
    "rhetorical_setups": {
        "confidence": 0.7,
        "phrases": [
            "plot twist:", "what if i told you", "here's a thought", "guess what",
            "believe it or not", "sounds too good to be true",
            "you might ask", "fair question"
        ]
    },
    "vague_declaratives": {
        "confidence": 0.65,
        "phrases": [
            "the stakes are high", "the stakes couldn't be higher",
            "timing is everything", "context matters",
            "there's a lot to unpack", "more than meets the eye"
        ]
    },
    "weasel_attribution": {
        "confidence": 0.75,
        "phrases": [
            "experts agree", "widely regarded as", "it is widely accepted",
            "many believe", "some say", "critics argue",
            "people are saying", "sources say", "insiders claim"
        ]
    }
}

MULTILINGUAL_BUZZWORDS = {
    "german": [
        "im heutigen schnelllebigen", "es gilt zu beachten", "nunmehr",
        "im digitalen Zeitalter", "die sich ständig wandelnde", "sowohl als auch",
        "es ist wichtig zu betonen", "im Folgenden",
        "zusammenfassend lässt sich sagen", "ein tiefgreifender Wandel",
        "die Synergieeffekte", "ganzheitlicher Ansatz", "der Gamechanger"
    ],
    "french": [
        "il est important de noter", "dans le paysage actuel",
        "dans un monde en constante évolution", "il convient de souligner",
        "force est de constater", "rappelons que", "en somme", "en fin de compte"
    ],
    "spanish": [
        "en el paisaje actual", "es importante destacar", "cabe señalar que",
        "en conclusión", "en el mundo de hoy", "no cabe duda de que"
    ],
    # Added 2026-07: high-slop-volume languages where detection tooling is
    # weakest (ontology §12). Markers are the formulaic phrases LLMs produce
    # when translating the English opening/hedging/closing templates.
    "hindi": [
        "आज की तेज़ रफ़्तार दुनिया में", "यह ध्यान रखना महत्वपूर्ण है",
        "निष्कर्ष में", "डिजिटल युग में", "संक्षेप में कहें तो",
        "गेम चेंजर", "समग्र दृष्टिकोण", "महत्वपूर्ण भूमिका निभाता है",
        "आइए जानते हैं", "यह कहना सुरक्षित है"
    ],
    "vietnamese": [
        "trong thế giới ngày nay", "trong thời đại số",
        "điều quan trọng cần lưu ý", "tóm lại", "không thể phủ nhận rằng",
        "đóng vai trò quan trọng", "trong bối cảnh hiện nay",
        "hãy cùng khám phá", "một cách toàn diện"
    ],
    "urdu": [
        "آج کی تیز رفتار دنیا میں", "یہ بات قابل ذکر ہے", "ڈیجیٹل دور میں",
        "خلاصہ یہ ہے کہ", "اہم کردار ادا کرتا ہے", "اس میں کوئی شک نہیں",
        "آئیے جانتے ہیں", "مجموعی طور پر"
    ]
}

STRUCTURAL_INDICATORS = [
    {"id": "ExcessiveEmDash", "threshold": 0.5, "per": "sentence", "confidence": 0.85},
    {"id": "UniformSentenceLength", "threshold": 3, "metric": "std_dev_words", "confidence": 0.7},
    {"id": "NumberedListOveruse", "threshold": 5, "metric": "consecutive_numbered_items", "confidence": 0.5},
    {"id": "MirroredIntroConclusion", "confidence": 0.75},
    {"id": "BalancedStructure", "confidence": 0.65},
    {"id": "ExcessiveHedging", "threshold": 3, "per": 500, "words": True, "confidence": 0.7},
    {"id": "PerfectGrammarUniformTone", "confidence": 0.55},
]

MORAL_PATTERNS = [
    "remember that", "in the end", "ultimately", "the lesson is",
    "what matters most", "at the end of the day", "it's important to remember",
    "the key takeaway", "the bottom line is",
]

AUTHORITY_PATTERNS = [
    "studies have shown", "research shows", "experts say",
    "it has been proven", "scientists have found", "researchers discovered",
    "recent studies", "a growing body of evidence",
]


STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "it", "its", "this", "that", "these",
    "those", "as", "at", "by", "from", "we", "you", "they", "he", "she", "i",
    "not", "no", "can", "will", "have", "has", "had", "do", "does", "their",
    "our", "your", "my", "his", "her", "them", "us", "s", "t",
}


def _term_pattern(term: str) -> str:
    """Regex for a term with word boundaries where the term edge is a word char."""
    t = term.lower()
    left = r'\b' if t[0].isalnum() else ''
    right = r'\b' if t[-1].isalnum() else ''
    return left + re.escape(t) + right


def find_term_matches(text_lower: str, terms: list) -> dict:
    """
    Match terms against text with word boundaries and overlap suppression:
    if a longer term already covers a span (e.g. "rich tapestry"), a shorter
    term inside that span (e.g. "tapestry") is not counted again.

    Returns {term_lowercase: occurrence_count} for matched terms. Keys are
    lowercased so callers can index lookup tables built with lowered terms
    even when the input term list has mixed case.
    """
    spans = []
    for term in terms:
        for m in re.finditer(_term_pattern(term), text_lower):
            spans.append((m.start(), m.end(), term.lower()))
    # Longest match wins; ties resolved by position
    spans.sort(key=lambda x: (-(x[1] - x[0]), x[0]))
    occupied = []
    counts = {}
    for start, end, term in spans:
        if any(start < oe and end > os for os, oe in occupied):
            continue
        occupied.append((start, end))
        counts[term] = counts.get(term, 0) + 1
    return counts


def information_density(text: str) -> float:
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def repetition_ratio(text: str) -> float:
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    counts = Counter(words)
    return counts.most_common(1)[0][1] / len(words)


def burstiness(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) < 2:
        return 0.0
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    return variance ** 0.5


def buzzword_score(text: str, tiers: Optional[dict] = None) -> tuple:
    if tiers is None:
        tiers = BUZZWORD_TIERS
    text_lower = text.lower()
    term_to_tier = {}
    all_terms = []
    for tier_name, tier_def in tiers.items():
        words = tier_def if isinstance(tier_def, list) else tier_def.get("words", [])
        for w in words:
            term_to_tier[w.lower()] = tier_name
            all_terms.append(w)
    # Match all tiers jointly so overlapping terms ("tapestry" inside
    # "rich tapestry") are counted once, for the longest match.
    matched = find_term_matches(text_lower, all_terms)
    hits = []
    tier_hits = {}
    for term in matched:
        tier = term_to_tier.get(term, "unknown")
        tier_hits.setdefault(tier, []).append(term)
        hits.append(term)
    return len(hits), hits, tier_hits



# Issue #22: substitute (fake-strong) verbs that vary prose away from the
# copula. NOTE: several of these strings overlap BUZZWORD_TIERS entries
# ("serves as a testament", "boasts" family). To prevent double scoring
# (#46 prevention) copula_stats() excludes substitute matches that overlap
# a buzzword span — those phrases are already penalized by the buzzword
# dimension and must not simultaneously lower the copula rate.
SUBSTITUTE_VERB_PATTERNS = [
    "serves as", "boasts", "features", "refers to", "represents", "embodies",
]


def copula_stats(text: str) -> dict:
    """Copula rate: is/are/was/were vs. substitute linking verbs (#22).

    Returns {"copulas", "substitutes", "rate"} where rate = copulas /
    (copulas + substitutes); 0.0 when neither occurs. Substitute matches
    overlapping buzzword spans are excluded from the denominator
    (#46 prevention, see SUBSTITUTE_VERB_PATTERNS note above).
    """
    text_lower = text.lower()
    copula_spans = [m.span() for m in re.finditer(r"\b(?:is|are|was|were)\b", text_lower)]
    sub_spans = []
    for m in re.finditer(
        r"\b(?:" + "|".join(re.escape(v) for v in SUBSTITUTE_VERB_PATTERNS) + r")\b",
        text_lower,
    ):
        # #46 prevention: ignore substitutes that overlap a buzzword match
        all_terms = [w for t in BUZZWORD_TIERS.values() for w in t["words"]]
        overlapping = any(
            m.start() < be and m.end() > bs
            for bm in re.finditer(
                r"(?:" + "|".join(_term_pattern(w) for w in all_terms) + r")",
                text_lower,
            )
            for bs, be in [bm.span()]
        )
        if not overlapping:
            sub_spans.append(m.span())
    total = len(copula_spans) + len(sub_spans)
    rate = len(copula_spans) / total if total else 0.0
    return {"copulas": len(copula_spans), "substitutes": len(sub_spans), "rate": rate}


# Issue #24: adverb-rate signal. Delimitation to the #21 voice principles:
# #21 is a WRITING doctrine (which adverbs to prefer or cut when composing);
# this dimension only MEASURES the -ly rate of received text and draws no
# style judgment. Delimitation to #22: adverbs are not verbs, so no span
# overlap with the copula dimension is possible by construction.
ADVERB_RATE_THRESHOLD = 0.04   # > 4% -ly words
ADVERB_MIN_WORDS = 40          # rate is meaningless on very short texts
INTENSIFIERS = ["very", "really", "extremely", "incredibly", "remarkably"]


def adverb_stats(text: str) -> dict:
    """Count -ly adverbs, total words, rate, and intensifier hits (#24).

    Intensifier hits are reported but only AMPLIFY an adverb rate that is
    already above threshold (see slop_score); they never contribute alone.
    FU-1 (review-batch-a.md §6): 4 of the 5 intensifiers end in -ly and were
    double-counted into the -ly rate. Intensifiers are their own signal, so
    their spans are excluded from BOTH the numerator and the denominator of
    the rate — a pure-intensifier text measures rate 0.0, never adverb_slop.
    """
    text_lower = text.lower()
    total = re.findall(r"\b\w+\b", text_lower)
    intensifier_spans = []
    for m in re.finditer(r"(?:" + "|".join(_term_pattern(w) for w in INTENSIFIERS) + r")",
                         text_lower):
        intensifier_spans.append(m.span())
    intensifiers = len(intensifier_spans)
    # -ly words minus intensifier spans (span-overlap exclusion like copula_stats)
    ly_spans = [m.span() for m in re.finditer(r"\b\w+ly\b", text_lower)]
    pure_ly = sum(
        1 for ws, we in ly_spans
        if not any(ws < ie and we > i_s for i_s, ie in intensifier_spans)
    )
    # denominator: all words except the intensifier occurrences themselves
    denom = len(total) - intensifiers
    rate = pure_ly / denom if denom > 0 else 0.0
    return {
        "ly_words": pure_ly,
        "total_words": len(total),
        "rate": round(rate, 4),
        "intensifiers": intensifiers,
    }

def phrase_category_score(text: str) -> dict:
    text_lower = text.lower()
    term_to_cat = {}
    all_terms = []
    for cat_name, cat_def in PHRASE_CATEGORIES.items():
        phrases = cat_def if isinstance(cat_def, list) else cat_def.get("phrases", [])
        for p in phrases:
            term_to_cat.setdefault(p.lower(), []).append(cat_name)
            all_terms.append(p)
    matched = find_term_matches(text_lower, all_terms)
    results = {}
    for term in matched:
        for cat in term_to_cat.get(term, []):
            results.setdefault(cat, []).append(term)
    return results


def multilingual_buzzword_score(text: str) -> dict:
    text_lower = text.lower()
    results = {}
    for lang, words in MULTILINGUAL_BUZZWORDS.items():
        matched = find_term_matches(text_lower, [w.lower() for w in words])
        if matched:
            results[lang] = sorted(matched)
    return results


def punctuation_anomaly_score(text: str) -> dict:
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    n = len(sentences) or 1
    return {
        "emDashRate": round((text.count('\u2014') + text.count('\u2013')) / n, 3),
        "ellipsisRate": round(text.count('...') / n, 3),
        "exclamationRate": round(text.count('!') / n, 3),
    }


def trailing_moral(text: str) -> bool:
    tail = text.lower().strip()[-200:]
    return bool(find_term_matches(tail, MORAL_PATTERNS))


def list_heavy(text: str) -> bool:
    lines = text.strip().split('\n')
    list_lines = sum(1 for l in lines if re.match(r'^\s*[-*•]\s|^\s*\d+[.)]\s', l))
    return len(lines) > 3 and list_lines / len(lines) > 0.4


def mirrored_intro_conclusion(text: str) -> bool:
    """Check if conclusion restates introduction with synonym substitution."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) < 4:
        return False
    intro_words = set(re.findall(r'\b\w+\b', sentences[0].lower())) - STOPWORDS
    conclusion_words = set(re.findall(r'\b\w+\b', sentences[-1].lower())) - STOPWORDS
    if len(intro_words) < 3 or len(conclusion_words) < 3:
        return False
    overlap = len(intro_words & conclusion_words) / min(len(intro_words), len(conclusion_words))
    return overlap > 0.6


def slop_score(text: str, weights: Optional[dict] = None, genre: Optional[str] = None) -> dict:
    # Issue #42: explicit genre register profile (no auto-detection).
    # Exemptions apply to SIGNAL matching only (composed with the #23 quote
    # exemption); structural dimensions keep the full text. The genre also
    # raises the decision threshold for risk classification — provenance
    # floors and >= 2-family escalation keep their original strength.
    genre_profile = None
    if genre is not None:
        genre_profile = genre_profiles.get_profile(genre)
    if weights is None:
        # Calibrated 2026-07 via eval/calibrate.py (coordinate ascent on
        # eval/corpus.jsonl, precision floor 0.95): F1 0.47 -> 0.89 at
        # threshold 0.40 with zero false positives. Weights intentionally sum
        # to > 1 — the total is capped at 1.0, so strong evidence on a few
        # dimensions is enough to cross the threshold. Recalibrate for your
        # domain with eval/calibrate.py --corpus your_data.jsonl.
        weights = {
            "density": 0.15,
            "repetition": 0.18,
            "burstiness": 0.30,
            "buzzwords": 0.26,
            "phrases": 0.30,
            "punctuation": 0.30,
            "trailing_moral": 0.06,
            "list_heavy": 0.04,
            "fake_authority": 0.18,
            "verbosity": 0.04,
            "multilingual": 0.04,
            "mirrored": 0.05,
            "structural": 0.08,
        }

    density = information_density(text)
    rep = repetition_ratio(text)
    burst = burstiness(text)
    # FP guards (#23): buzzword/phrase/multilingual/authority signals are
    # matched on the quote-stripped text — quoted slop examples (reviews,
    # documentation, meta-analysis) do not inherit the example's signals.
    # Structural dimensions (density, burstiness, repetition) keep the
    # full text.
    signal_text = fp_guards.strip_quotes(text)
    if genre_profile is not None:
        signal_text = genre_profiles.strip_exempt_terms(
            signal_text, genre_profile["exempt_terms"])
        weights = dict(weights)
        for k in genre_profile.get("zero_weights", []):
            weights[k] = 0.0
    buzz_count, buzz_hits, buzz_tiers = buzzword_score(signal_text)
    phrase_matches = phrase_category_score(signal_text)
    multilingual_matches = multilingual_buzzword_score(signal_text)
    punct = punctuation_anomaly_score(text)
    # Provenance markers (#20): deterministic AI-pipeline artifacts. High
    # confidence — counted per match, never stripped by quote exemption
    # (a quoted artifact still proves the source text passed through a
    # pipeline).
    prov_matches = provenance_signals.provenance_hits(text)
    prov_count = sum(len(v) for v in prov_matches.values())
    cop = copula_stats(text)
    adv = adverb_stats(text)
    # Cumulative rule (#23): a phrase category only scores with >= 2 hits.
    total_phrases = fp_guards.effective_phrase_count(phrase_matches)
    total_multi = sum(len(v) for v in multilingual_matches.values())

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    num_sentences = len(sentences) or 1
    avg_sentence_len = len(re.findall(r'\b\w+\b', text)) / num_sentences

    # Normalize
    density_slop = max(0, (0.50 - density) / 0.50)
    rep_slop = min(1, rep / 0.30)
    # Burstiness is meaningless for very short texts: with < 3 sentences the
    # std-dev of sentence lengths is ~0 by construction, which would falsely
    # push every short text toward slop. Treat it as neutral instead.
    burst_slop = max(0, (5 - burst) / 5) if num_sentences >= 3 else 0.0
    buzz_slop = min(1, buzz_count / 6)  # 6+ buzzwords = definite slop
    # (divisor aligned with src/scorer.py; was 8 — MS-I1 calibration 2026-08-24,
    # see eval/control_set.jsonl slop-fn-01, 3 tier-2 buzzwords + 2 phrase hits
    # scored only 0.279 and slipped under the threshold)
    phrase_slop = min(1, total_phrases / 4)
    punct_slop = min(1, (punct["emDashRate"] + punct["ellipsisRate"] + punct["exclamationRate"]) / 2)
    moral_slop = 1.0 if trailing_moral(text) else 0.0
    list_slop = 1.0 if list_heavy(text) else 0.0
    authority_matches = find_term_matches(signal_text.lower(), AUTHORITY_PATTERNS)
    auth_count = len(authority_matches)
    auth_slop = min(1, auth_count / 2)
    verbose_slop = min(1, max(0, (avg_sentence_len - 20)) / 15)
    multi_slop = min(1, total_multi / 3)
    mirrored_slop = 1.0 if mirrored_intro_conclusion(text) else 0.0

    # Structural signals count
    struct_signals = 0
    if punct["emDashRate"] > 0.5:
        struct_signals += 1
    if num_sentences >= 3 and burst < 3:
        struct_signals += 1
    if mirrored_slop:
        struct_signals += 1
    struct_slop = min(1, struct_signals / 3)

    overall = (
        weights["density"] * density_slop +
        weights["repetition"] * rep_slop +
        weights["burstiness"] * burst_slop +
        weights["buzzwords"] * buzz_slop +
        weights["phrases"] * phrase_slop +
        weights["punctuation"] * punct_slop +
        weights["trailing_moral"] * moral_slop +
        weights["list_heavy"] * list_slop +
        weights["fake_authority"] * auth_slop +
        weights["verbosity"] * verbose_slop +
        weights["multilingual"] * multi_slop +
        weights["mirrored"] * mirrored_slop +
        weights["structural"] * struct_slop
    )

    # Non-English texts get diluted by the English-only dimensions (buzzwords,
    # phrases, authority claims are all English). If a text hits 3+ multilingual
    # AI markers, that is strong evidence on its own — floor at "Suspicious".
    if total_multi >= 3:
        overall = max(overall, DECISION_THRESHOLD)

    # Escalation (#23 generalization of the ">= 2 high-severity signals"
    # ontology rule): two or more independent marker families agreeing are
    # decisive even when neutral dimensions (density, repetition,
    # burstiness) dilute the weighted sum. Families:
    #   - buzzwords >= 50% of the normalization divisor
    #   - corroborated phrase categories (>= 2 hits, cumulative rule)
    #   - fake-authority claims
    #   - trailing moral, mirrored intro/conclusion
    #   - a single hit in a HIGH-CONFIDENCE phrase category (confidence
    #     >= 0.75: opening/closing formulas, hedging, metaphor abuse,
    #     weasel attribution) — a lone "in conclusion," plus buzzwords is
    #     still two families agreeing.
    # Adverb rate (#24): conditional contribution — fires only above the
    # rate threshold on texts of sufficient length; intensifiers (very,
    # really, extremely, incredibly, remarkably) amplify an already-fired
    # rate but never trigger on their own. Not a strong escalation family.
    adverb_slop = 0.0
    if adv["total_words"] >= ADVERB_MIN_WORDS and adv["rate"] > ADVERB_RATE_THRESHOLD:
        adverb_slop = 0.5
        if adv["intensifiers"] >= 2:
            adverb_slop = 1.0
    overall += weights.get("adverb", 0.0) * adverb_slop
    # Copula rate (#22): conditional contribution only — definition-heavy
    # prose (rate >= 0.9 with >= 4 linking constructions) adds a small
    # weighted amount; never a standalone trigger, never a strong family.
    copula_slop = 1.0 if (cop["rate"] >= 0.9 and cop["copulas"] + cop["substitutes"] >= 4) else 0.0
    overall += weights.get("copula", 0.0) * copula_slop
    # Provenance (#20): any pipeline artifact floors the text at the
    # decision threshold; 2+ markers are treated as decisive evidence.
    prov_slop = min(1, prov_count / 2)
    overall += weights.get("provenance", 0.0) * prov_slop
    if prov_count >= 1:
        overall = max(overall, DECISION_THRESHOLD)
    high_conf_single = any(
        PHRASE_CATEGORIES[cat].get("confidence", 0.7) >= 0.75
        for cat in phrase_matches
    )
    strong_families = sum([
        buzz_slop >= 0.5,
        phrase_slop >= 0.5,
        auth_slop >= 0.5,
        moral_slop == 1.0,
        mirrored_slop == 1.0,
        high_conf_single,
        prov_count >= 1,
    ])
    if strong_families >= 2:
        overall = max(overall, DECISION_THRESHOLD)

    decision_threshold = (
        genre_profile["decision_threshold"] if genre_profile else DECISION_THRESHOLD
    )
    score = round(min(overall, 1.0), 3)

    if score >= 0.90:
        risk = "⚫ Malicious/Severe"
    elif score >= 0.70:
        risk = "🔴 Slop"
    elif score >= decision_threshold:
        risk = "🟠 Suspicious"
    elif score >= 0.25:
        risk = "🟡 AI-Assisted"
    else:
        risk = "🟢 Clean"

    if score >= 0.70:
        action = "Do not cite. Do not store as fact. Require independent verification."
    elif score >= decision_threshold:
        action = "Use only as weak signal. Cross-check with primary sources."
    elif score >= 0.25:
        action = "Use with cross-checking."
    else:
        action = "Normal use, standard source checks apply."

    return {
        "slop_score": score,
        "risk_level": risk,
        "action": action,
        **({"genre": genre} if genre else {}),
        "dimensions": {
            "information_density": round(density, 3),
            "repetition_ratio": round(rep, 3),
            "burstiness": round(burst, 2),
            "buzzword_count": buzz_count,
            "phrase_match_count": total_phrases,
            "multilingual_matches": total_multi,
            "provenance_markers": prov_count,
            "copula": cop,
            "adverb": {k: adv[k] for k in ("ly_words", "rate", "intensifiers")},
            "fake_authority_claims": auth_count,
            "avg_sentence_length": round(avg_sentence_len, 1),
            "punctuation": punct,
            "has_trailing_moral": moral_slop == 1.0,
            "is_list_heavy": list_slop == 1.0,
            "has_mirrored_intro_conclusion": mirrored_slop == 1.0,
        },
        "dimension_scores": {
            "density_slop": round(density_slop, 3),
            "repetition_slop": round(rep_slop, 3),
            "burstiness_slop": round(burst_slop, 3),
            "buzzword_slop": round(buzz_slop, 3),
            "phrase_slop": round(phrase_slop, 3),
            "punctuation_slop": round(punct_slop, 3),
            "moral_slop": moral_slop,
            "list_slop": list_slop,
            "authority_slop": round(auth_slop, 3),
            "verbosity_slop": round(verbose_slop, 3),
            "multilingual_slop": round(multi_slop, 3),
            "mirrored_slop": mirrored_slop,
            "provenance_slop": round(prov_slop, 3),
            "copula_slop": copula_slop,
            "adverb_slop": adverb_slop,
            "structural_slop": round(struct_slop, 3),
        },
        "signals": {
            "buzzword_hits": buzz_hits,
            "buzzword_tiers": buzz_tiers,
            "phrase_categories": phrase_matches,
            "multilingual": multilingual_matches,
            "authority_phrases": sorted(authority_matches),
            "moral_detected": moral_slop == 1.0,
            "list_heavy": list_slop == 1.0,
            "mirrored_intro_conclusion": mirrored_slop == 1.0,
            "provenance": prov_matches,
        }
    }


def format_report(result: dict) -> str:
    lines = [
        f"🔍 Slop Analysis v2",
        f"Score: {result['slop_score']} | {result['risk_level']}",
        f"Action: {result['action']}",
        "",
        "📊 Dimensions:",
    ]

    dims = result["dimensions"]
    dscores = result["dimension_scores"]
    lines.append(f"  Density: {dims['information_density']} (slop: {dscores['density_slop']})")
    lines.append(f"  Repetition: {dims['repetition_ratio']} (slop: {dscores['repetition_slop']})")
    lines.append(f"  Burstiness: {dims['burstiness']} (slop: {dscores['burstiness_slop']})")
    lines.append(f"  Buzzwords: {dims['buzzword_count']} (slop: {dscores['buzzword_slop']})")
    lines.append(f"  AI Phrases: {dims['phrase_match_count']} (slop: {dscores['phrase_slop']})")
    lines.append(f"  Authority claims: {dims['fake_authority_claims']} (slop: {dscores['authority_slop']})")
    lines.append(f"  Multilingual: {dims['multilingual_matches']} (slop: {dscores['multilingual_slop']})")
    lines.append(f"  Avg sentence: {dims['avg_sentence_length']} words (slop: {dscores['verbosity_slop']})")
    lines.append(f"  Mirrored intro↔conclusion: {'⚠️ YES' if dims['has_mirrored_intro_conclusion'] else 'No'}")
    lines.append(f"  Trailing moral: {'⚠️ YES' if dims['has_trailing_moral'] else 'No'}")
    lines.append(f"  List-heavy: {'⚠️ YES' if dims['is_list_heavy'] else 'No'}")

    signals = result["signals"]
    if signals["buzzword_tiers"]:
        lines.append(f"\n🏷️ Buzzwords by tier:")
        for tier, words in signals["buzzword_tiers"].items():
            lines.append(f"  {tier}: {', '.join(words)}")
    if signals["phrase_categories"]:
        lines.append(f"\n🔗 AI Phrases:")
        for cat, phrases in signals["phrase_categories"].items():
            lines.append(f"  {cat}: {', '.join(phrases)}")
    if signals["multilingual"]:
        lines.append(f"\n🌐 Multilingual:")
        for lang, words in signals["multilingual"].items():
            lines.append(f"  {lang}: {', '.join(words)}")
    if signals["authority_phrases"]:
        lines.append(f"\n📢 Authority claims: {', '.join(signals['authority_phrases'])}")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 slop_scorer.py \"Text to analyze\"")
        print("       echo \"text\" | python3 slop_scorer.py -")
        print("       python3 slop_scorer.py --json \"Text to analyze\"")
        sys.exit(1)

    use_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--json"]

    # Issue #42: explicit genre-register profile (--genre legal|academic|...)
    genre = None
    if "--genre" in args:
        i = args.index("--genre")
        if i + 1 >= len(args):
            print("Error: --genre requires a name", file=sys.stderr)
            sys.exit(2)
        genre = args[i + 1]
        try:
            genre_profiles.get_profile(genre)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)
        args = args[:i] + args[i + 2:]

    # --file PATH: explicit file input (preferred)
    file_path = None
    if "--file" in args:
        i = args.index("--file")
        if i + 1 >= len(args):
            print("Error: --file requires a path", file=sys.stderr)
            sys.exit(2)
        file_path = args[i + 1]
        args = args[:i] + args[i + 2:]

    if file_path is not None:
        if not os.path.isfile(file_path):
            print(f"Error: No such file: {file_path}", file=sys.stderr)
            sys.exit(2)
        with open(file_path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    elif args and args[0] == "-":
        text = sys.stdin.read()
    elif args and os.path.isfile(args[0]):
        # Auto-detection: a positional arg that is an existing file is read
        # as file content. (MS-I1 bug: it used to be scored as literal argv
        # text, producing artifacts like "Avg sentence 3.0 words".)
        if len(args) > 1:
            print("Error: multiple args with a file path is ambiguous; "
                  "pass the file alone or use --file", file=sys.stderr)
            sys.exit(2)
        file_path = args[0]
        with open(file_path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    elif args:
        print("Warning: scoring inline argv text is deprecated; "
              "use --file PATH or pipe via stdin (\"-\") instead.",
              file=sys.stderr)
        text = " ".join(args)
    else:
        print("Usage: python3 slop_scorer.py [--json] [--genre NAME] (--file PATH | - | \"Text\")",
              file=sys.stderr)
        sys.exit(1)

    result = slop_score(text, genre=genre)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))
