#!/usr/bin/env python3
"""CLI for the DESLOP-LOOP orchestrator (issue #51).

The loop itself never rewrites text (ADR-0001). To run a fixing loop you
must provide a fix callback module (a Python file defining
``fix(text, findings) -> candidate``); without one the CLI runs in
audit-only mode (DETECT + EXIT-CHECK) and honestly escalates.

Usage:
    python3 scripts/deslop_loop_cli.py INPUT.txt [--runs-dir runs] \
        [--fix-module path/to/fixer.py] [--threshold 0.4] [--max-iter 5]

Output: verdict, exit check, iteration count and the run directory.
"""

import argparse
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.deslop_loop import DeslopLoop, LoopParams  # noqa: E402


def load_fix_module(path):
    spec = importlib.util.spec_from_file_location("deslop_fix_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fix = getattr(mod, "fix", None)
    if not callable(fix):
        raise SystemExit(f"fix module {path} does not define fix(text, findings)")
    return fix


def main():
    ap = argparse.ArgumentParser(description="DESLOP-LOOP orchestrator CLI")
    ap.add_argument("input", help="text file to deslop")
    ap.add_argument("--runs-dir", default="runs")
    ap.add_argument("--fix-module", default=None,
                    help="python file with fix(text, findings) -> candidate")
    ap.add_argument("--threshold", type=float, default=0.4)
    ap.add_argument("--max-iter", type=int, default=5)
    ap.add_argument("--epsilon", type=float, default=0.01)
    ap.add_argument("--voice-budget", type=float, default=0.25)
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()

    with open(args.input) as f:
        text = f.read()

    fix = load_fix_module(args.fix_module) if args.fix_module else None
    loop = DeslopLoop(
        params=LoopParams(score_threshold=args.threshold, max_iter=args.max_iter,
                          epsilon=args.epsilon, voice_budget=args.voice_budget),
        runs_dir=args.runs_dir, run_id=args.run_id)
    res = loop.run(text, fix=fix)
    print(json.dumps({
        "verdict": res.verdict,
        "exit_check": res.exit_check,
        "iterations": res.iterations,
        "score_initial": round(res.score_initial, 4),
        "score_final": round(res.score_final, 4),
        "open_signals": res.open_signals,
        "guarantee": res.guarantee,
        "run_dir": res.run_dir,
    }, indent=2, ensure_ascii=False))
    return 0 if res.verdict == "EXIT_OK" else 1


if __name__ == "__main__":
    sys.exit(main())
