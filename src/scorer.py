"""
AI Slop Scoring Engine — dimension measurements and signal detection.

Lower-level than classifier.py — provides individual scoring functions
that can be composed into custom detection pipelines.
"""

import re
from collections import Counter
from typing import Optional


# Signal entries may carry placeholders: [X] stands for one word, [N] for a
# number ("here are [N] ways", "in the age of [X]"). Without expansion these
# entries are escaped literally and can never match (review 2026-08 §1.2).
_PLACEHOLDER = re.compile(r'\[[xn]\]')
_PLACEHOLDER_REGEX = {'[x]': r'[\w-]+', '[n]': r'\d+'}


def _term_pattern(term: str) -> str:
    """Regex for a term with word boundaries where the term edge is a word char.

    [X] expands to one word, [N] to a number; an empty term never matches.
    """
    t = term.lower().strip()
    if not t:
        return r'(?!)'
    parts, pos = [], 0
    for m in _PLACEHOLDER.finditer(t):
        parts.append(re.escape(t[pos:m.start()]))
        parts.append(_PLACEHOLDER_REGEX[m.group(0)])
        pos = m.end()
    parts.append(re.escape(t[pos:]))
    body = ''.join(parts)
    left = r'\b' if (t[0].isalnum() or t[0] == '[') else ''
    right = r'\b' if (t[-1].isalnum() or t[-1] == ']') else ''
    return left + body + right


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


# The aggregate lives in src/classifier.py (SlopClassifier), which reads the
# tiers, phrases and severities from ontology.json and aggregates with
# noisy-OR. A second, hand-weighted slop_score() with its own 14-word buzzword
# list used to sit here; nothing but its own demo ever called it, so it is
# gone rather than pretending to be a second supported entry point
# (review 2026-08 §3.4).


if __name__ == "__main__":
    import json

    from classifier import SlopClassifier

    demo = """In today's fast-paced digital landscape, leveraging cutting-edge AI solutions
    is paramount for businesses seeking to unlock their full potential. The key is to
    find balance between innovation and practicality, as studies have shown that a robust
    approach can deliver game-changing results."""

    result = SlopClassifier("ontology.json").classify_text(demo)
    print(json.dumps({
        "slop_score": result.overall_slop_score,
        "severity": result.severity,
        "signals": [s.signal_id for s in result.signals_detected],
        "dimensions": {k: v.value for k, v in result.dimensions.items()},
    }, indent=2))
