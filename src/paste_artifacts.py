"""PASTE ARTIFACTS — 6 deterministic micro-signals (issue #113).

Chat-paste artifacts and elision markers that survive when assistant
output is pasted into code or doc files. All patterns are corpus-backed
from the slop-detection landscape review (2026-09-02):

1. elision-comment         — '// ... rest of code unchanged' (silently
                             deleted code!)         [stopslop SLOP001]
2. chat-preamble           — 'Certainly! Here's ...' assistant preamble
                             pasted into the file    [stopslop SLOP002]
3. fence-in-code           — stray Markdown fences inside code files
4. meta-process-comment    — comments narrating the generation process
                             ('agent behavior', 'phase 2 of the plan')
                             [scanaislop/aislop meta-comment]
5. list-label-marker       — G1/NG2-style label markers at list items
                             [jv-k/deslopper]
6. placeholder-credential-shape — your-api-key-here / INSERT_TOKEN
                             placeholders left in shipped files [stopslop]

DETECT-ONLY (ADR-0001): this module never rewrites anything and its
findings are advisory, never part of the numeric text/code slop score.

Detection is corpus-calibrated inline lists (documented conscious
deviation from the ontology.json SSOT projection, see
scripts/check_ssot.py) — the SSOT entry lives in ontology.json
`signals.paste_artifacts` for catalog parity.
"""

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Signal catalogs (regex, compiled once)
# ---------------------------------------------------------------------------

# 1) Elision comments: the assistant "shortened" the output and the paste
# silently dropped real code. High precision, high severity — one hit is
# a finding, because the elided region is unverifiable by definition.
ELISION_COMMENT_PATTERNS = [
    re.compile(
        r"(?im)^\s*(?://|#|--|/\*|<!--)?\s*(?:\.\.\.|…|\[?dots?\]?|\.\.\.)\s*"
        r"(?:the\s+)?(?:rest|remainder|remaining\s+part|other\s+parts?)\s+"
        r"(?:of\s+)?(?:the\s+)?(?:code|file|content|implementation|logic|"
        r"config(?:uration)?|function|class|test\w*)\b[^.\n]{0,40}"
        r"(?:is\s+)?(?:unchanged|stays?\s+the\s+same|remains?\s+the\s+same|"
        r"as\s+before|not\s+shown|omitted|elided|the\s+same)?\s*"
        r"(?:-->|\*/)?[\s.]*$",
    ),
    # "[... existing code here ...]" bracketed elision
    re.compile(
        r"(?i)\[\s*\.\.\.?\s*(?:existing|remaining|previous|other)\s+"
        r"(?:code|content|lines?|implementation|logic)\b[^]]{0,30}\]",
    ),
]

# 2) Chat preamble: assistant conversational framing pasted on top of a
# code or doc file. Single hit is a finding (very high precision).
CHAT_PREAMBLE_PATTERNS = [
    re.compile(
        r"(?im)^\s*(?:certainly|of\s+course|sure|great\s+question|"
        r"absolutely|happy\s+to\s+help|i'?d\s+be\s+happy\s+to\s+help)\s*[!,.]?\s*$",
    ),
    re.compile(
        r"(?im)^\s*(?:certainly|of\s+course|sure|absolutely)[!,.]?\s*"
        r"here'?s\s+(?:the|your|an?|my)\b[^.\n]{0,80}",
    ),
    re.compile(
        r"(?im)^\s*here'?s\s+the\s+(?:corrected|updated|revised|complete|"
        r"full|final|entire|correct)\s+(?:code|version|file|script|"
        r"function|implementation)\b",
    ),
    re.compile(
        r"(?im)^\s*as\s+(?:an?\s+)?(?:ai|assistant|language\s+model)\b[^.\n]{0,60}",
    ),
]

# 3) Stray Markdown fences inside code: ``` fence markers that open or
# close a block although the surrounding text is code, not Markdown.
# Two hits = an open+close pair; single fence is ambiguous (keep MIN_HITS=2).
FENCE_IN_CODE_PATTERNS = [
    re.compile(r"(?im)^\s*```[a-zA-Z0-9_+-]*\s*$"),
    re.compile(r"(?im)^\s*```\s*$"),
]

# 4) Meta-process comments: comments about the *generation process*, not
# about the code. Two distinct hits make the signal (a lone "phase 2"
# can be a legitimate project phase reference — keep_when).
META_PROCESS_COMMENT_PATTERNS = [
    re.compile(
        r"(?im)^\s*(?://|#|--)\s*(?:phase|step|stage)\s+\d+\s*(?:of|:)\s*"
        r"[^.\n]{0,60}$",
    ),
    re.compile(
        r"(?i)\b(?:the\s+)?(?:agent|assistant|model|llm|ai)\s+"
        r"(?:behavior|will\s+(?:now|then)|output|response)\b",
    ),
    re.compile(
        r"(?i)\b(?:as\s+)?(?:per|per)\s+(?:my\s+|the\s+)?(?:previous|last)\s+"
        r"(?:response|message|answer|turn|instruction\w*)\b",
    ),
    re.compile(
        r"(?i)\b(?:regenerat\w+|re-roll\w*|re-?prompt\w*)\s+"
        r"(?:the\s+)?(?:output|response|answer|code)\b",
    ),
]

# 5) List-label markers: synthetic taxonomy labels (G1/NG2/FN3/BS-I7 …)
# glued onto bullet items — classification residue from agent workflows.
# Two hits make the signal; a single marker can be a genuine reference.
LIST_LABEL_MARKER_PATTERNS = [
    re.compile(
        r"(?im)^\s*(?:[-*+]|\d+[.)])\s+"
        r"(?:G\d+|NG\d+|FN\d+|BS-I\d+|T\d+|M\d+|S\d+|A\d+|P\d+)\s*[:.)]\s+",
    ),
]

