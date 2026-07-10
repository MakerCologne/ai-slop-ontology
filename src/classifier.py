"""
AI Slop Classifier v1.2 — uses the AI Slop Ontology signal database.

v1.2: severity-weighted scoring per the documented formula, word-boundary
matching with overlap deduplication, multilingual case-insensitivity fix.

Usage:
    from classifier import SlopClassifier

    classifier = SlopClassifier("ontology.json")
    result = classifier.classify_text("In today's fast-paced digital landscape...")
    print(result)
"""

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

try:
    from scorer import find_term_matches
except ImportError:  # allow import as package module
    from src.scorer import find_term_matches


def _trailing_moral(text):
    text_lower = text.lower().strip()
    moral_patterns = ["remember that", "in the end", "ultimately", "the lesson is",
                      "what matters most", "at the end of the day", "it's important to remember"]
    return any(p in text_lower[-200:] for p in moral_patterns)


def _list_heavy(text):
    lines = text.strip().split('\n')
    list_lines = sum(1 for l in lines if re.match(r'^\s*[-*•]\s|^\s*\d+[.)]\s', l))
    return len(lines) > 3 and list_lines / len(lines) > 0.4


@dataclass
class SignalMatch:
    signal_id: str
    confidence: float
    evidence: str
    severity: str = "medium"  # critical | high | medium | low


# Severity assignment per signal type, used by the documented scoring formula
# slop_score = min(1.0, sum(weights[severity] * confidence) / max(1, n))
SIGNAL_SEVERITY = {
    "CriticalBuzzword": "critical",
    "BuzzwordOveruse_Severe": "high",
    "BuzzwordOveruse": "medium",
    "PhrasePatternSevere": "high",
    "PhrasePattern": "medium",
    "ExcessiveHedging": "medium",
    "MetaphorAbuse": "medium",
    "FakeAuthorityPattern": "high",
    "EmDashExcess": "medium",
    "EllipsisExcess": "low",
    "ExclamationExcess": "low",
    "UniformSentenceLength": "medium",
    "TrailingMoral": "low",
    "ListHeavy": "low",
    "InventedPackage": "critical",
    "HardcodedSecret": "critical",
    "ExcessiveComments": "low",
}

SEVERITY_WEIGHTS = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}


def _severity_for(signal_id: str) -> str:
    # A multilingual hit means >= 2 language-specific AI markers matched;
    # since all other signals are English-based, this is strong evidence.
    if signal_id.startswith("Multilingual_"):
        return "high"
    return SIGNAL_SEVERITY.get(signal_id, "medium")


@dataclass
class DimensionResult:
    name: str
    value: float
    is_slop: bool
    threshold: str = ""
    note: str = ""


@dataclass
class ClassificationResult:
    modality: str
    slop_types: list[str] = field(default_factory=list)
    signals_detected: list[SignalMatch] = field(default_factory=list)
    dimensions: dict[str, DimensionResult] = field(default_factory=dict)
    overall_slop_score: float = 0.0
    severity: str = "clean"
    countermeasures: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    buzzword_report: dict = field(default_factory=dict)
    phrase_report: dict = field(default_factory=dict)


