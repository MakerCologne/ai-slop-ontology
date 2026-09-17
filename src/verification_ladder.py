"""VERIFICATION LADDER — fake-done metric for the code axis (issue #121).

Implements the spec in docs/metric/VERIFICATION-LADDER.md: every function
in a module is placed on a ladder of evidential strength, derived
exclusively from the code itself::

    asserted > tested > reachable > claimed-only > stub > synthetic-risk

Rung definitions (evidence required, under-credits, never over-credits):

- ``asserted``      — an executable ``assert`` statement in the analyzed
                      sources exercises the function (strongest: runtime
                      verification bundled with the code).
- ``tested``        — the function is referenced from a ``test_*``
                      function in the provided test sources.
- ``reachable``     — a call path exists from module-level code / known
                      entry points to the function (direct or transitive
                      within the analyzed unit).
- ``claimed-only``  — behavior is claimed (docstring or name implies
                      behavior) but no asserts, tests or callers exist.
- ``stub``          — signature without implementation (``pass``, ``...``,
                      ``raise NotImplementedError``; docstring-only body).
- ``synthetic-risk``— the function returns random or hardcoded values
                      where its name/docstring claims a computation
                      (critical-tier candidate, reported as a gate).

Spec-ambiguity note: the spec lists ``asserted`` as the top rung with the
parenthetical "nur behauptet (Docstring/Kommentar)", which would collide
with ``claimed-only``. We resolve it as: ``asserted`` = verified by
executable ``assert`` statements; docstring-only claims land on
``claimed-only`` (matching the spec's own definition of that rung).

DETECT-ONLY (adr/0006): the ladder is a per-function report line, never a
numeric score and never part of the text/code slop score. ``synthetic-risk``
findings are surfaced as ``gates`` (advisory, critical-tier candidate
#55) — promotion to a scored signal requires its own SIGNAL-DoD issue with
3/3/2 fixtures, per the spec's integration section.

Public surface::

    analyze_module(source, test_sources=None, entry_points=None) -> {
        "ladder": [...],          # rung order, best first
        "functions": [ {name, level, evidence} ],
        "summary": {rung: count},
        "gates": [ {name, reason, evidence} ],   # synthetic-risk entries
    }
"""

import ast

LADDER = [
    "asserted",
    "tested",
    "reachable",
    "claimed-only",
    "stub",
    "synthetic-risk",
]

# Function-name stems that claim a computation. Returning random or
# hardcoded values from such a function is synthetic-risk evidence.
_COMPUTE_STEMS = (
    "compute", "calc", "convert", "parse", "generate", "score", "detect",
    "analyze", "evaluate", "sum", "total", "average", "measure", "extract",
    "transform", "validate", "process", "count", "estimate", "predict",
)

_COMPUTE_DOC_HINTS = (
    "calculat", "comput", "parse", "convert", "generate", "score",
    "detect", "analyz", "evaluat", "measur", "extract", "transform",
    "validat", "sum ", "average", "count",
)

_ENTRY_NAMES = ("main", "run", "cli", "handler", "serve", "start")


def _function_bodies(func: ast.FunctionDef):
    """Body statements with the docstring stripped."""
    body = list(func.body)
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        body = body[1:]
    return body


def _is_stub(func: ast.FunctionDef) -> bool:
    body = _function_bodies(func)
    # docstring-only body (empty after strip) = signature without impl
    if not body:
        return True
    for stmt in body:
        if isinstance(stmt, ast.Pass):
            continue
        if (isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is Ellipsis):
            continue
        if (isinstance(stmt, ast.Raise) and stmt.exc is not None
                and isinstance(stmt.exc, ast.Call)
                and getattr(stmt.exc.func, "id", "") == "NotImplementedError"):
            continue
        return False
    return True


def _returns(func: ast.FunctionDef):
    out = []
    for node in ast.walk(func):
        if isinstance(node, ast.Return) and node.value is not None:
            out.append(node.value)
    return out


def _is_random_expr(node) -> bool:
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        base = node.func.value
        if isinstance(base, ast.Name) and base.id == "random":
            return True
        if (isinstance(base, ast.Name) and base.id == "np"
                and node.func.attr in ("random", "randint", "rand")):
            return True
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        if node.value.id == "random" and node.func.attr != "seed":
            return True
    return False


def _is_constant_return(node) -> bool:
    # Numeric/str constant (not True/False/None); lists/dicts of constants
    if isinstance(node, ast.Constant):
        return node.value is not None and not isinstance(node.value, bool)
    if isinstance(node, (ast.List, ast.Dict, ast.Tuple, ast.Set)):
        try:
            for item in ast.walk(node):
                if isinstance(item, ast.Name):
                    return False
            return True
        except Exception:
            return False
    return False


def _claims_computation(func: ast.FunctionDef) -> bool:
    lname = func.name.lower()
    if any(stem in lname for stem in _COMPUTE_STEMS):
        return True
    doc = ast.get_docstring(func) or ""
    ldoc = doc.lower()
    return any(hint in ldoc for hint in _COMPUTE_DOC_HINTS)


