"""slop — command-line toolkit for the AI Slop Ontology.

Subcommands:
    score      numeric slop score + severity for a text
    classify   full classification: slop types, signals, dimensions, actions
    rhetoric   detect-only rhetorical AI writing patterns (named evidence)
    check      combined report: score + types + rhetorical patterns
    code       classify source code for slop patterns
    info       signal-database and ontology metadata
    benchmark  run the labelled-corpus benchmark
    selfcheck  run the JSON/TTL/YAML/skill consistency check

Text input for score/classify/rhetoric/check/code:
    slop score "some text"        positional
    echo text | slop score -      stdin (dash)
    slop score --file draft.md    from a file
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from ._engine import get_engine, is_installed_layout, repo_root


# --------------------------------------------------------------------------- #
# input helpers
# --------------------------------------------------------------------------- #

def _read_input(args) -> str:
    if getattr(args, "file", None):
        return Path(args.file).read_text(encoding="utf-8")
    text = getattr(args, "text", None)
    if text is None or text == "-":
        return sys.stdin.read()
    return text


def _analysis_input(args, eng):
    """(text to analyze, raw score or None).

    With --strip-markup the document's quoted material is removed first and the
    untouched text is scored too, so both numbers can be reported (#69).
    """
    raw = _read_input(args)
    if not getattr(args, "strip_markup", False):
        return raw, None
    from ._engine import strip_markup
    return strip_markup(raw), eng.classify_text(raw).overall_slop_score


def _print_strip_header(raw_score: float, stripped_score: float) -> None:
    print(f"markdown pre-pass (#69): raw {raw_score:.2f} → stripped "
          f"{stripped_score:.2f} — the stripped score judges the prose")


def _bar(score: float, width: int = 20) -> str:
    filled = int(round(score * width))
    return "█" * filled + "·" * (width - filled)


_SEVERITY_ICON = {
    "clean": "🟢", "ai_assisted": "🟡", "suspicious": "🟠",
    "slop_candidate": "🔴", "critical": "⚫",
}


# --------------------------------------------------------------------------- #
# result serialization
# --------------------------------------------------------------------------- #

def _result_to_dict(r) -> dict:
    return {
        "modality": r.modality,
        "slop_score": r.overall_slop_score,
        "severity": r.severity,
        "slop_types": list(r.slop_types),
        "signals": [
            {"signal": s.signal_id, "confidence": s.confidence,
             "severity": s.severity, "evidence": s.evidence}
            for s in r.signals_detected
        ],
        "dimensions": {
            k: {"value": d.value, "is_slop": d.is_slop, "threshold": d.threshold}
            for k, d in r.dimensions.items()
        },
        "countermeasures": list(r.countermeasures),
    }


# --------------------------------------------------------------------------- #
# subcommand implementations
# --------------------------------------------------------------------------- #

def _gate(args, score: float) -> int:
    """Exit code for CI gating: 1 when --fail-over is set and score >= it."""
    threshold = getattr(args, "fail_over", None)
    if threshold is not None and score >= threshold:
        return 1
    return 0


def cmd_score(args, eng) -> int:
    text, raw_score = _analysis_input(args, eng)
    r = eng.classify_text(text)
    if args.json:
        payload = {"slop_score": r.overall_slop_score, "severity": r.severity}
        if raw_score is not None:
            payload["raw_slop_score"] = raw_score
            payload["stripped"] = True
        print(json.dumps(payload, indent=2))
        return _gate(args, r.overall_slop_score)
    if raw_score is not None:
        _print_strip_header(raw_score, r.overall_slop_score)
    icon = _SEVERITY_ICON.get(r.severity, "•")
    print(f"{icon} slop score {r.overall_slop_score:.2f}  [{_bar(r.overall_slop_score)}]  {r.severity}")
    if r.signals_detected:
        top = sorted(r.signals_detected, key=lambda s: -s.confidence)[:3]
        print("  top signals: " + ", ".join(f"{s.signal_id}" for s in top))
    return _gate(args, r.overall_slop_score)


def cmd_classify(args, eng) -> int:
    text, raw_score = _analysis_input(args, eng)
    r = eng.classify_text(text)
    if args.json:
        payload = _result_to_dict(r)
        if raw_score is not None:
            payload["raw_slop_score"] = raw_score
            payload["stripped"] = True
        print(json.dumps(payload, indent=2))
        return 0
    if raw_score is not None:
        _print_strip_header(raw_score, r.overall_slop_score)
    _print_classification(r)
    return 0


def cmd_code(args, eng) -> int:
    code = _read_input(args)
    r = eng.classify_code(code, args.lang or "")
    if args.json:
        print(json.dumps(_result_to_dict(r), indent=2))
        return 0
    _print_classification(r)
    return 0


def _print_classification(r) -> None:
    icon = _SEVERITY_ICON.get(r.severity, "•")
    print(f"{icon} slop score {r.overall_slop_score:.2f}  [{_bar(r.overall_slop_score)}]  {r.severity}")
    if r.slop_types:
        print("\nslop types:")
        for t in r.slop_types:
            print(f"  • {t}")
    if r.signals_detected:
        print(f"\nsignals ({len(r.signals_detected)}):")
        for s in sorted(r.signals_detected, key=lambda s: -s.confidence):
            print(f"  ⚠ {s.signal_id} [{s.severity} {s.confidence:.0%}] — {s.evidence}")
    if r.dimensions:
        dims = ", ".join(f"{k}={d.value}{'!' if d.is_slop else ''}" for k, d in r.dimensions.items())
        print(f"\ndimensions: {dims}")
    if r.countermeasures:
        print("\nrecommended: " + ", ".join(r.countermeasures))


def cmd_rhetoric(args, eng) -> int:
    # rhetoric reports no score, so the raw classification _analysis_input
    # would compute is pure waste — strip without scoring.
    text = _read_input(args)
    if getattr(args, "strip_markup", False):
        from ._engine import strip_markup
        text = strip_markup(text)
    findings = eng.rhetorical(text)
    if args.json:
        print(json.dumps({"rhetorical_patterns": findings}, indent=2))
        return 0
    if not findings:
        print("No rhetorical slop patterns detected.")
        return 0
    print(f"✍️  rhetorical patterns ({len(findings)}):")
    for f in findings:
        print(f"  • {f['label']} ({f['confidence']:.0%}) — \"{f['evidence']}\"")
        print(f"      fix: {f['fix']}")
    return 0


def cmd_check(args, eng) -> int:
    text, raw_score = _analysis_input(args, eng)
    r = eng.classify_text(text)
    findings = eng.rhetorical(text)
    if args.json:
        out = _result_to_dict(r)
        out["rhetorical_patterns"] = findings
        if raw_score is not None:
            out["raw_slop_score"] = raw_score
            out["stripped"] = True
        print(json.dumps(out, indent=2))
        return _gate(args, r.overall_slop_score)
    if raw_score is not None:
        _print_strip_header(raw_score, r.overall_slop_score)
    _print_classification(r)
    print()
    if findings:
        print(f"✍️  rhetorical patterns ({len(findings)}):")
        for f in findings:
            print(f"  • {f['label']} ({f['confidence']:.0%}) — \"{f['evidence']}\"")
    else:
        print("✍️  no rhetorical slop patterns detected")
    return _gate(args, r.overall_slop_score)


def cmd_info(args, eng) -> int:
    stats = eng.signal_stats()
    meta = eng.ontology_meta()
    cat = eng.rhetorical_catalogue()
    if args.json:
        print(json.dumps({"ontology": meta, "signals": stats,
                          "rhetorical_patterns": sorted(cat)}, indent=2))
        return 0
    print(f"AI Slop Ontology — {meta['name']} v{meta['version']} ({meta['date']}, {meta['license']})")
    print(f"ontology file: {eng.ontology_file}")
    print(f"\nsignal database: {stats['total_signals']} signals")
    print(f"  buzzwords:   {stats['buzzwords']} across {len(stats['buzzword_tiers'])} tiers")
    print(f"  phrases:     {stats['total_phrases']} across {len(stats['phrase_categories'])} categories")
    print(f"  structural:  {stats['structural_indicators']}")
    print(f"  punctuation: {stats['punctuation_indicators']}")
    print(f"  languages:   {', '.join(stats['languages'])}")
    print(f"  rhetorical:  {len(cat)} detect-only patterns ({', '.join(sorted(cat))})")
    return 0


def _run_script(rel_path: str, extra=None) -> int:
    script = repo_root() / rel_path
    if not script.exists():
        if is_installed_layout():
            print(
                f"error: this command runs {rel_path} from the repository and "
                f"is not available in an installed slopkit — clone the repo, or "
                f"point SLOP_REPO_ROOT at a checkout.",
                file=sys.stderr,
            )
        else:
            print(f"error: {rel_path} not found in repo", file=sys.stderr)
        return 2
    cmd = [sys.executable, str(script)] + (extra or [])
    return subprocess.run(cmd, cwd=str(repo_root())).returncode


def cmd_benchmark(args, eng) -> int:
    return _run_script("eval/run_benchmark.py")


def cmd_selfcheck(args, eng) -> int:
    return _run_script("scripts/check_consistency.py")


# --------------------------------------------------------------------------- #
# argument parser
# --------------------------------------------------------------------------- #

def _add_text_args(p, strip_markup=True):
    p.add_argument("text", nargs="?", default=None,
                   help="text to analyze; '-' or omitted reads stdin")
    p.add_argument("--file", "-f", help="read input from a file instead")
    p.add_argument("--json", action="store_true", help="machine-readable JSON output")
    if not strip_markup:
        return
    p.add_argument("--strip-markup", action="store_true",
                   help="score the prose of a Markdown document: code blocks, "
                        "tables, blockquotes, quoted example lists and the "
                        "table of contents are removed first. Raw and stripped "
                        "score are reported side by side (#69)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slop",
        description="AI Slop toolkit — score, classify, and detect AI-slop patterns.",
    )
    parser.add_argument("--version", action="version", version=f"slopkit {__version__}")
    parser.add_argument("--ontology", help="path to an alternate ontology.json")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    specs = [
        ("score", "numeric slop score + severity", cmd_score, True, True),
        ("classify", "full classification report", cmd_classify, True, False),
        ("rhetoric", "detect-only rhetorical patterns", cmd_rhetoric, True, False),
        ("check", "combined score + rhetorical report", cmd_check, True, True),
    ]
    for name, help_text, func, text_args, gate in specs:
        sp = sub.add_parser(name, help=help_text)
        if text_args:
            _add_text_args(sp)
        if gate:
            sp.add_argument("--fail-over", type=float, metavar="THRESHOLD",
                            help="exit non-zero when the slop score is >= THRESHOLD (CI gating)")
        sp.set_defaults(func=func)

    # Source code is not Markdown, so the pre-pass has nothing to do there.
    # Accepting the flag and ignoring it would be worse than not offering it.
    sp_code = sub.add_parser("code", help="classify source code for slop")
    _add_text_args(sp_code, strip_markup=False)
    sp_code.add_argument("--lang", help="language hint (e.g. python, js)")
    sp_code.set_defaults(func=cmd_code)

    sp_info = sub.add_parser("info", help="signal-database + ontology metadata")
    sp_info.add_argument("--json", action="store_true")
    sp_info.set_defaults(func=cmd_info)

    sp_bench = sub.add_parser("benchmark", help="run the labelled-corpus benchmark")
    sp_bench.set_defaults(func=cmd_benchmark)

    sp_self = sub.add_parser("selfcheck", help="run the serialization consistency check")
    sp_self.set_defaults(func=cmd_selfcheck)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0

    # benchmark/selfcheck don't need the engine loaded.
    if args.command in ("benchmark", "selfcheck"):
        return args.func(args, None)

    try:
        eng = get_engine(getattr(args, "ontology", None))
    except FileNotFoundError as e:
        print(f"error: cannot load ontology ({e})", file=sys.stderr)
        return 2
    return args.func(args, eng)


if __name__ == "__main__":
    sys.exit(main())
