#!/usr/bin/env python3
"""Verify the citation sources of the Human/Work/SEO slop extension.

Two layers, because a citation can fail in two different ways:

  offline (default)  Deterministic structural checks with no network:
                     - arXiv ids match YYMM.NNNNN and are not future-dated
                     - DOIs match the 10.xxxx/suffix grammar
                     - every other source is a well-formed http(s) URL
                     - every source id (S01…) is referenced by >= 1 type
                     Fails (exit 1) on any structural problem. Runs in CI.

  --online           Additionally resolves every URL over the network and
                     reports one of: ok / not_found / inconclusive. Only
                     not_found (HTTP 404/410 or DNS failure) is treated as a
                     hard failure; 403/429/timeouts are "inconclusive" because
                     publishers routinely block automated clients even for real
                     papers. Meant for a scheduled/manual job, not the main CI.

Usage:
    python3 verify_sources.py            # offline structural checks
    python3 verify_sources.py --online   # also resolve URLs
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTENSION = HERE / "human_work_seo_slop.json"

ARXIV_NEW = re.compile(r"^https://arxiv\.org/abs/(\d{2})(\d{2})\.(\d{4,5})(v\d+)?$")
ARXIV_OLD = re.compile(r"^https://arxiv\.org/abs/[a-z-]+(\.[A-Z]{2})?/\d{7}(v\d+)?$")
DOI = re.compile(r"^https://doi\.org/10\.\d{4,9}/\S+$")
URL = re.compile(r"^https?://[^\s/]+\.[^\s/]+.*$")


def classify(url: str) -> str:
    if "arxiv.org/abs/" in url:
        return "arxiv"
    if "doi.org/" in url:
        return "doi"
    return "url"


def check_structure(source_id: str, url: str, as_of: datetime.date):
    """Return an error string, or None when the source is structurally valid."""
    kind = classify(url)

    if kind == "arxiv":
        m = ARXIV_NEW.match(url)
        if not m:
            if ARXIV_OLD.match(url):
                return None
            return f"{source_id}: malformed arXiv id ({url})"
        yy, mm = int(m.group(1)), int(m.group(2))
        if not 1 <= mm <= 12:
            return f"{source_id}: arXiv month out of range ({url})"
        year = 2000 + yy
        # An arXiv id encodes its submission month; it cannot be in the future.
        if (year, mm) > (as_of.year, as_of.month):
            return f"{source_id}: arXiv id is future-dated {year}-{mm:02d} ({url})"
        return None

    if kind == "doi":
        return None if DOI.match(url) else f"{source_id}: malformed DOI ({url})"

    return None if URL.match(url) else f"{source_id}: malformed URL ({url})"


def load():
    return json.loads(EXTENSION.read_text(encoding="utf-8"))


def run_offline(data, as_of: datetime.date):
    """Return (errors, warnings). Errors gate CI; warnings are quality smells."""
    errors, warnings = [], []
    sources = data["sources"]

    for sid, url in sources.items():
        err = check_structure(sid, url, as_of)
        if err:
            errors.append(err)

    # Every referenced id must be declared (mirror of the existing unit test).
    for item in data["types"]:
        for sid in item.get("sources", []):
            if sid not in sources:
                errors.append(f"{item['id']}: references undeclared source {sid}")

    # Every declared source should be cited by at least one type. Uncited
    # sources are a padding smell, not a structural error — warn, don't fail.
    referenced = set()
    for item in data["types"]:
        referenced.update(item.get("sources", []))
    for sid in sorted(set(sources) - referenced):
        warnings.append(f"{sid}: declared but never referenced by a type")

    return errors, warnings


def run_online(sources):
    """Resolve each URL; returns (results, hard_failures)."""
    import urllib.error
    import urllib.request

    results = {}
    hard = []
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", "ai-slop-ontology-source-verifier/1.0")]

    for sid, url in sources.items():
        try:
            req = urllib.request.Request(url, method="HEAD")
            with opener.open(req, timeout=20) as resp:
                code = resp.status
            status = "ok" if code < 400 else f"inconclusive(HTTP {code})"
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                status = f"not_found(HTTP {e.code})"
                hard.append(f"{sid}: {url} -> HTTP {e.code}")
            else:
                status = f"inconclusive(HTTP {e.code})"
        except Exception as e:  # DNS failure, timeout, TLS, proxy block, ...
            reason = type(e).__name__
            # A DNS failure is a strong "does not exist" signal.
            if "NameResolutionError" in reason or "gaierror" in reason:
                status = "not_found(DNS)"
                hard.append(f"{sid}: {url} -> DNS resolution failed")
            else:
                status = f"inconclusive({reason})"
        results[sid] = (url, status)

    return results, hard


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify extension citation sources.")
    parser.add_argument("--online", action="store_true",
                        help="also resolve URLs over the network")
    parser.add_argument("--as-of", help="YYYY-MM-DD used for the arXiv future check")
    args = parser.parse_args(argv)

    as_of = (datetime.date.fromisoformat(args.as_of) if args.as_of
             else datetime.date.today())
    data = load()

    errors, warnings = run_offline(data, as_of)
    for w in warnings:
        print(f"  ⚠ {w}")
    if errors:
        print("Source verification FAILED (offline):")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    print(f"Offline source check passed ({len(data['sources'])} sources: "
          f"structure valid, none future-dated"
          + (f"; {len(warnings)} uncited)" if warnings else ")"))

    if args.online:
        results, hard = run_online(data["sources"])
        print("\nOnline resolution:")
        for sid in sorted(results):
            url, status = results[sid]
            mark = "✓" if status == "ok" else ("✗" if status.startswith("not_found") else "?")
            print(f"  {mark} {sid} {status}  {url}")
        if hard:
            print("\nOnline verification FAILED (dead/nonexistent URLs):")
            for h in hard:
                print(f"  ✗ {h}")
            return 1
        print("\nOnline check: no dead links (403/429/timeouts treated as inconclusive).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
