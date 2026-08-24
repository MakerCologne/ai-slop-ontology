#!/usr/bin/env python3
"""
False-positive learning store (issue #29).

A JSONL file (`not_slop.jsonl`) of reviewed false positives. Each entry:

    {"signal_id": "buzzwords", "sample_hash": "<sha256[:16] of sample>",
     "note": "why this is fine", "date": "YYYY-MM-DD", "added_by": "name"}

The scorer consults the store via `exemptions_for()`: a signal family whose
id AND the sample's hash both appear in the store is excluded from the
evaluation of that exact sample and reported as `exempted`. Persistence is
a plain file — append-only JSONL, no server, no API.

Public surface:
    sample_hash(text) -> str
    add_entry(path, signal_id, sample_text, note, added_by) -> None
    load_store(path) -> list[dict]
    exemptions_for(entries, sample_hash_value) -> set[str]
"""

import hashlib
import json
import os
from datetime import date


def sample_hash(text: str) -> str:
    """Stable per-sample hash (sha256 of the UTF-8 text, first 16 hex chars)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def add_entry(path: str, signal_id: str, sample_text: str,
              note: str = "", added_by: str = "manual") -> dict:
    """Append one reviewed-false-positive entry to the store file."""
    entry = {
        "signal_id": signal_id,
        "sample_hash": sample_hash(sample_text),
        "note": note,
        "date": date.today().isoformat(),
        "added_by": added_by,
    }
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def load_store(path: str) -> list:
    """Load all entries; missing file = empty store (first use is normal)."""
    if not os.path.isfile(path):
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def exemptions_for(entries: list, sample_hash_value: str) -> set:
    """Signal-family ids exempted for this exact sample hash."""
    return {
        e["signal_id"] for e in entries
        if e.get("sample_hash") == sample_hash_value
    }
