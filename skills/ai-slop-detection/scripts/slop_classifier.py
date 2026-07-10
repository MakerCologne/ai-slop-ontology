#!/usr/bin/env python3
"""
AI Slop Classifier v2 — Extended slop types from AI Slop Ontology v1.0.0.

Usage:
    python3 slop_classifier.py "Text to analyze"
    python3 slop_classifier.py --json "Text to analyze"
    echo "text" | python3 slop_classifier.py -

Returns: slop types, detected signals, severity, countermeasures.
"""

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from slop_scorer import (
    BUZZWORD_TIERS, PHRASE_CATEGORIES, MULTILINGUAL_BUZZWORDS,
    MORAL_PATTERNS, AUTHORITY_PATTERNS,
    buzzword_score, phrase_category_score, multilingual_buzzword_score,
    information_density, burstiness, trailing_moral, list_heavy,
    punctuation_anomaly_score, mirrored_intro_conclusion, find_term_matches,
)


@dataclass
class SignalMatch:
    signal_id: str
    confidence: float
    evidence: str


@dataclass
class SlopType:
    name: str
    score: float
    description: str


@dataclass
class ClassificationResult:
    slop_types: list = field(default_factory=list)
    signals: list = field(default_factory=list)
    severity: str = "clean"
    score: float = 0.0
    countermeasures: list = field(default_factory=list)
    notes: list = field(default_factory=list)


# --- Slop Type Pattern Definitions (extended from ontology.json v1.0.0) ---

SLOP_TYPE_PATTERNS = {
    "GenericSlop": {
        "patterns": [],
        "description": "Generic AI text with buzzwords, low density, uniform structure",
    },
    "SEOContentFarmSlop": {
        "patterns": ["in this article", "we will explore", "table of contents", "let's dive in",
                      "let's break it down", "here are", "top reasons"],
        "description": "SEO-optimized content farm article with no original reporting",
    },
    "AcademicSlop": {
        "patterns": ["novel approaches", "growing body of literature", "proposing a framework",
                      "existing paradigms", "contemporary challenges", "this paper contributes"],
        "description": "AI academic text that could describe any paper in any field",
    },
    "PseudoInsightSlop": {
        "patterns": [],
        "description": "Fake insights that sound profound but say nothing",
    },
    "FakeAuthoritySlop": {
        "patterns": ["studies have shown", "research shows", "experts say",
                      "it has been proven", "scientists have found", "a growing body of evidence"],
        "description": "Unsubstantiated authority claims without real citations",
    },
    "WellnessSlop": {
        "patterns": ["self-care", "isn't selfish", "journey", "embrace your", "inner peace",
                      "mindful", "holistic approach", "cultivating", "fostering"],
        "description": "AI-generated wellness/lifestyle content",
    },
    "WikipediaRehash": {
        "patterns": ["is defined as", "is known as", "refers to", "can be described as"],
        "description": "Rephrased common knowledge with no originality",
    },
    "EngagementClickbaitSlop": {
        "patterns": ["please like", "share if", "nobody helped", "amazing reaction",
                      "you won't believe", "mind-blowing", "here's the kicker"],
        "description": "Engagement-bait content designed for social media virality",
    },
    "PropagandaDisinfoSlop": {
        "patterns": ["they don't want you to know", "wake up", "the truth about",
                      "mainstream media won't", "what they're hiding"],
        "description": "AI-generated disinformation or propaganda content",
    },
    "Workslop": {
        "patterns": ["per my last email", "circling back", "touching base",
                      "action items", "moving forward", "on the same page",
                      "synergize", "circle back", "align on", "connect offline"],
        "description": "AI-generated workplace communication (performance theater)",
    },
    "LegalSlop": {
        "patterns": ["it is well established", "precedent clearly shows",
                      "the court has consistently held", "established jurisprudence"],
        "description": "AI-generated legal content with fabricated precedents — ESPECIALLY DANGEROUS",
    },
    "LinkedInSlop": {
        "patterns": ["thrilled to announce", "humbled to share", "excited to share",
                      "key takeaway", "game-changer", "grateful for the opportunity"],
        "description": "LinkedIn-style inspirational posts with zero substance",
    },
    "SecurityReportSlop": {
        "patterns": ["potential vulnerability", "could potentially allow", "may lead to remote code execution",
                      "this vulnerability could", "an attacker could potentially", "severity: critical",
                      "responsible disclosure", "proof of concept below"],
        "description": "AI-generated vulnerability reports that sound technical but contain nothing "
                       "actionable (curl killed its bug bounty over these, Feb 2026)",
    },
    "PeerReviewSlop": {
        "patterns": ["the authors present", "this paper addresses an important",
                      "the manuscript is well written", "minor revisions", "the contribution is unclear",
                      "would benefit from additional experiments", "the related work section"],
        "description": "AI-generated peer reviews: narrow, generic feedback without engagement "
                       "with the actual content (Organization Science 2026: >30% of reviews AI-involved)",
    },
}


