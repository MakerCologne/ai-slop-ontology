"""
AI Slop Classifier — uses the AI Slop Ontology to classify content.

Usage:
    from classifier import SlopClassifier

    classifier = SlopClassifier("ontology.json")
    result = classifier.classify_text("In today's fast-paced digital landscape...")
    print(result)
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SignalMatch:
    signal_id: str
    confidence: float
    evidence: str


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


class SlopClassifier:
    """Classify content using the AI Slop Ontology."""

    def __init__(self, ontology_path: str = "ontology.json"):
        with open(ontology_path) as f:
            self.ontology = json.load(f)
        self._load_text_patterns()

    def _load_text_patterns(self):
        """Pre-compile text signal patterns."""
        self.buzzword_tiers = {}
        for tier_name, words in self.ontology["signals"]["text"][0]["tiers"].items():
            self.buzzword_tiers[tier_name] = [w.lower() for w in words]

        self.generic_transitions = [
            p.lower() for p in self.ontology["signals"]["text"][1]["phrases"]
        ]

    def classify_text(self, text: str) -> ClassificationResult:
        """Classify a text for AI slop."""
        result = ClassificationResult(modality="text")

        # --- Signal Detection ---
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        unique_words = len(set(words))

        # 1. Buzzword Overuse
        buzzword_hits = []
        for tier, tier_words in self.buzzword_tiers.items():
            for w in tier_words:
                count = text_lower.count(w)
                if count > 0:
                    buzzword_hits.append((w, tier, count))

        if len(buzzword_hits) >= 3:
            evidence = f"Found: {', '.join(f'{w} ({t})' for w, t, c in buzzword_hits)}"
            result.signals_detected.append(SignalMatch(
                "BuzzwordOveruse", 0.8 + min(len(buzzword_hits) * 0.02, 0.15), evidence
            ))

        # 2. Generic Transitions
        transition_hits = [p for p in self.generic_transitions if p in text_lower]
        if len(transition_hits) >= 2:
            result.signals_detected.append(SignalMatch(
                "GenericTransition", 0.75,
                f"Found: {', '.join(transition_hits)}"
            ))

        # 3. Punctuation Anomaly
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        num_sentences = len(sentences) or 1
        em_dashes = text.count('—') + text.count('–')
        if em_dashes / num_sentences > 0.5:
            result.signals_detected.append(SignalMatch(
                "PunctuationAnomaly", 0.85,
                f"Em-dash usage: {em_dashes} in {num_sentences} sentences"
            ))

        # 4. Uniform Sentence Length
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            if len(lengths) >= 3:
                mean_len = sum(lengths) / len(lengths)
                variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
                std_dev = variance ** 0.5
                if std_dev < 3:
                    result.signals_detected.append(SignalMatch(
                        "UniformSentenceLength", 0.7,
                        f"All sentences {int(mean_len)-2}-{int(mean_len)+2} words, low burstiness"
                    ))

        # --- Dimension Measurement ---
        # Density
        if total_words > 0:
            density = unique_words / total_words
            result.dimensions["Density"] = DimensionResult(
                "Density", round(density, 2), density < 0.40, "< 0.40"
            )

        # Repetition
        if total_words > 0:
            from collections import Counter
            word_counts = Counter(words)
            most_common_ratio = word_counts.most_common(1)[0][1] / total_words
            result.dimensions["Repetition"] = DimensionResult(
                "Repetition", round(most_common_ratio, 2), most_common_ratio > 0.20, "> 0.20"
            )

        # Verbosity (approximation: avg words per sentence)
        if sentences:
            avg_sentence_len = total_words / num_sentences
            result.dimensions["Verbosity"] = DimensionResult(
                "Verbosity", round(avg_sentence_len / 30, 2),
                avg_sentence_len > 25, "> 25 words/sentence"
            )

        # --- Type Classification ---
        type_scores = {}
        text_types = self.ontology["slopTypes"]["TEXT_SLOP"]

        # GenericSlop: buzzwords + low density
        generic_score = 0
        if any(s.signal_id == "BuzzwordOveruse" for s in result.signals_detected):
            generic_score += 0.4
        if result.dimensions.get("Density", DimensionResult("", 1, False)).is_slop:
            generic_score += 0.3
        if any(s.signal_id == "UniformSentenceLength" for s in result.signals_detected):
            generic_score += 0.2
        type_scores["GenericSlop"] = generic_score

        # PseudoInsightSlop: low density + generic transitions
        pseudo_score = 0
        if result.dimensions.get("Density", DimensionResult("", 1, False)).is_slop:
            pseudo_score += 0.3
        if any(s.signal_id == "GenericTransition" for s in result.signals_detected):
            pseudo_score += 0.4
        type_scores["PseudoInsightSlop"] = pseudo_score

        # FakeAuthoritySlop: "studies have shown" pattern
        authority_patterns = ["studies have shown", "research shows", "experts say", "it has been proven"]
        if any(p in text_lower for p in authority_patterns):
            type_scores["FakeAuthoritySlop"] = 0.7
            result.signals_detected.append(SignalMatch(
                "FakeAuthorityPattern", 0.8,
                f"Found unsubstantiated authority claim"
            ))

        # WellnessSlop: wellness phrases
        wellness_patterns = ["self-care", "isn't selfish", "journey", "embrace", "inner"]
        wellness_hits = sum(1 for p in wellness_patterns if p in text_lower)
        if wellness_hits >= 2:
            type_scores["WellnessSlop"] = 0.6

        # WikipediaRehash: "is defined as" pattern + low density
        if "is defined as" in text_lower or "is known as" in text_lower:
            type_scores["WikipediaRehash"] = 0.5

        # Sort by score, keep significant ones
        result.slop_types = sorted(type_scores.keys(), key=lambda t: type_scores[t], reverse=True)
        result.slop_types = [t for t in result.slop_types if type_scores[t] >= 0.3]

        # --- Overall Score ---
        signal_score = len(result.signals_detected) / 5  # max 5 signals
        dimension_score = sum(1 for d in result.dimensions.values() if d.is_slop) / max(len(result.dimensions), 1)
        type_score = len(result.slop_types) / 3
        result.overall_slop_score = round(min((signal_score * 0.4 + dimension_score * 0.4 + type_score * 0.2), 1.0), 2)

        # --- Severity ---
        if result.overall_slop_score >= 0.8:
            result.severity = "critical"
        elif result.overall_slop_score >= 0.6:
            result.severity = "high"
        elif result.overall_slop_score >= 0.4:
            result.severity = "medium"
        elif result.overall_slop_score >= 0.2:
            result.severity = "low"
        else:
            result.severity = "clean"

        # --- Countermeasures ---
        if result.severity in ("critical", "high"):
            result.countermeasures = ["PromptEngineering", "QualityGates"]
        elif result.severity == "medium":
            result.countermeasures = ["HumanReview"]
        else:
            result.countermeasures = []

        return result

    def to_dict(self, result: ClassificationResult) -> dict:
        """Convert result to JSON-serializable dict matching ontology output format."""
        return {
            "modality": result.modality,
            "slopTypes": result.slop_types,
            "signalsDetected": [
                {"signal": s.signal_id, "confidence": s.confidence, "evidence": s.evidence}
                for s in result.signals_detected
            ],
            "dimensions": {
                name: {"value": d.value, "isSlop": d.is_slop, "threshold": d.threshold, "note": d.note}
                for name, d in result.dimensions.items()
            },
            "overallSlopScore": result.overall_slop_score,
            "severity": result.severity,
            "countermeasures": result.countermeasures
        }


if __name__ == "__main__":
    classifier = SlopClassifier("ontology.json")

    test_cases = [
        "In today's fast-paced digital landscape, leveraging cutting-edge AI solutions is paramount for businesses seeking to unlock their full potential. The key is to find balance between innovation and practicality.",
        "The quick brown fox jumps over the lazy dog. Python 3.12 adds new type syntax. Coffee tastes best when freshly ground.",
        "Recent studies have shown that self-care isn't selfish. In conclusion, the tapestry of life is a journey of a thousand miles."
    ]

    for i, text in enumerate(test_cases):
        result = classifier.classify_text(text)
        output = classifier.to_dict(result)
        print(f"\n--- Test {i+1} (score: {result.overall_slop_score}, severity: {result.severity}) ---")
        print(f"Types: {result.slop_types}")
        for s in result.signals_detected:
            print(f"  Signal: {s.signal_id} ({s.confidence:.0%}) — {s.evidence}")
