#!/usr/bin/env python3
"""
AI Slop Scorer v2 — Extended signal database from AI Slop Ontology v1.0.0.

Usage:
    python3 slop_scorer.py "Text to analyze"
    python3 slop_scorer.py --json "Text to analyze"
    echo "Text to analyze" | python3 slop_scorer.py -

Returns slop_score (0-1) with dimension breakdown.
"""

import json
import re
import sys
from collections import Counter
from typing import Optional

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
            "landscape", "dynamic"
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
            "deep dive", "deep-dive"
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
    hits = []
    tier_hits = {}
    for tier_name, tier_def in tiers.items():
        words = tier_def if isinstance(tier_def, list) else tier_def.get("words", [])
        tier_matches = []
        for w in words:
            if w in text_lower:
                tier_matches.append(w)
        if tier_matches:
            tier_hits[tier_name] = tier_matches
            hits.extend(tier_matches)
    return len(hits), hits, tier_hits


def phrase_category_score(text: str) -> dict:
    text_lower = text.lower()
    results = {}
    for cat_name, cat_def in PHRASE_CATEGORIES.items():
        phrases = cat_def if isinstance(cat_def, list) else cat_def.get("phrases", [])
        matches = [p for p in phrases if p in text_lower]
        if matches:
            results[cat_name] = matches
    return results


def multilingual_buzzword_score(text: str) -> dict:
    text_lower = text.lower()
    results = {}
    for lang, words in MULTILINGUAL_BUZZWORDS.items():
        matches = [w for w in words if w in text_lower]
        if matches:
            results[lang] = matches
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
    return any(p in tail for p in MORAL_PATTERNS)


def list_heavy(text: str) -> bool:
    lines = text.strip().split('\n')
    list_lines = sum(1 for l in lines if re.match(r'^\s*[-*•]\s|^\s*\d+[.)]\s', l))
    return len(lines) > 3 and list_lines / len(lines) > 0.4


def mirrored_intro_conclusion(text: str) -> bool:
    """Check if conclusion restates introduction with synonym substitution."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) < 4:
        return False
    intro_words = set(re.findall(r'\b\w+\b', sentences[0].lower()))
    conclusion_words = set(re.findall(r'\b\w+\b', sentences[-1].lower()))
    if not intro_words or not conclusion_words:
        return False
    overlap = len(intro_words & conclusion_words) / min(len(intro_words), len(conclusion_words))
    return overlap > 0.6


def slop_score(text: str, weights: Optional[dict] = None) -> dict:
    if weights is None:
        weights = {
            "density": 0.15,
            "repetition": 0.08,
            "burstiness": 0.08,
            "buzzwords": 0.12,
            "phrases": 0.15,
            "punctuation": 0.05,
            "trailing_moral": 0.04,
            "list_heavy": 0.04,
            "fake_authority": 0.08,
            "verbosity": 0.04,
            "multilingual": 0.04,
            "mirrored": 0.05,
            "structural": 0.08,
        }

    density = information_density(text)
    rep = repetition_ratio(text)
    burst = burstiness(text)
    buzz_count, buzz_hits, buzz_tiers = buzzword_score(text)
    phrase_matches = phrase_category_score(text)
    multilingual_matches = multilingual_buzzword_score(text)
    punct = punctuation_anomaly_score(text)
    total_phrases = sum(len(v) for v in phrase_matches.values())
    total_multi = sum(len(v) for v in multilingual_matches.values())

    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    num_sentences = len(sentences) or 1
    avg_sentence_len = len(re.findall(r'\b\w+\b', text)) / num_sentences

    # Normalize
    density_slop = max(0, (0.50 - density) / 0.50)
    rep_slop = min(1, rep / 0.30)
    burst_slop = max(0, (5 - burst) / 5)
    buzz_slop = min(1, buzz_count / 8)
    phrase_slop = min(1, total_phrases / 4)
    punct_slop = min(1, (punct["emDashRate"] + punct["ellipsisRate"] + punct["exclamationRate"]) / 2)
    moral_slop = 1.0 if trailing_moral(text) else 0.0
    list_slop = 1.0 if list_heavy(text) else 0.0
    auth_count = sum(1 for p in AUTHORITY_PATTERNS if p in text.lower())
    auth_slop = min(1, auth_count / 2)
    verbose_slop = min(1, max(0, (avg_sentence_len - 20)) / 15)
    multi_slop = min(1, total_multi / 3)
    mirrored_slop = 1.0 if mirrored_intro_conclusion(text) else 0.0

    # Structural signals count
    struct_signals = 0
    if punct["emDashRate"] > 0.5:
        struct_signals += 1
    if burst < 3:
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

    score = round(min(overall, 1.0), 3)

    if score >= 0.90:
        risk = "⚫ Malicious/Severe"
    elif score >= 0.70:
        risk = "🔴 Slop"
    elif score >= 0.40:
        risk = "🟠 Suspicious"
    elif score >= 0.25:
        risk = "🟡 AI-Assisted"
    else:
        risk = "🟢 Clean"

    if score >= 0.70:
        action = "Do not cite. Do not store as fact. Require independent verification."
    elif score >= 0.40:
        action = "Use only as weak signal. Cross-check with primary sources."
    elif score >= 0.25:
        action = "Use with cross-checking."
    else:
        action = "Normal use, standard source checks apply."

    return {
        "slop_score": score,
        "risk_level": risk,
        "action": action,
        "dimensions": {
            "information_density": round(density, 3),
            "repetition_ratio": round(rep, 3),
            "burstiness": round(burst, 2),
            "buzzword_count": buzz_count,
            "phrase_match_count": total_phrases,
            "multilingual_matches": total_multi,
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
            "structural_slop": round(struct_slop, 3),
        },
        "signals": {
            "buzzword_hits": buzz_hits,
            "buzzword_tiers": buzz_tiers,
            "phrase_categories": phrase_matches,
            "multilingual": multilingual_matches,
            "authority_phrases": [p for p in AUTHORITY_PATTERNS if p in text.lower()],
            "moral_detected": moral_slop == 1.0,
            "list_heavy": list_slop == 1.0,
            "mirrored_intro_conclusion": mirrored_slop == 1.0,
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

    if args[0] == "-":
        text = sys.stdin.read()
    else:
        text = " ".join(args)

    result = slop_score(text)

    if use_json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))