class SlopClassifier:
    """Classify content using the AI Slop Ontology signal database."""

    def __init__(self, ontology_path: str = "ontology.json"):
        with open(ontology_path) as f:
            self.ontology = json.load(f)
        self._load_signals()

    def _load_signals(self):
        """Pre-compile all signal patterns from the ontology."""
        sigs = self.ontology["signals"]
        text_sigs = sigs["text"]

        # --- Buzzwords (all tiers) ---
        self.buzzword_tiers = {}
        self.buzzword_confidence = {}
        tiers = text_sigs["buzzwords"]["tiers"]
        for tier_name, tier_data in tiers.items():
            words = tier_data["words"]
            self.buzzword_tiers[tier_name] = [w.lower() for w in words]
            self.buzzword_confidence[tier_name] = tier_data.get("confidence", 0.5)

        # --- Phrases (all categories) ---
        self.phrase_categories = {}
        self.phrase_confidence = {}
        phrase_cats = text_sigs["phrases"]["categories"]
        for cat_name, cat_data in phrase_cats.items():
            self.phrase_categories[cat_name] = [p.lower() for p in cat_data["items"]]
            self.phrase_confidence[cat_name] = cat_data.get("confidence", 0.5)

        # --- Structural indicators ---
        self.structural_indicators = text_sigs.get("structural", {}).get("indicators", [])

        # --- Punctuation thresholds ---
        self.punctuation_indicators = text_sigs.get("punctuation", {}).get("indicators", [])

        # --- Multilingual ---
        self.multilingual = sigs.get("multilingual", {})

    def classify_text(self, text: str) -> ClassificationResult:
        """Classify a text for AI slop using the full signal database."""
        result = ClassificationResult(modality="text")

        text_lower = text.lower()
        words = re.findall(r'\b[\w-]+\b', text_lower)
        total_words = len(words)
        unique_words = len(set(words))
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        num_sentences = len(sentences) or 1

        # ============================================================
        # 1. BUZZWORD DETECTION (all tiers)
        # ============================================================
        buzzword_hits = []  # (word, tier, count, confidence)
        tier_summary = {}

        # Match all tiers jointly with word boundaries; overlapping terms
        # ("tapestry" inside "rich tapestry") count once for the longest match.
        term_to_tier = {}
        all_terms = []
        for tier_name, tier_words in self.buzzword_tiers.items():
            for w in tier_words:
                term_to_tier[w] = tier_name
                all_terms.append(w)
        matched = find_term_matches(text_lower, all_terms)
        for w, count in matched.items():
            tier_name = term_to_tier[w]
            tier_summary.setdefault(tier_name, []).append((w, count))
            buzzword_hits.append((w, tier_name, count, self.buzzword_confidence[tier_name]))

        result.buzzword_report = tier_summary

        if buzzword_hits:
            # Weight by tier confidence
            weighted_score = sum(conf * min(count, 3) for _, _, count, conf in buzzword_hits)
            max_possible = sum(self.buzzword_confidence.get(t, 0.5) * 3 for _, t, _, _ in buzzword_hits)
            normalized = min(1.0, weighted_score / max(max_possible, 1))

            hit_words = [w for w, _, _, _ in buzzword_hits]
            unique_hits = len(set(hit_words))

            # Escalation rules
            critical_hits = [w for w, t, _, _ in buzzword_hits if "critical" in t]
            if critical_hits:
                result.signals_detected.append(SignalMatch(
                    "CriticalBuzzword", 0.90,
                    f"Tier1 hit(s): {', '.join(set(critical_hits))}"
                ))

            if unique_hits >= 5:
                result.signals_detected.append(SignalMatch(
                    "BuzzwordOveruse_Severe", 0.85 + min(unique_hits * 0.01, 0.10),
                    f"{unique_hits} unique buzzwords: {', '.join(set(hit_words[:10]))}"
                ))
            elif unique_hits >= 3:
                result.signals_detected.append(SignalMatch(
                    "BuzzwordOveruse", 0.75 + min(unique_hits * 0.02, 0.15),
                    f"Found: {', '.join(set(hit_words))}"
                ))

        # ============================================================
        # 2. PHRASE PATTERN DETECTION (all categories)
        # ============================================================
        phrase_hits = {}
        total_phrase_hits = 0

        term_to_cats = {}
        all_phrases = []
        for cat_name, phrases in self.phrase_categories.items():
            for p in phrases:
                term_to_cats.setdefault(p, []).append(cat_name)
                all_phrases.append(p)
        for p in find_term_matches(text_lower, all_phrases):
            for cat_name in term_to_cats[p]:
                phrase_hits.setdefault(cat_name, []).append(p)
                total_phrase_hits += 1

        result.phrase_report = phrase_hits

        if total_phrase_hits >= 4:
            hit_list = [f"{cat}: {len(items)}" for cat, items in phrase_hits.items()]
            result.signals_detected.append(SignalMatch(
                "PhrasePatternSevere", 0.85,
                f"4+ phrase categories hit: {'; '.join(hit_list)}"
            ))
        elif total_phrase_hits >= 2:
            all_phrases = [p for items in phrase_hits.values() for p in items]
            result.signals_detected.append(SignalMatch(
                "PhrasePattern", 0.75,
                f"Found: {', '.join(all_phrases[:8])}"
            ))

        # Category-specific signals
        if "hedging_qualifiers" in phrase_hits and len(phrase_hits["hedging_qualifiers"]) >= 3:
            result.signals_detected.append(SignalMatch(
                "ExcessiveHedging", 0.70,
                f"Hedging phrases: {', '.join(phrase_hits['hedging_qualifiers'])}"
            ))

        if "metaphor_abuse" in phrase_hits and len(phrase_hits["metaphor_abuse"]) >= 2:
            result.signals_detected.append(SignalMatch(
                "MetaphorAbuse", 0.75,
                f"Tapestry-style metaphors: {', '.join(phrase_hits['metaphor_abuse'])}"
            ))

        if "authority_claims" in phrase_hits and len(phrase_hits["authority_claims"]) >= 2:
            result.signals_detected.append(SignalMatch(
                "FakeAuthorityPattern", 0.80,
                f"Unsubstantiated authority: {', '.join(phrase_hits['authority_claims'])}"
            ))

        # ============================================================
        # 3. PUNCTUATION ANOMALIES
        # ============================================================
        em_dashes = text.count('—') + text.count('–')
        if em_dashes / num_sentences > 0.5:
            result.signals_detected.append(SignalMatch(
                "EmDashExcess", 0.85,
                f"Em-dash usage: {em_dashes} in {num_sentences} sentences ({em_dashes/num_sentences:.1f}/sentence)"
            ))

        ellipses = text.count('...')
        if ellipses / num_sentences > 0.3:
            result.signals_detected.append(SignalMatch(
                "EllipsisExcess", 0.70,
                f"Ellipsis usage: {ellipses} in {num_sentences} sentences"
            ))

        exclamations = text.count('!')
        if exclamations / num_sentences > 0.2:
            result.signals_detected.append(SignalMatch(
                "ExclamationExcess", 0.65,
                f"Exclamation usage: {exclamations} in {num_sentences} sentences"
            ))

        # ============================================================
        # 4. STRUCTURAL INDICATORS
        # ============================================================
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            # Require >= 5 sentences: with fewer, near-zero variance is expected
            # and short factual texts would be falsely flagged as uniform.
            if len(lengths) >= 5:
                mean_len = sum(lengths) / len(lengths)
                variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
                std_dev = variance ** 0.5
                if std_dev < 3:
                    result.signals_detected.append(SignalMatch(
                        "UniformSentenceLength", 0.70,
                        f"All sentences {int(mean_len)-2}-{int(mean_len)+2} words, std_dev={std_dev:.1f}"
                    ))

        # Trailing moral
        if _trailing_moral(text):
            result.signals_detected.append(SignalMatch(
                "TrailingMoral", 0.70,
                "Ends with moral/lesson statement"
            ))

        # List-heavy
        if _list_heavy(text):
            result.signals_detected.append(SignalMatch(
                "ListHeavy", 0.50,
                ">40% list items in text"
            ))

        # ============================================================
        # 5. MULTILINGUAL CHECK
        # ============================================================
        for lang, lang_data in self.multilingual.items():
            if isinstance(lang_data, dict) and "buzzwords" in lang_data:
                lang_hits = sorted(find_term_matches(
                    text_lower, [w.lower() for w in lang_data["buzzwords"]]))
                if len(lang_hits) >= 2:
                    result.signals_detected.append(SignalMatch(
                        f"Multilingual_{lang}", 0.70,
                        f"{lang} AI markers: {', '.join(lang_hits)}"
                    ))

        # ============================================================
        # 6. DIMENSION MEASUREMENT
        # ============================================================
        if total_words > 0:
            density = unique_words / total_words
            result.dimensions["Density"] = DimensionResult(
                "Density", round(density, 2), density < 0.40, "< 0.40",
                f"{unique_words}/{total_words} unique/total"
            )

            word_counts = Counter(words)
            most_common_ratio = word_counts.most_common(1)[0][1] / total_words
            result.dimensions["Repetition"] = DimensionResult(
                "Repetition", round(most_common_ratio, 2), most_common_ratio > 0.20, "> 0.20"
            )

        # ============================================================
        # 7. SCORE CALCULATION
        # ============================================================
        # Noisy-OR aggregation (ontology §6): independent pieces of evidence
        # accumulate instead of being averaged away — a mean-based formula let
        # three medium signals cancel each other down to ~0.29. Escalation for
        # any critical signal or >= 2 high-severity signals still applies.
        for s in result.signals_detected:
            s.severity = _severity_for(s.signal_id)

        if result.signals_detected:
            no_slop_prob = 1.0
            for s in result.signals_detected:
                no_slop_prob *= 1.0 - SEVERITY_WEIGHTS[s.severity] * s.confidence
            result.overall_slop_score = min(1.0, round(1.0 - no_slop_prob, 4))

            has_critical = any(s.severity == "critical" for s in result.signals_detected)
            high_count = sum(1 for s in result.signals_detected if s.severity in ("critical", "high"))
            if has_critical or high_count >= 2:
                result.overall_slop_score = max(result.overall_slop_score, 0.70)

            if result.overall_slop_score >= 0.70:
                result.severity = "slop_candidate"
                result.countermeasures = ["exclude_from_rag", "do_not_cite", "label_as_ai"]
            elif result.overall_slop_score >= 0.40:
                result.severity = "suspicious"
                result.countermeasures = ["require_human_review", "cross_check_sources"]
            elif result.overall_slop_score >= 0.25:
                result.severity = "ai_assisted"
                result.countermeasures = ["source_check_recommended"]
            else:
                result.severity = "clean"
                result.countermeasures = ["standard_quality_check"]
        else:
            result.overall_slop_score = 0.0
            result.severity = "clean"
            result.countermeasures = ["standard_quality_check"]

        return result

    def classify_code(self, code: str, language: str = "") -> ClassificationResult:
        """Classify code for AI slop patterns."""
        result = ClassificationResult(modality="code")

        code_sigs = self.ontology["signals"].get("code", {}).get("indicators", [])

        # Check for invented packages
        import_patterns = re.findall(r'(?:import|from|require|use)\s+["\']?([a-zA-Z0-9_-]+)', code)
        known_examples = []
        for sig in code_sigs:
            if sig.get("id") == "InventedPackage":
                known_examples = sig.get("knownExamples", [])

        invented = [p for p in import_patterns if p in known_examples]
        if invented:
            result.signals_detected.append(SignalMatch(
                "InventedPackage", 1.0,
                f"Hallucinated packages: {', '.join(invented)}"
            ))

        # Hardcoded secrets
        if re.search(r'(?:api[_-]?key|password|secret|token)\s*[:=]\s*["\'][^"\']{8,}', code, re.I):
            result.signals_detected.append(SignalMatch(
                "HardcodedSecret", 0.95, "API key or password found in code"
            ))

        # Excessive comments
        comment_lines = len(re.findall(r'^\s*//|^\s*#|^\s*/\*', code, re.MULTILINE))
        code_lines = len([l for l in code.split('\n') if l.strip() and not l.strip().startswith(('#', '//'))])
        if code_lines > 0 and comment_lines / code_lines > 0.8:
            result.signals_detected.append(SignalMatch(
                "ExcessiveComments", 0.60,
                f"Comment/code ratio: {comment_lines}/{code_lines}"
            ))

        # Score (noisy-OR, same aggregation as classify_text)
        for s in result.signals_detected:
            s.severity = _severity_for(s.signal_id)
        if result.signals_detected:
            no_slop_prob = 1.0
            for s in result.signals_detected:
                no_slop_prob *= 1.0 - SEVERITY_WEIGHTS[s.severity] * s.confidence
            result.overall_slop_score = min(1.0, round(1.0 - no_slop_prob, 4))
            if any(s.severity == "critical" for s in result.signals_detected):
                result.overall_slop_score = max(result.overall_slop_score, 0.70)
            if result.overall_slop_score >= 0.70:
                result.severity = "slop_candidate"
            elif result.overall_slop_score >= 0.40:
                result.severity = "suspicious"
            else:
                result.severity = "ai_assisted"

        return result

    def get_signal_stats(self) -> dict:
        """Return statistics about the loaded signal database."""
        total_buzzwords = sum(len(words) for words in self.buzzword_tiers.values())
        total_phrases = sum(len(phrases) for phrases in self.phrase_categories.values())
        return {
            "buzzwords": total_buzzwords,
            "buzzword_tiers": list(self.buzzword_tiers.keys()),
            "phrase_categories": list(self.phrase_categories.keys()),
            "total_phrases": total_phrases,
            "structural_indicators": len(self.structural_indicators),
            "punctuation_indicators": len(self.punctuation_indicators),
            "languages": [k for k, v in self.multilingual.items()
                          if isinstance(v, dict) and "buzzwords" in v],
            "total_signals": total_buzzwords + total_phrases + len(self.structural_indicators) + len(self.punctuation_indicators)
        }


