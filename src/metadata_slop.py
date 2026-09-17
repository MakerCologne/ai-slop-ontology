"""METADATA / CONFIG / DATA SLOP — detect-only signal class (issue #45).

Covers the surfaces #9/#10/#31 (code-AST, docs) do NOT touch:

- CommitMessageSlop: generated commit messages / PR descriptions
  ("This PR refactors ... to improve readability and maintainability")
- JsonFieldSlop: empty generated JSON data fields
  ("description": "A comprehensive suite of tools ...")
- ConfigBoilerplateSlop: dockerfile/YAML/Terraform boilerplate comments

DETECT-ONLY: this module never rewrites anything (ADR-0001 detector-only
repo). All signals report findings with evidence; scoring is advisory and
never part of the numeric text/code slop score.

Detection is corpus-calibrated inline lists (documented conscious deviation
from the ontology.json SSOT projection, see scripts/check_ssot.py) — the
SSOT entry lives in ontology.json `signals.metadata` for catalog parity.
"""

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Signal catalogs (regex, compiled once)
# ---------------------------------------------------------------------------

# Commit messages / PR bodies produced by coding agents. High-precision
# patterns: verb-first summary + generic benefit clause. These are the
# classic "This PR refactors X to improve readability and maintainability"
# constructions (cf. gap-report blind-spot BS-I2).
COMMIT_MESSAGE_PATTERNS = [
    # "This PR/MR/commit/CL changes X to improve Y and Z"
    re.compile(
        r"(?i)this\s+(?:pr|mr|commit|cl|change|patch)\b[^.\n]{0,80}?"
        r"\b(?:to\s+)?improve(?:s)?\s+(?:code\s+)?(?:readability|maintainability"
        r"|clarity|robustness|performance|consistency)",
    ),
    # "improve code readability and maintainability" benefit tail
    re.compile(
        r"(?i)improv\w*\s+(?:the\s+)?(?:code\s+)?"
        r"(?:readability|maintainability|clarity)(?:\s+(?:and|&)\s+"
        r"(?:the\s+)?(?:readability|maintainability|clarity))+",
    ),
    # "This PR implements feature X" + filler "as per the requirements"
    re.compile(
        r"(?i)this\s+(?:pr|mr|commit)\s+(?:implements|adds|introduces)\b"
        r"[^.\n]{0,60}\bas\s+(?:per\s+)?(?:the\s+)?(?:requirements?|spec"
        r"|request|discussion)",
    ),
    # Co-Authored-By / Generated-with agent trailers are fine — but a
    # subject line that narrates the assistant ("I have implemented ...")
    # is generated-message slop.
    re.compile(
        r"(?im)^\s*(?:i\s+have\s+|i've\s+)?(?:implemented|updated|added|fixed)\b"
        r"[^.\n]{0,60}\b(?:for\s+you|as\s+requested|as\s+asked)\b",
    ),
]

# Empty generated JSON data fields: a *data* field (description, summary,
# title, notes, comment) whose value is a generic filler sentence instead
# of real content (BS-I3). Key insight: the field exists, but the value is
# template output ("A comprehensive suite of tools ...", "Various fixes").
JSON_FIELD_PATTERNS = [
    re.compile(
        r'(?i)"(?:description|summary|title|notes?|comment|details?)"\s*:\s*"'
        r'[^"]{0,120}?'
        r'(?:a\s+comprehensive|a\s+powerful|a\s+versatile|various|multiple|'
        r'several|numerous)\b[^"]{0,120}"',
    ),
    # "TODO: add description" style placeholder values in data fields
    re.compile(
        r'(?i)"(?:description|summary|title|notes?|comment|details?)"\s*:\s*"'
        r'[^"]{0,60}\btodo\b[^"]{0,60}"',
    ),
    # Value that just restates the key: "description": "The description of X"
    re.compile(
        r'(?i)"(description|summary|title|notes|comment|details)"\s*:\s*"'
        r'[Tt]he\s+\1\s+(?:of|for)\b',
    ),
]

