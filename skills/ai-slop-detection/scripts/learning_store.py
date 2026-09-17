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


def learn_entry(path, note, signal_id=None, sample_text=None, added_by="manual"):
    """Issue #120: simple learn input — a freetext note is enough.

    Input standard (docs/loop-guards/120-learn-input-standard.md):
    `slop learn "false positive on src/foo.rs"` — no UI, no schema
    enforcement. signal_id defaults to "reviewed" (refine later);
    sample_text defaults to the note itself so the entry stays
    attributable even without a file. Optional `--file` upgrades the
    entry to an exact-sample exemption.
    """
    note = (note or "").strip()
    if not note:
        raise ValueError("learn input requires a non-empty freetext note")
    return add_entry(
        path,
        signal_id=signal_id or "reviewed",
        sample_text=sample_text if sample_text is not None else note,
        note=note,
        added_by=added_by,
    )


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


def _cli():
    import argparse
    parser = argparse.ArgumentParser(
        description="Learn input (issue #120): freetext + optional path is enough.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("learn", help='append a learning entry, e.g. learn "false positive on src/foo.rs"')
    p.add_argument("note", help="freetext — anything the reviewer wants to say")
    p.add_argument("--signal", help="signal_id if known (default: 'reviewed')")
    p.add_argument("--file", help="optional existing file the note refers to")
    p.add_argument("--store", help="store path (default: not_slop.jsonl next to --file or cwd)")
    p.add_argument("--by", help="who is learning (default: 'manual')")
    args = parser.parse_args()

    sample_text = None
    if args.file:
        if not os.path.isfile(args.file):
            raise SystemExit(f"Error: no such file: {args.file}")
        with open(args.file, encoding="utf-8", errors="replace") as f:
            sample_text = f.read()
    store = args.store or (
        os.path.join(os.path.dirname(os.path.abspath(args.file)), "not_slop.jsonl")
        if args.file else os.path.join(os.getcwd(), "not_slop.jsonl"))
    entry = learn_entry(store, args.note, signal_id=args.signal,
                        sample_text=sample_text, added_by=args.by)
    src = args.file or "<note-as-sample>"
    print(f"Learned: {entry['signal_id']} ({src}, hash {entry['sample_hash']}, "
          f"store: {store})")


if __name__ == "__main__":
    _cli()