def classify_text(text: str) -> ClassificationResult:
    result = ClassificationResult()
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    total_words = len(words)
    unique_words = len(set(words))
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    num_sentences = len(sentences) or 1

    # --- Signal Detection ---

    # 1. Buzzword Overuse (using extended tiers)
    buzz_count, buzz_hits, buzz_tiers = buzzword_score(text)
    if buzz_count >= 3:
        evidence = f"Found {buzz_count}: " + ", ".join(buzz_hits[:10])
        result.signals.append(SignalMatch("BuzzwordOveruse", 0.8 + min(buzz_count * 0.02, 0.15), evidence))

    # 2. AI Phrase Patterns (6 categories)
    phrase_matches = phrase_category_score(text)
    total_phrases = sum(len(v) for v in phrase_matches.values())
    if total_phrases >= 2:
        all_phrases = [p for phrases in phrase_matches.values() for p in phrases]
        evidence = f"Found {total_phrases}: " + ", ".join(all_phrases[:8])
        result.signals.append(SignalMatch("AIPhrasePattern", 0.75 + min(total_phrases * 0.02, 0.15), evidence))

    # 3. Punctuation Anomaly
    punct = punctuation_anomaly_score(text)
    if punct["emDashRate"] > 0.5:
        em_dashes = text.count('\u2014') + text.count('\u2013')
        result.signals.append(SignalMatch("PunctuationAnomaly", 0.85,
                                          f"Em-dash usage: {em_dashes} in {num_sentences} sentences"))

    # 4. Uniform Sentence Length (>= 5 sentences: below that, near-zero
    # variance is expected and short factual texts get falsely flagged)
    if len(sentences) >= 5:
        burst = burstiness(text)
        if burst < 3:
            lengths = [len(s.split()) for s in sentences]
            mean_len = sum(lengths) / len(lengths)
            result.signals.append(SignalMatch("UniformSentenceLength", 0.7,
                                              f"All sentences {int(mean_len)-2}-{int(mean_len)+2} words, burstiness={burst:.1f}"))

    # 5. Low Information Density
    if total_words > 0:
        density = unique_words / total_words
        if density < 0.40:
            result.signals.append(SignalMatch("LowDensity", 0.75, f"Information density: {density:.2f} (< 0.40)"))

    # 6. Trailing Moral
    if trailing_moral(text):
        result.signals.append(SignalMatch("TrailingMoral", 0.8, "Text ends with generic moral/lesson statement"))

    # 7. Excessive Lists
    if list_heavy(text):
        result.signals.append(SignalMatch("ExcessiveLists", 0.75, "Over 40% of lines are list items"))

    # 8. Mirrored Intro/Conclusion
    if mirrored_intro_conclusion(text):
        result.signals.append(SignalMatch("MirroredIntroConclusion", 0.75,
                                          "Conclusion restates introduction with synonym substitution"))

    # 9. Multilingual Artifacts
    multi_matches = multilingual_buzzword_score(text)
    total_multi = sum(len(v) for v in multi_matches.values())
    if total_multi >= 2:
        all_multi = [p for phrases in multi_matches.values() for p in phrases]
        result.signals.append(SignalMatch("MultilingualArtifacts", 0.7,
                                          f"Non-English AI patterns: {', '.join(all_multi)}"))

    # 10. Fake Authority
    authority_hits = sorted(find_term_matches(text_lower, AUTHORITY_PATTERNS))
    if authority_hits:
        result.signals.append(SignalMatch("FakeAuthorityPattern", 0.8,
                                          f"Unsubstantiated authority: {', '.join(authority_hits)}"))

    # --- Slop Type Classification ---
    type_scores = {}

    # Pattern-based types
    for type_name, type_def in SLOP_TYPE_PATTERNS.items():
        if not type_def["patterns"]:
            continue
        hits = len(find_term_matches(text_lower, type_def["patterns"]))
        if hits >= 1:
            type_scores[type_name] = min(0.3 + hits * 0.15, 0.95)

    # Composite types
    # GenericSlop: buzzwords + low density + uniform
    generic_score = 0
    if any(s.signal_id == "BuzzwordOveruse" for s in result.signals):
        generic_score += 0.35
    if any(s.signal_id == "LowDensity" for s in result.signals):
        generic_score += 0.25
    if any(s.signal_id == "UniformSentenceLength" for s in result.signals):
        generic_score += 0.2
    if any(s.signal_id == "AIPhrasePattern" for s in result.signals):
        generic_score += 0.2
    if generic_score >= 0.3:
        type_scores["GenericSlop"] = generic_score

    # PseudoInsightSlop
    pseudo_score = 0
    if any(s.signal_id == "LowDensity" for s in result.signals):
        pseudo_score += 0.25
    if any(s.signal_id == "AIPhrasePattern" for s in result.signals):
        pseudo_score += 0.35
    if any(s.signal_id == "TrailingMoral" for s in result.signals):
        pseudo_score += 0.25
    if any(s.signal_id == "MirroredIntroConclusion" for s in result.signals):
        pseudo_score += 0.15
    if pseudo_score >= 0.3:
        type_scores["PseudoInsightSlop"] = pseudo_score

    # --- Score Calculation ---
    signal_score = len(result.signals) / 6
    type_score = sum(type_scores.values()) / max(len(type_scores), 1) * 0.6 + (0.4 if type_scores else 0)
    dimension_count = 0
    if total_words > 0 and unique_words / total_words < 0.40:
        dimension_count += 1
    if total_words > 0:
        counts = Counter(words)
        if counts.most_common(1)[0][1] / total_words > 0.20:
            dimension_count += 1

    dimension_score = dimension_count / 2
    result.score = round(min(signal_score * 0.4 + dimension_score * 0.2 + min(type_score, 1.0) * 0.4, 1.0), 2)

    # Two or more distinctive patterns of a single slop type (score >= 0.6,
    # e.g. "precedent clearly shows" + "the court has consistently held") are
    # decisive on their own, even when generic dimensions stay quiet.
    if type_scores and max(type_scores.values()) >= 0.6:
        result.score = max(result.score, 0.45)

    # Severity
    if result.score >= 0.80:
        result.severity = "critical"
    elif result.score >= 0.60:
        result.severity = "high"
    elif result.score >= 0.40:
        result.severity = "medium"
    elif result.score >= 0.20:
        result.severity = "low"
    else:
        result.severity = "clean"

    # Types
    result.slop_types = sorted(
        [SlopType(name, round(score, 2), SLOP_TYPE_PATTERNS.get(name, {}).get("description", ""))
         for name, score in type_scores.items() if score >= 0.3],
        key=lambda t: t.score,
        reverse=True,
    )

    # Countermeasures
    if result.severity in ("critical", "high"):
        result.countermeasures = ["Do not cite as source", "Find independent verification",
                                  "Do not store in memory as fact"]
    elif result.severity == "medium":
        result.countermeasures = ["Cross-check with primary sources", "Use only as weak signal"]
    elif result.severity == "low":
        result.countermeasures = ["Standard source quality checks"]
    else:
        result.countermeasures = []

    return result