if __name__ == "__main__":
    import sys

    classifier = SlopClassifier(sys.argv[1] if len(sys.argv) > 1 else "ontology.json")
    stats = classifier.get_signal_stats()
    print(f"=== AI Slop Classifier v1.2 ===")
    print(f"Signal database: {stats['total_signals']} total signals")
    print(f"  Buzzwords: {stats['buzzwords']} across {len(stats['buzzword_tiers'])} tiers")
    print(f"  Phrases: {stats['total_phrases']} across {len(stats['phrase_categories'])} categories")
    print(f"  Structural: {stats['structural_indicators']}")
    print(f"  Punctuation: {stats['punctuation_indicators']}")
    print(f"  Languages: {', '.join(stats['languages'])}")
    print()

    # Demo
    test = """In today's rapidly evolving digital landscape, it's important to note that 
    the rich tapestry of AI tools serves as a testament to innovation. Whether you're a 
    seasoned developer or just starting out, let's dive into how these cutting-edge 
    solutions can unlock your potential and harness the power of transformative technology. 
    At its core, this paradigm shift is paramount to navigating the landscape of modern 
    software development. Furthermore, it's crucial to understand the multifaceted nature 
    of these robust, seamless, and holistic platforms."""

    result = classifier.classify_text(test)
    print(f"Slop Score: {result.overall_slop_score:.2f} ({result.severity})")
    print(f"Signals: {len(result.signals_detected)}")
    for s in result.signals_detected:
        print(f"  [{s.confidence:.2f}] {s.signal_id}: {s.evidence}")
    if result.buzzword_report:
        print(f"Buzzwords by tier:")
        for tier, hits in result.buzzword_report.items():
            print(f"  {tier}: {', '.join(f'{w} ({c}x)' for w, c in hits)}")
    if result.phrase_report:
        print(f"Phrases by category:")
        for cat, hits in result.phrase_report.items():
            print(f"  {cat}: {', '.join(hits)}")
