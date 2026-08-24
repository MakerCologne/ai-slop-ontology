#!/usr/bin/env python3
"""False-positive learning store (issue #29) — STUB for Red phase.

Entry format: {"signal_id", "sample_hash", "note", "date", "added_by"}
(one JSON object per line, JSONL persistence).
"""

from datetime import date as _date


def sample_hash(text: str) -> str:
    return "stub-" + _date.today().isoformat()


def add_entry(path, signal_id, sample_text, note="", added_by="manual") -> None:
    raise NotImplementedError


def load_store(path) -> list:
    return []


def exemptions_for(entries, sample_hash_value) -> set:
    return set()