def format_report(result: ClassificationResult) -> str:
    lines = [
        f"🔬 Slop Classification v2",
        f"Severity: {result.severity.upper()} | Score: {result.score}",
        "",
    ]

    if result.slop_types:
        lines.append("📋 Slop Types:")
        for t in result.slop_types:
            lines.append(f"  • {t.name} ({t.score}) — {t.description}")
    else:
        lines.append("📋 No significant slop types detected")

    if result.signals:
        lines.append(f"\n📡 Signals ({len(result.signals)}):")
        for s in result.signals:
            lines.append(f"  ⚠️ {s.signal_id} ({s.confidence:.0%}) — {s.evidence}")

    if result.countermeasures:
        lines.append(f"\n🛡️ Recommended actions:")
        for c in result.countermeasures:
            lines.append(f"  → {c}")

    return "\n".join(lines)


def to_dict(result: ClassificationResult) -> dict:
    return {
        "severity": result.severity,
        "score": result.score,
        "slop_types": [{"name": t.name, "score": t.score, "description": t.description} for t in result.slop_types],
        "signals": [{"signal": s.signal_id, "confidence": s.confidence, "evidence": s.evidence} for s in result.signals],
        "countermeasures": result.countermeasures,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 slop_classifier.py \"Text to analyze\"")
        print("       echo \"text\" | python3 slop_classifier.py -")
        print("       python3 slop_classifier.py --json \"Text to analyze\"")
        sys.exit(1)

    use_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--json"]

    if args[0] == "-":
        text = sys.stdin.read()
    else:
        text = " ".join(args)

    result = classify_text(text)

    if use_json:
        print(json.dumps(to_dict(result), indent=2))
    else:
        print(format_report(result))