def _uses_params(func: ast.FunctionDef) -> bool:
    params = {a.arg for a in func.args.args if a.arg not in ("self", "cls")}
    if not params:
        return True  # no params: nothing to leave unused
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and node.id in params:
            if isinstance(node.ctx, ast.Load):
                return True
    return False


def _is_synthetic_risk(func: ast.FunctionDef):
    """Returns evidence string or None."""
    if _is_stub(func) or not _claims_computation(func):
        return None
    rets = _returns(func)
    if not rets:
        return None
    for node in rets:
        if _is_random_expr(node):
            return (f"{func.name}() returns a random value "
                    f"(random.*) while its name/docstring claims a "
                    f"computation")
        if _is_constant_return(node) and not _uses_params(func):
            return (f"{func.name}() returns a hardcoded constant while "
                    f"its parameters are unused (claims a computation)")
    return None


def _called_names(node) -> set:
    out = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
            out.add(sub.func.id)
    return out


def _asserted_names(node) -> set:
    """Functions exercised by `assert ... f(...)` statements."""
    out = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Assert):
            for call in ast.walk(sub.test):
                if (isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Name)):
                    out.add(call.func.id)
                if (isinstance(call, ast.Compare)
                        and isinstance(call.left, ast.Call)
                        and isinstance(call.left.func, ast.Name)):
                    out.add(call.left.func.id)
    return out


def _reachable_from(entry_calls: dict, direct: dict) -> set:
    """Transitive closure of the call graph from the entry names."""
    seen = set()
    stack = list(entry_calls)
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(direct.get(cur, ()))
    return seen


def analyze_module(source: str, test_sources=None, entry_points=None) -> dict:
    """Place every function of `source` on the verification ladder.

    Under-credit rule: a rung is only credited with positive evidence;
    absence of evidence lands the function on the lowest rung its *negative*
    evidence justifies (stub / synthetic-risk), else claimed-only.
    """
    tree = ast.parse(source)
    test_sources = test_sources or []

    functions = {}
    direct_calls = {}      # func name -> set of called function names
    module_level_calls = set()
    module_asserted = set()
    # test-function name -> set of referenced function names
    tested_by = {}

    # --- collect functions and intra-module call graph -------------
    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.scope = None

        def _handle_func(self, node):
            functions[node.name] = node
            calls = _called_names(node)
            # exclude immediate self-recursion from "caller" evidence
            direct_calls[node.name] = calls - {node.name}
            prev = self.scope
            self.scope = node.name
            self.generic_visit(node)
            self.scope = prev

        visit_FunctionDef = _handle_func
        visit_AsyncFunctionDef = _handle_func

    Visitor().visit(tree)

    for stmt in tree.body:
        module_level_calls |= _called_names(stmt)
    module_asserted |= _asserted_names(tree)

    for ts in test_sources:
        ttree = ast.parse(ts)
        for node in ast.walk(ttree):
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name.startswith("test")):
                tested_by[node.name] = _called_names(node) | _asserted_names(node)

    tested = set()
    for names in tested_by.values():
        tested |= names

    # --- entry points ------------------------------------------------
    entry = set(module_level_calls) | set(entry_points or [])
    # conventional entry names count only if they exist
    entry |= {n for n in _ENTRY_NAMES if n in functions}
    reachable = _reachable_from({n for n in entry if n in functions},
                                direct_calls)

    results = []
    gates = []
    for name, func in functions.items():
        level = None
        evidence = ""
        synthetic = _is_synthetic_risk(func)
        if synthetic:
            level = "synthetic-risk"
            evidence = synthetic
            gates.append({"name": name, "reason": "synthetic-risk",
                          "evidence": synthetic})
        elif _is_stub(func):
            level = "stub"
            body = _function_bodies(func)
            kind = "pass/..." if body and isinstance(
                body[0], ast.Pass) else "NotImplementedError"
            evidence = f"{name}() has no implementation ({kind})"
        elif name in module_asserted:
            level = "asserted"
            evidence = f"an assert statement exercises {name}()"
        elif name in tested:
            level = "tested"
            evidence = f"a test function references {name}()"
        elif name in reachable:
            level = "reachable"
            evidence = f"a call path from module level reaches {name}()"
        elif ast.get_docstring(func):
            level = "claimed-only"
            evidence = (f"{name}() has a behavior-claiming docstring but "
                        f"no asserts, tests or callers")
        else:
            level = "claimed-only"
            evidence = (f"{name}() has no asserts, tests or callers "
                        f"(implicit claim by existence)")

        results.append({"name": name, "level": level, "evidence": evidence})

    summary = {rung: 0 for rung in LADDER}
    for r in results:
        summary[r["level"]] += 1

    return {
        "ladder": list(LADDER),
        "functions": sorted(results, key=lambda r: LADDER.index(r["level"])),
        "summary": summary,
        "gates": gates,
    }
