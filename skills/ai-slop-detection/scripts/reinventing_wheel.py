#!/usr/bin/env python3
"""
Reinventing-wheel detection (issue #32) — detect-only, code context.

Flags new functions in a module whose name+signature is near-duplicate of an
existing function in the SAME module (Ratcliff/Obershelp similarity > 0.8,
via difflib.SequenceMatcher) while the existing function's name is not
referenced in the new function's docstring (no "delegates to X", no
compat-shim note). Near-duplicates with a stated relationship are deliberate
API shims, not slop.

Public surface:
    detect_reinventing_wheel(py_source) -> list[{category, new_function,
        existing_function, similarity, referenced_existing, keep_when}]
"""

import ast
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.8


def _signature(fn: ast.FunctionDef) -> str:
    args = [a.arg for a in fn.args.args]
    defaults = len(fn.args.defaults)
    sig = ",".join(args)
    if defaults:
        sig += f";opt={defaults}"
    return f"{fn.name}({sig})"


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def detect_reinventing_wheel(py_source: str) -> list:
    try:
        tree = ast.parse(py_source)
    except SyntaxError:
        return []

    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    hits = []
    for i, fn in enumerate(functions):
        docstring = ast.get_docstring(fn) or ""
        for other in functions[:i]:
            sig_new, sig_old = _signature(fn), _signature(other)
            sim = _similarity(sig_new, sig_old)
            if sim <= SIMILARITY_THRESHOLD:
                continue
            referenced = other.name in docstring
            if referenced:
                continue  # explicit relationship: deliberate shim
            hits.append({
                "category": "reinventing-wheel",
                "new_function": fn.name,
                "existing_function": other.name,
                "similarity": round(sim, 3),
                "referenced_existing": False,
                "keep_when": "Genuinely different behavior that happens to "
                             "share a name shape — the docstring should then "
                             "say so (referencing the existing function).",
            })
    return hits
