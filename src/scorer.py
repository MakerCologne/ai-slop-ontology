"""
AI Slop Scoring Engine — dimension measurements and signal detection.

Lower-level than classifier.py — provides individual scoring functions
that can be composed into custom detection pipelines.
"""

import re
from collections import Counter
from typing import Optional


# Placeholder expansion (issue #83). Phrases in ontology.json use [X] for a
# noun phrase and [N] for a count; re.escape() alone made them literal, so
# they could never match real text.
_PLACEHOLDER_RE = re.compile(r"\[([xn])\]")

# [X]: one to four words, lazily — a trailing [X] then consumes a single word
# instead of swallowing the rest of the clause, while a medial one grows only
# as far as the rest of the phrase requires. No sentence or clause boundary
# may be crossed.
_ANY_NOUN_PHRASE = r"\w[\w'-]*(?:\s+\w[\w'-]*){0,3}?"

# [N]: digits or a written-out count.
_ANY_COUNT = (r"\d{1,4}|one|two|three|four|five|six|seven|eight|nine|ten|"
              r"eleven|twelve|fifteen|twenty|thirty|fifty|hundred")


def _term_pattern(term: str) -> str:
    """Regex for a term with word boundaries where the term edge is a word char.

    [X] and [N] are expanded rather than escaped, so template phrases match
    the texts they describe (#83).
    """
    t = term.lower()
    parts, pos = [], 0
    for m in _PLACEHOLDER_RE.finditer(t):
        parts.append(re.escape(t[pos:m.start()]))
        body = _ANY_NOUN_PHRASE if m.group(1) == "x" else _ANY_COUNT
        parts.append("(?:" + body + ")")
        pos = m.end()
    parts.append(re.escape(t[pos:]))
    # A placeholder at either edge still begins/ends on a word character.
    left = r"\b" if (t[0].isalnum() or t.startswith(("[x]", "[n]"))) else ""
    right = r"\b" if (t[-1].isalnum() or t.endswith(("[x]", "[n]"))) else ""
    return left + "".join(parts) + right


def find_term_matches(text_lower: str, terms: list) -> dict:
    """
    Match terms with word boundaries and overlap suppression: if a longer term
    already covers a span (e.g. "rich tapestry"), a shorter term inside that
    span (e.g. "tapestry") is not counted again.

    Returns {term_lowercase: occurrence_count} for matched terms. Keys are
    lowercased so callers can index lookup tables built with lowered terms
    even when the input term list has mixed case.
    """
    spans = []
    for term in terms:
        for m in re.finditer(_term_pattern(term), text_lower):
            spans.append((m.start(), m.end(), term.lower()))
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
    term_to_tier = {}
    all_terms = []
    for tier_name, words in tiers.items():
        for w in words:
            term_to_tier[w.lower()] = tier_name
            all_terms.append(w)
    matched = find_term_matches(text_lower, all_terms)
    hits = [f"{term} ({term_to_tier[term]})" for term in matched]
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
    return bool(find_term_matches(tail, moral_patterns))


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
    num_sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
    density_slop = max(0, (0.50 - density) / 0.50)  # below 0.50 is increasingly slop
    rep_slop = min(1, rep / 0.30)  # above 0.30 is definitely slop
    # Burstiness is only meaningful with >= 3 sentences; neutral otherwise
    burst_slop = max(0, (5 - burst) / 5) if num_sentences >= 3 else 0.0
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
