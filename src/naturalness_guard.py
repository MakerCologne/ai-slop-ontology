"""NATURALNESS GUARD — over-sanitization as advisory signal (issue #81).

The FP counterpart at the other end of the slop scale: a text with all
slop signals removed AND all human quirks removed (burstiness, favorite
punctuation, register mixture) is itself a tell — "zu sauber" ist ein
Tell (humanizer-de). Detect-only, advisory, never part of the numeric
slop score (ADR-0001 scope; identical contract to paste_artifacts.py).

Signals (issue #81 Lösung, Teilumfang — see DEFERRED below):
1. over_sanitized  — very low slop-signal density + extremely uniform
                     burstiness + zero idiosyncrasy markers (em-dash 0,
                     contractions 0, sentence-length variance minimal).
                     Low confidence, advisory only.
2. register_drift  — marker distance between document halves exceeds
                     threshold (register collapse, humanizer-de M69/30):
                     one half colloquial-marked, the other clinically
                     bare. Language-neutral marker proxy (EN calibrated).
3. modal_particle_anomaly (M63) — DEFERRED to #73 (DE-Signallayer): needs
   the German modal-particle inventory which does not exist yet.

Guardrail (Pflicht laut #81): technical documentation / API docs /
legal text are legitimately uniform. Genre profiles (#42) exempt those
genres: classify_text(text, genre=...) with genre in EXEMPT_GENRES
disables the signal entirely (documented keep_when, not detection logic).

SSOT: ontology.json `signals.naturalnessGuard` for catalog parity
(corpus-calibrated inline thresholds = documented conscious deviation,
same register class as paste_artifacts / deIdeology).
"""

import re
import statistics
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Genre exemption (#42 profiles, keep_when guard)
# ---------------------------------------------------------------------------
EXEMPT_GENRES = {
    "technical",     # technical documentation / handbooks
    "api-doc",       # reference / API docs
    "legal",         # contracts, statutes, terms
    "scientific",    # methods sections, abstracts
    "changelog",     # release notes
}

# Language-neutral idiosyncrasy / colloquiality markers (EN-calibrated).
# Used for both over_sanitized ("none anywhere") and register_drift
# ("uneven distribution across document halves").
_IDIOSYNCRASY_MARKERS = [
    re.compile(r"\b(?:don't|can't|won't|it's|that's|you're|we're|let's|"
               r"isn't|doesn't|didn't|there's|what's)\b", re.I),
    re.compile(r"(?:^|[.!?]\s+)(?:and|but|so|yet)\s+\w", re.I | re.M),
    re.compile(r"—|–"),
    re.compile(r"\b(?:actually|honestly|kinda|sorta|pretty much|"
               r"to be fair|frankly|basically|tbh)\b", re.I),
    re.compile(r"!\s"),
    re.compile(r"\b(?:we|our|us)\b", re.I),  # authorial voice
]

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class NaturalnessFinding:
    signal_id: str
    confidence: float
    evidence: str
    severity: str = "low"

    def __repr__(self):
        return (f"NaturalnessFinding({self.signal_id!r}, conf={self.confidence:.2f}, "
                f"evidence={self.evidence!r})")


@dataclass
class NaturalnessResult:
    signals_detected: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    @property
    def is_advisory(self) -> bool:
        return bool(self.signals_detected)

    def summary(self) -> str:
        if not self.signals_detected:
            return "naturalness: ok (no over-sanitization markers)"
        return ("naturalness: " + "; ".join(
            f"{f.signal_id} (conf={f.confidence:.2f})" for f in self.signals_detected))


def _sentences(text: str) -> list:
    sents = [s.strip() for s in _SENT_SPLIT.split(text.strip()) if s.strip()]
    return [s for s in sents if len(s.split()) >= 3]


def _marker_density(text: str) -> float:
    """Markers per 100 words."""
    words = len(text.split())
    if words == 0:
        return 0.0
    hits = sum(len(p.findall(text)) for p in _IDIOSYNCRASY_MARKERS)
    return 100.0 * hits / words


def _burstiness(sents: list) -> float:
    """Coefficient of variation of sentence word lengths (0 = perfectly uniform)."""
    lens = [len(s.split()) for s in sents]
    if len(lens) < 4 or statistics.mean(lens) == 0:
        return -1.0  # too short to judge
    return statistics.pstdev(lens) / statistics.mean(lens)


class NaturalnessGuard:
    """Detect-only over-sanitization guard (#81). Advisory, never scored."""

    # Thresholds (conservative — advisory must not fire on decent prose):
    MIN_WORDS = 120          # below this, uniformity is not meaningful
    MAX_MARKER_DENSITY = 0.6 # markers per 100 words: near-total absence
    MAX_BURSTINESS = 0.25    # extremely uniform sentence lengths
    DRIFT_RATIO = 4.0        # half A density >= 4x half B density
    DRIFT_MIN_DENSITY = 2.0  # and half A actually carries markers

    def classify_text(self, text: str, genre: str = "general"
                      ) -> NaturalnessResult:
        text = text or ""
        res = NaturalnessResult()
        if genre in EXEMPT_GENRES:
            res.notes.append(
                f"skipped: genre '{genre}' legitimately uniform "
                f"(keep_when, #42 profiles)")
            return res

        words = len(text.split())
        if words < self.MIN_WORDS:
            res.notes.append(f"skipped: <{self.MIN_WORDS} words")
            return res

        sents = _sentences(text)
        density = _marker_density(text)
        burst = _burstiness(sents)

        # 1) over_sanitized: everything bland — no slop *and* no humanity
        if density <= self.MAX_MARKER_DENSITY and 0.0 <= burst <= self.MAX_BURSTINESS:
            res.signals_detected.append(NaturalnessFinding(
                signal_id="over_sanitized",
                confidence=0.35,
                evidence=(f"marker_density={density:.2f}/100w "
                          f"(≤{self.MAX_MARKER_DENSITY}), "
                          f"burstiness={burst:.2f} (≤{self.MAX_BURSTINESS})"),
                severity="low"))
            res.notes.append("advisory: möglicherweise über-glättet — "
                             "nicht score-wirksam")

        # 2) register_drift: halves differ in marker density (M69/30 proxy)
        half = len(text) // 2
        # split at sentence boundary nearest the middle
        split_at = text.rfind(". ", 0, half + len(text) // 10)
        if split_at <= 0:
            split_at = half
        d_a = _marker_density(text[:split_at])
        d_b = _marker_density(text[split_at:])
        hi, lo = max(d_a, d_b), min(d_a, d_b)
        if (hi >= self.DRIFT_MIN_DENSITY
                and hi >= self.DRIFT_RATIO * max(lo, 0.05)):
            which = "first" if d_a >= d_b else "second"
            res.signals_detected.append(NaturalnessFinding(
                signal_id="register_drift",
                confidence=0.45,
                evidence=(f"half-density {d_a:.2f} vs {d_b:.2f}/100w "
                          f"({which} half colloquial-marked)"),
                severity="low"))

        return res

    classify = classify_text  # convenience alias


if __name__ == "__main__":  # pragma: no cover - smoke test
    flat = ("The system provides functionality. The system ensures reliability. "
            "The system delivers performance. The system supports scalability. "
            "The system enables efficiency. The system maintains stability. "
            "The system offers capability. The system implements process. "
            "The system provides functionality. The system ensures reliability. "
            "The system delivers performance. The system supports scalability. "
            "The system enables efficiency. The system maintains stability. ")
    r = NaturalnessGuard().classify_text(flat)
    print(r.summary(), r.notes)
