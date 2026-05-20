"""
AI Slop Scoring Engine — dimension measurements and signal detection.

Lower-level than classifier.py — provides individual scoring functions
that can be composed into custom detection pipelines.
"""

import re
from collections import Counter
from typing import Optional


def information_density(text: str) -> float:
    """Unique words / total words. < 0.40 = slop."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def repetition_ratio(text: str) -> float:
    """Most common token / total tokens. > 0.20 = slop."""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    counts = Counter(words)
    return counts.most_common(1)[0][1] / len(words)


def burstiness(text: str) -> float:
    """Standard deviation of sentence lengths. Low = uniform (AI-like)."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    if len(sentences) < 2:
        return 0.0
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    return variance ** 0.5


def buzzword_score(text: str, tiers: dict[str, list[str]]) -> tuple[int, list[str]]:
    """Count buzzword occurrences across tiers. > 3 = generic slop."""
    text_lower = text.lower()
    hits = []
    for tier_name, words in tiers.items():
        for w in words:
            if w in text_lower:
                hits.append(f"{w} ({tier_name})")
    return len(hits), hits


def punctuation_anomaly_score(text: str) -> dict[str, float]:
    """Check em-dash, ellipsis, exclamation rates per sentence."""
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    n = len(sentences) or 1
    return {
        "emDashRate": (text.count('—') + text.count('–')) / n,
        "ellipsisRate": text.count('...') / n,
        "exclamationRate": text.count('!') / n,
    }


def trailing_moral(text: str) -> bool:
    """Check if text ends with a moral/lesson statement."""
    text_lower = text.lower().strip()
    moral_patterns = [
        "remember that", "in the end", "ultimately", "the lesson is",
        "what matters most", "at the end of the day", "it's important to remember"
    ]
    # Check last 200 chars
    tail = text_lower[-200:]
    return any(p in tail for p in moral_patterns)


def list_heavy(text: str) -> bool:
    """Check if text is overly reliant on lists (>40% list items)."""
    lines = text.strip().split('\n')
    list_lines = sum(1 for l in lines if re.match(r'^\s*[-*•]\s|^\s*\d+[.)]\s', l))
    return len(lines) > 3 and list_lines / len(lines) > 0.4


def slop_score(
    text: str,
    buzzword_tiers: Optional[dict] = None,
    weights: Optional[dict] = None
) -> dict:
    """
    Compute a comprehensive slop score for text.

    Returns dict with individual scores and overall score (0-1).
    """
    if buzzword_tiers is None:
        buzzword_tiers = {
            "tier1": ["delve", "realm", "tapestry", "landscape"],
            "tier2": ["unleash", "unlock", "harness", "leverage"],
            "tier3": ["paradigm", "synergy", "robust"],
            "tier4": ["cutting-edge", "state-of-the-art", "game-changing"]
        }

    if weights is None:
        weights = {
            "density": 0.25,
            "repetition": 0.15,
            "burstiness": 0.15,
            "buzzwords": 0.20,
            "punctuation": 0.10,
            "trailing_moral": 0.05,
            "list_heavy": 0.10
        }

    density = information_density(text)
    rep = repetition_ratio(text)
    burst = burstiness(text)
    buzz_count, buzz_hits = buzzword_score(text, buzzword_tiers)
    punct = punctuation_anomaly_score(text)

    # Normalize to 0-1 (higher = more slop)
    density_slop = max(0, (0.50 - density) / 0.50)  # below 0.50 is increasingly slop
    rep_slop = min(1, rep / 0.30)  # above 0.30 is definitely slop
    burst_slop = max(0, (5 - burst) / 5)  # below 5 is increasingly uniform
    buzz_slop = min(1, buzz_count / 6)  # 6+ buzzwords = definite slop
    punct_slop = min(1, (punct["emDashRate"] + punct["ellipsisRate"] + punct["exclamationRate"]) / 2)
    moral_slop = 1.0 if trailing_moral(text) else 0.0
    list_slop = 1.0 if list_heavy(text) else 0.0

    overall = (
        weights["density"] * density_slop +
        weights["repetition"] * rep_slop +
        weights["burstiness"] * burst_slop +
        weights["buzzwords"] * buzz_slop +
        weights["punctuation"] * punct_slop +
        weights["trailing_moral"] * moral_slop +
        weights["list_heavy"] * list_slop
    )

    return {
        "overall": round(min(overall, 1.0), 3),
        "dimensions": {
            "density": round(density, 3),
            "densitySlop": round(density_slop, 3),
            "repetition": round(rep, 3),
            "repetitionSlop": round(rep_slop, 3),
            "burstiness": round(burst, 2),
            "burstinessSlop": round(burst_slop, 3),
            "buzzwordCount": buzz_count,
            "buzzwordSlop": round(buzz_slop, 3),
            "punctuationSlop": round(punct_slop, 3),
            "trailingMoral": moral_slop == 1.0,
            "listHeavy": list_slop == 1.0,
        },
        "buzzwordHits": buzz_hits,
        "punctuationRates": punct,
    }


if __name__ == "__main__":
    test = """In today's fast-paced digital landscape, leveraging cutting-edge AI solutions
    is paramount for businesses seeking to unlock their full potential. The key is to
    find balance between innovation and practicality, as studies have shown that a robust
    approach can deliver game-changing results. It's important to note that self-care
    isn't selfish — it's a fundamental aspect of maintaining the synergy needed to thrive."""

    result = slop_score(test)
    import json
    print(json.dumps(result, indent=2))