# 6) Placeholder credential shapes: template placeholders where a real
# secret/belongs. Single hit is a finding (never legitimate in shipped
# code — either unfinished template output or fake config).
PLACEHOLDER_CREDENTIAL_PATTERNS = [
    re.compile(
        r"(?i)\b(?:your|my|the|insert|replace|enter|add)_?"
        r"(?:api[_-]?key|token|secret|password|credential[_-]?s?|key)"
        r"(?:[_-]?(?:here|now))?\b",
    ),
    re.compile(
        r"(?i)\b(?:insert|replace|enter|paste|fill[_-]?in)\s+"
        r"(?:your\s+|the\s+|the\s+actual\s+)?"
        r"(?:api[_-]?key|token|secret|password|credential[_-]?s?)\b",
    ),
    re.compile(
        r"(?i)[\"']?(?:sk|pk|rk)[-_][a-z0-9]*x{3,}[a-z0-9]*[\"']?",
    ),
]


@dataclass
class PasteArtifactFinding:
    signal_id: str
    surface: str  # code | markdown | any
    confidence: float
    evidence: str
    severity: str = "medium"  # detect-only: advisory, never hard-gated

    def __str__(self):  # pragma: no cover - debug helper
        return f"[{self.signal_id}] {self.evidence[:80]!r} (conf {self.confidence})"


@dataclass
class PasteArtifactResult:
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


class PasteArtifactClassifier:
    """Detect-only slop detector for chat-paste artifacts and elision
    markers in code/doc files (issue #113).

    Usage:
        pac = PasteArtifactClassifier()
        res = pac.classify_text(code_or_doc_text)
    """

    SIGNAL_SEVERITY = {
        "elision-comment": "high",
        "chat-preamble": "high",
        "fence-in-code": "medium",
        "meta-process-comment": "medium",
        "list-label-marker": "low",
        "placeholder-credential-shape": "medium",
    }

    # Per-signal hit thresholds (issue #113 "Nachbesserungsqualität"):
    # single-hit signals are near-certain; pattern-y signals need 2+.
    SINGLE_HIT_SIGNALS = {
        "elision-comment",
        "chat-preamble",
        "placeholder-credential-shape",
    }

    # keep_when guards (documented escape hatches, not detection logic):
    #   elision-comment   — legitimate in quoted/tutorial excerpts when the
    #                       elided region is explicitly labeled "not shown"
    #   chat-preamble     — a transcript/chat-log file that *documents* an
    #                       assistant conversation (documented intent)
    #   fence-in-code     — Markdown files where fences are the format
    #   meta-process-comment — a real project phase plan ("Phase 2: v1.1")
    #   list-label-marker — a spec that genuinely uses a label taxonomy
    #   placeholder-credential-shape — template/example files whose *purpose*
    #                       is to be filled in (e.g. .env.example)

    def __init__(self):
        self._signals = {
            "elision-comment": ELISION_COMMENT_PATTERNS,
            "chat-preamble": CHAT_PREAMBLE_PATTERNS,
            "fence-in-code": FENCE_IN_CODE_PATTERNS,
            "meta-process-comment": META_PROCESS_COMMENT_PATTERNS,
            "list-label-marker": LIST_LABEL_MARKER_PATTERNS,
            "placeholder-credential-shape": PLACEHOLDER_CREDENTIAL_PATTERNS,
        }

    # -- internal -----------------------------------------------------------

    @staticmethod
    def _match_all(patterns, text):
        # Count *matches* (not distinct patterns): 2 labeled list items hit
        # the same pattern twice, and that must count as two hits.
        count, evidence = 0, []
        for pat in patterns:
            for m in pat.finditer(text):
                count += 1
                evidence.append(m.group(0)[:120])
        return count, evidence

    def _classify(self, signal_id: str, surface: str, patterns, text: str
                  ) -> PasteArtifactResult:
        hits, evidence = self._match_all(patterns, text)
        res = PasteArtifactResult()
        min_hits = 1 if signal_id in self.SINGLE_HIT_SIGNALS else 2
        if hits >= min_hits:
            conf = min(0.95, 0.5 + 0.15 * hits) if min_hits > 1 else 0.85
            res.signals_detected.append(PasteArtifactFinding(
                signal_id=signal_id, surface=surface, confidence=conf,
                evidence=" | ".join(evidence[:3]),
                severity=self.SIGNAL_SEVERITY[signal_id]))
            res.slop_types.append(signal_id)
        return res

    # -- public API -----------------------------------------------------------

    def classify_text(self, text: str, is_markdown: bool = False
                      ) -> PasteArtifactResult:
        """Classify code or doc text for paste artifacts and elision.

        `is_markdown=True` disables the fence-in-code signal (fences are
        the native format in Markdown files).
        """
        text = text or ""
        res = PasteArtifactResult()
        for signal_id, patterns in self._signals.items():
            if signal_id == "fence-in-code" and is_markdown:
                continue
            sub = self._classify(signal_id, "any", patterns, text)
            res.signals_detected.extend(sub.signals_detected)
            res.slop_types.extend(sub.slop_types)
        if is_markdown:
            res.notes.append("fence-in-code skipped: markdown surface")
        return res

    classify = classify_text  # convenience alias


if __name__ == "__main__":  # pragma: no cover - smoke test
    demo = """Certainly! Here's the updated code:

```python
# ... rest of the code unchanged ...
# Phase 2 of the plan: agent behavior verified
def f(): pass
# Phase 3: model output checked
```
"""
    r = PasteArtifactClassifier().classify_text(demo)
    print(r.summary())
    for f in r.signals_detected:
        print(f)