# Boilerplate comments in config files: Dockerfile / YAML / Terraform.
# Only *narrating* comments count (comment that explains what the next line
# obviously does, in generic terms) — instructional LICENSE header etc. are
# not slop (BS-I4).
CONFIG_BOILERPLATE_PATTERNS = [
    # Dockerfile: "# Install dependencies" over a FROM/requirements line
    re.compile(
        r"(?im)^\s*#\s*(?:install(?:ing)?|setup|configure|copy|update)\s+"
        r"(?:the\s+)?(?:dependencies|requirements|files?|packages?)\s*$"
        r"(?=\s*\n\s*(?:RUN|COPY|ADD|apt-get|pip|npm|COPY)\b)",
    ),
    # YAML: "# Configuration for <service>" top comment
    re.compile(
        r"(?im)^\s*#\s*(?:configuration|settings?|config)\s+for\s+[\w.-]+\s*$",
    ),
    # Terraform: "# Create a <resource> resource" above a resource block
    re.compile(
        r"(?im)^\s*#\s*create\s+(?:a|an)\s+[\w-]+\s+(?:resource|bucket|group|"
        r"instance|role|policy)\s*$",
    ),
    # Generic "# This script does X" narration header
    re.compile(
        r"(?im)^\s*#\s*this\s+(?:script|file|config|section)\s+"
        r"(?:does|contains|defines|sets up)\b",
    ),
]


@dataclass
class MetadataFinding:
    signal_id: str
    surface: str  # commit_message | json_data | config
    confidence: float
    evidence: str
    severity: str = "medium"  # detect-only: advisory, never hard-gated

    def __str__(self):  # pragma: no cover - debug helper
        return f"[{self.signal_id}] {self.evidence[:80]!r} (conf {self.confidence})"


@dataclass
class MetadataSlopResult:
    signals_detected: list = field(default_factory=list)
    slop_types: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    @property
    def is_slop(self) -> bool:
        return bool(self.signals_detected)

    def summary(self) -> str:
        if not self.signals_detected:
            return "clean"
        ids = sorted({f.signal_id for f in self.signals_detected})
        return ", ".join(ids)


class MetadataSlopClassifier:
    """Detect-only slop detector for metadata/config/data surfaces.

    Usage:
        mdc = MetadataSlopClassifier()
        res = mdc.classify_commit_message("This PR refactors X to improve ...")
        res = mdc.classify_json_fields(json_text)
        res = mdc.classify_config(config_text)
    """

    SIGNAL_SEVERITY = {
        "CommitMessageSlop": "medium",
        "JsonFieldSlop": "medium",
        "ConfigBoilerplateSlop": "low",
    }

    # A single hit on these surfaces is weak evidence (patterns can be
    # legitimate); 2+ distinct patterns make the signal.
    MIN_HITS = 2

    def __init__(self):
        self._commit = COMMIT_MESSAGE_PATTERNS
        self._json = JSON_FIELD_PATTERNS
        self._config = CONFIG_BOILERPLATE_PATTERNS

    # -- internal ---------------------------------------------------------

    @staticmethod
    def _match_all(patterns, text):
        hits, evidence = set(), []
        for i, pat in enumerate(patterns):
            for m in pat.finditer(text):
                hits.add(i)
                evidence.append(m.group(0)[:120])
        return hits, evidence

    def _classify(self, signal_id: str, surface: str, patterns, text: str
                  ) -> MetadataSlopResult:
        hits, evidence = self._match_all(patterns, text)
        res = MetadataSlopResult()
        if len(hits) >= self.MIN_HITS:
            conf = min(0.95, 0.5 + 0.15 * len(hits))
            res.signals_detected.append(MetadataFinding(
                signal_id=signal_id, surface=surface, confidence=conf,
                evidence=" | ".join(evidence[:3]),
                severity=self.SIGNAL_SEVERITY[signal_id]))
            res.slop_types.append(signal_id)
        return res

    # -- public API ---------------------------------------------------------

    def classify_commit_message(self, text: str) -> MetadataSlopResult:
        """Classify a commit message / PR body (any VCS text)."""
        return self._classify(
            "CommitMessageSlop", "commit_message", self._commit, text or "")

    def classify_json_fields(self, json_text: str) -> MetadataSlopResult:
        """Classify data fields in a JSON document / string."""
        return self._classify(
            "JsonFieldSlop", "json_data", self._json, json_text or "")

    classify_json = classify_json_fields  # convenience alias

    def classify_config(self, config_text: str) -> MetadataSlopResult:
        """Classify comments in Dockerfile/YAML/Terraform-style config."""
        return self._classify(
            "ConfigBoilerplateSlop", "config", self._config, config_text or "")

    def classify_all(self, commit_message="", json_text="", config_text=""):
        """Run all three surfaces, merge into one result."""
        merged = MetadataSlopResult()
        for res in (
            self.classify_commit_message(commit_message),
            self.classify_json_fields(json_text),
            self.classify_config(config_text),
        ):
            merged.signals_detected.extend(res.signals_detected)
            merged.slop_types.extend(res.slop_types)
            merged.notes.extend(res.notes)
        return merged
