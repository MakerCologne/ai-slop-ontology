"""METADATA / CONFIG / DATA SLOP — detect-only signal class (issue #45).

Covers the surfaces #9/#10/#31 (code-AST, docs) do NOT touch:

- CommitMessageSlop: generated commit messages / PR descriptions
  ("This PR refactors ... to improve readability and maintainability")
- JsonFieldSlop: empty generated JSON data fields
  ("description": "A comprehensive suite of tools ...")
- ConfigBoilerplateSlop: dockerfile/YAML/Terraform boilerplate comments
- #111 extension (blind-spot A7/BS-I6): CommitVelocitySlop (Cadence
  behavioral: additions/min, burst clusters, add/delete ratios),
  PRStructureSlop (anti-slop rules: emoji title, dangling code refs),
  CommitKeywordSlop (gitorit vocabulary/structure).

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
        "CommitVelocitySlop": "medium",
        "PRStructureSlop": "medium",
        "CommitKeywordSlop": "low",
    }

    # A single hit on these surfaces is weak evidence (patterns can be
    # legitimate); 2+ distinct patterns make the signal.
    MIN_HITS = 2

    def __init__(self):
        self._commit = COMMIT_MESSAGE_PATTERNS
        self._json = JSON_FIELD_PATTERNS
        self._config = CONFIG_BOILERPLATE_PATTERNS
        # #111 analyzers (behavioral / PR-structure / commit keywords)
        self.velocity = BehavioralAnalyzer()
        self.pr_structure = PRStructureAnalyzer()
        self.commit_keywords = CommitKeywordAnalyzer()

    # convenience pass-throughs for the #111 signal groups
    def classify_commit_history(self, commits):
        return self.velocity.analyze(commits)

    def classify_pull_request(self, pr):
        return self.pr_structure.analyze(pr)

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

# ---------------------------------------------------------------------------
# Issue #111: metadata-slop extension — behavioral, PR-structure and
# commit-keyword signals (blind-spot A7 / BS-I6). Rule sources, empirically
# calibrated by the landscape review (research/slop-detection-landscape-2026-09-02):
#   - peakoss/anti-slop (34 rules from 130+ manually reviewed slop PRs)
#   - TryCadence/Cadence (quantitative commit-velocity behavior)
#   - drhiidden/gitorit (commit-message keywords / structure)
# Same contract as #45: detect-only, advisory, never scored, MIN_HITS-style
# FP guards (multiple independent checks must fire).
# ---------------------------------------------------------------------------

import datetime as _dt

# gitorit-style generated commit-message vocabulary and structure.
COMMIT_KEYWORD_PATTERNS = [
    # agent gerund/marketing vocabulary in the *subject or body*
    re.compile(
        r"(?i)\b(?:enhancing|seamlessly|comprehensive|holistic|robustly"
        r"|leveraging|streamlining|empowering)\b"),
    # bullet-list body of pure additive gerunds ("- Adding ...\n- Fixing ...")
    re.compile(r"(?im)^\s*[-*]\s+\w+ing\b[^.\n]{0,60}$"),
]

# anti-slop style blocked terms for PR titles (marketing register).
PR_TITLE_BLOCKED = re.compile(
    r"(?i)\b(?:comprehensive|seamless|seamlessly|amazing|revolutionary"
    r"|cutting-edge|state-of-the-art|game-?changer|robust)\b")
PR_EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F900-\U0001F9FF]")


@dataclass
class CommitRecord:
    """Minimal commit metadata for behavioral analysis (Cadence-style)."""
    timestamp: _dt.datetime
    additions: int = 0
    deletions: int = 0
    message: str = ""


class BehavioralAnalyzer:
    """Detect-only velocity/behavior signals over a commit history.

    Rules (per Cadence, FP-guarded — at least MIN_RULES must fire):
      - additions/min > 100 sustained (needs >=2 commits within a window)
      - >=3 consecutive inter-commit gaps < 60s (burst cluster)
      - add/delete ratio > 90% across the history with volume > 200 lines
      - unnaturally consistent per-commit ratios (near-zero variance while
        volume is non-trivial)
    """

    SIGNAL_ID = "CommitVelocitySlop"
    SURFACE = "commit_history"

    MIN_RULES = 2
    VELOCITY_ADD_PER_MIN = 100.0
    MIN_GAP_SECONDS = 60
    BURST_MIN_CONSECUTIVE = 3
    ADD_DELETE_RATIO = 0.9
    MIN_TOTAL_LINES = 200

    def analyze(self, commits: list) -> MetadataSlopResult:
        res = MetadataSlopResult()
        commits = sorted(
            [c for c in commits if c and c.timestamp], key=lambda c: c.timestamp)
        if len(commits) < 2:
            return res
        fired, evidence = [], []

        # rule 1: sustained additions/min over whole span
        span_min = max(
            (commits[-1].timestamp - commits[0].timestamp).total_seconds(),
            1.0) / 60.0
        total_add = sum(c.additions for c in commits)
        rate = total_add / span_min
        if rate > self.VELOCITY_ADD_PER_MIN:
            fired.append("additions_per_min")
            evidence.append(f"{rate:.0f} additions/min over {span_min:.1f} min")

        # rule 2: burst cluster of short gaps
        gaps = [(commits[i + 1].timestamp - commits[i].timestamp).total_seconds()
                for i in range(len(commits) - 1)]
        run = best = 0
        for g in gaps:
            run = run + 1 if g < self.MIN_GAP_SECONDS else 0
            best = max(best, run)
        if best >= self.BURST_MIN_CONSECUTIVE:
            fired.append("burst_cluster")
            evidence.append(
                f"{best + 1} commits with <{self.MIN_GAP_SECONDS}s gaps")

        # rule 3: add-heavy ratio with volume
        total_del = sum(c.deletions for c in commits)
        total = total_add + total_del
        if total > self.MIN_TOTAL_LINES and total_del >= 0 \
                and total_add / total > self.ADD_DELETE_RATIO:
            fired.append("add_delete_ratio")
            evidence.append(
                f"add/delete ratio {total_add}/{total} "
                f"({total_add / total:.0%} additions)")

        # rule 4: unnaturally consistent per-commit ratios
        ratios = [c.additions / (c.additions + c.deletions)
                  for c in commits
                  if (c.additions + c.deletions) >= 10]
        if len(ratios) >= 4:
            spread = max(ratios) - min(ratios)
            if spread < 0.02:
                fired.append("suspiciously_consistent_ratios")
                evidence.append(f"ratio spread {spread:.3f} over {len(ratios)} commits")

        if len(fired) >= self.MIN_RULES:
            res.signals_detected.append(MetadataFinding(
                signal_id=self.SIGNAL_ID, surface=self.SURFACE,
                confidence=min(0.95, 0.5 + 0.15 * len(fired)),
                evidence=" | ".join(evidence),
                severity="medium"))
            res.slop_types.append(self.SIGNAL_ID)
        return res


class PRStructureAnalyzer:
    """Detect-only PR-structure signals (anti-slop style rule set).

    Input is a minimal dict: {"title", "body", "changed_files": [...]}.
    Rules (FP-guarded, >= MIN_RULES must fire):
      - >=2 emoji in title
      - blocked marketing term in title
      - code references (backticked tokens or path-like strings) that
        match none of the changed files (reference without diff relation)
      - message length > 200 chars AND keyword structure (gitorit)
    """

    SIGNAL_ID = "PRStructureSlop"
    SURFACE = "pull_request"

    MIN_RULES = 2
    TITLE_EMOJI_MAX = 2
    MSG_LEN = 200

    def analyze(self, pr: dict) -> MetadataSlopResult:
        res = MetadataSlopResult()
        title = pr.get("title") or ""
        body = pr.get("body") or ""
        changed = [str(f) for f in (pr.get("changed_files") or [])]
        fired, evidence = [], []

        n_emoji = len(PR_EMOJI.findall(title))
        if n_emoji >= self.TITLE_EMOJI_MAX:
            fired.append("title_emoji_count")
            evidence.append(f"{n_emoji} emoji in title")

        m = PR_TITLE_BLOCKED.search(title)
        if m:
            fired.append("title_blocked_term")
            evidence.append(f"title term {m.group(0)!r}")

        # code references without diff relation: backticked tokens or
        # path-like strings in title/body that appear in no changed file
        refs = set(re.findall(r"`([^`\n]{2,80})`", title + "\n" + body))
        refs |= set(re.findall(
            r"(?<![\w./])[\w-]+/[\w.-]+/[\w.-]+(?:\.[a-z]{1,4})?",
            title + "\n" + body))
        dangling = [r for r in refs
                    if not any(r in f or f.endswith(r) for f in changed)]
        if refs and dangling and len(dangling) >= 1:
            fired.append("dangling_code_reference")
            evidence.append(
                "refs not in diff: " + ", ".join(dangling[:3]))

        text = title + "\n\n" + body
        if len(text) > self.MSG_LEN and any(
                p.search(text) for p in COMMIT_KEYWORD_PATTERNS):
            fired.append("long_keyword_message")
            evidence.append(f"{len(text)} chars + agent keywords")

        if len(fired) >= self.MIN_RULES:
            res.signals_detected.append(MetadataFinding(
                signal_id=self.SIGNAL_ID, surface=self.SURFACE,
                confidence=min(0.95, 0.5 + 0.15 * len(fired)),
                evidence=" | ".join(evidence),
                severity="medium"))
            res.slop_types.append(self.SIGNAL_ID)
        return res


class CommitKeywordAnalyzer:
    """gitorit-style commit-message keyword/structure check.

    FP guard: keyword hit AND (length > 200 chars OR bullet-gerund
    structure) — a single marketing word in a short honest message is not
    slop.
    """

    SIGNAL_ID = "CommitKeywordSlop"
    SURFACE = "commit_message"
    MSG_LEN = 200

    def analyze(self, message: str) -> MetadataSlopResult:
        res = MetadataSlopResult()
        message = message or ""
        kw_hits = [p.pattern for p in COMMIT_KEYWORD_PATTERNS
                   if p.search(message)]
        structural = len(message) > self.MSG_LEN or (
            COMMIT_KEYWORD_PATTERNS[1].search(message) is not None)
        if kw_hits and structural:
            res.signals_detected.append(MetadataFinding(
                signal_id=self.SIGNAL_ID, surface=self.SURFACE,
                confidence=0.7,
                evidence=message[:120],
                severity="low"))
            res.slop_types.append(self.SIGNAL_ID)
        return res
