#!/usr/bin/env python3
"""
Anchor-Drift signal (issue #78, detect-only).

Protected anchors (cf. evidence-ledger concept, deep/11): numbers, direct
quotes, URLs, DOIs. `anchor_diff(text_a, text_b)` compares the anchor sets
of two text versions and reports

  - anchor_lost      anchor present in A, gone in B (content-losing rewrite)
  - anchor_added     anchor present only in B (invented detail)
  - authority_shift  a retained number whose nearby authority carrier
                     changed ("according to the study" -> "researchers say")

Language-agnostic by construction: anchors are regex-level; the closed
carrier list covers EN+DE marker words. DETECT-ONLY — findings never feed
the numeric slop score (ADR-0001 discipline: scorer stays untouched).

FP expectation (#64): human rewrites that deliberately drop a number while
keeping the claim read as anchor_lost — that is the intended advisory, not a
false positive; confidence is fixed at 0.6, output is advisory-only.

keep_when: texts shorter than 20 characters or without any anchor are never
diffed (trivially stable).

Public surface:
    extract_anchors(text) -> {"number": [...], "quote": [...], "url": [...], "doi": [...]}
    anchor_diff(text_a, text_b) -> {"anchor_lost": [...], "anchor_added": [...],
                                    "authority_shift": [...], "has_drift": bool}
"""

import re

# --- anchor extractors -------------------------------------------------------

_NUM_RE = re.compile(r"\d+(?:[.,]\d+)*%?")
_URL_RE = re.compile(r"https?://[^\s\"'<>»“]+")
_DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>,;]+")
_QUOTE_PAIRS = [
    ('„', '“'), ('"', '"'), ('“', '”'), ('«', '»'), ('‘', '’'), ("'", "'"),
]

# Closed carrier list (EN+DE authority marker words). Deliberately small;
# anything outside the list is not an authority carrier.
AUTHORITY_CARRIERS = {
    "according to", "reported by", "study", "studies", "researchers",
    "professor", "prof", "dr", "expert", "experts", "source", "sources",
    "report", "reports",
    "laut", "zufolge", "studie", "studien", "forscher", "forscherinnen",
    "bericht", "berichte", "experte", "expertin", "experten", "quelle",
    "quellen", "untersuchung", "untersuchungen",
}

_CONTEXT_RADIUS = 60  # chars around a number occurrence for carrier lookup


def _canon_number(raw: str) -> str:
    """Canonicalize locale variants: 3,5 == 3.5; 1,000/1.000 == 1000.

    A separator followed by exactly 3 digits (and not ending a number with
    another separator) is a thousands separator; otherwise decimal. The
    percent sign is formatting, not anchor identity ("12,4 %" == "12.4%").
    """
    body = raw.rstrip("%")
    parts = re.split(r"[.,]", body)
    if len(parts) == 1:
        return str(int(parts[0]))
    if all(len(p) == 3 for p in parts[1:]):
        value = int("".join(parts))  # thousands grouping
    else:
        value = float(".".join(parts))  # decimal (comma or point)
    return str(int(value)) if float(value).is_integer() else str(value)


def extract_anchors(text: str) -> dict:
    """Extract canonical anchor multisets by kind (order-preserving lists)."""
    quotes = []
    for opener, closer in _QUOTE_PAIRS:
        for m in re.finditer(
                re.escape(opener) + r"(.{1,300}?)" + re.escape(closer), text):
            content = m.group(1).strip()
            if content and content not in quotes:
                quotes.append(content)
    return {
        "number": [_canon_number(m.group(0)) for m in _NUM_RE.finditer(text)],
        "quote": quotes,
        "url": [m.group(0).rstrip(".,;:)") for m in _URL_RE.finditer(text)],
        "doi": [m.group(0).rstrip(".,;:)") for m in _DOI_RE.finditer(text)],
    }


def _carriers_near(text: str, value: str) -> set:
    """Authority carrier words within +/- _CONTEXT_RADIUS chars of any
    occurrence of the number token `value` (locale-tolerant match)."""
    variants = {value, value.replace(".", ",")}
    hits = []
    for v in variants:
        pat = re.escape(v).replace(r"\.", r"[.,]")
        hits.extend(m for m in re.finditer(r"(?<![\d.,])" + pat + r"(?![\d])", text))
    if not hits:
        hits = []
    words = set()
    for m in hits:
        lo = max(0, m.start() - _CONTEXT_RADIUS)
        hi = min(len(text), m.end() + _CONTEXT_RADIUS)
        window = re.findall(r"[A-Za-zÄÖÜäöüß]+", text[lo:hi].lower())
        words.update(window)
    return words & AUTHORITY_CARRIERS


def anchor_diff(text_a: str, text_b: str) -> dict:
    """Diff the protected-anchor sets of two text versions (detect-only)."""
    if len(text_a) < 20 and len(text_b) < 20:
        return {"anchor_lost": [], "anchor_added": [],
                "authority_shift": [], "has_drift": False}

    a, b = extract_anchors(text_a), extract_anchors(text_b)
    lost, added, shift = [], [], []

    for kind in ("number", "quote", "url", "doi"):
        from collections import Counter
        ca, cb = Counter(a[kind]), Counter(b[kind])
        for value, n in (ca - cb).items():
            lost.append({"kind": kind, "value": value,
                         "evidence": f"anchor in original, missing in rewrite"})
        for value, n in (cb - ca).items():
            added.append({"kind": kind, "value": value,
                          "evidence": f"anchor only in rewrite"})

    # authority_shift: number retained, nearby carrier set changed
    for value in sorted(set(a["number"]) & set(b["number"])):
        carriers_a = _carriers_near(text_a, value)
        carriers_b = _carriers_near(text_b, value)
        if carriers_a and (carriers_a != carriers_b):
            shift.append({
                "kind": "number", "value": value,
                "evidence": (f"authority carrier changed: "
                             f"{sorted(carriers_a)} -> {sorted(carriers_b)}"),
            })

    return {"anchor_lost": lost, "anchor_added": added,
            "authority_shift": shift,
            "has_drift": bool(lost or added or shift)}
