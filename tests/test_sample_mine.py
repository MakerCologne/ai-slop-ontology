#!/usr/bin/env python3
"""Issue #12 — empirical re-calibration loop (sampling harness).

DoD: mine() proposes only NEW n-grams (not covered by scorer vocabulary),
ranks by doc-frequency, caps candidates, and never touches the network.
"""

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "eval", "sample_mine.py")


def _samples(tmp, records):
    path = os.path.join(tmp, "samples.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps({"text": r, "model": "m", "domain": "blog"}) + "\n")
    return path


def run_mine(path, *extra):
    out = subprocess.run([sys.executable, SCRIPT, "mine", "--samples", path, *extra],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    return out.stdout


def test_repeated_ngram_proposed(tmp_path):
    marker = "quuxblorf zabbing carefully"  # not in any current tier
    path = _samples(str(tmp_path), [f"{marker} fills sample one.", f"again {marker} two.",
                                    "unrelated text only here."])
    out = run_mine(path, "--json")
    data = json.loads(out)
    phrases = [c["phrase"] for c in data["candidates"]]
    assert any("quuxblorf zabbing carefully" in p
               for p in phrases), phrases


def test_known_vocabulary_filtered(tmp_path):
    # "delve" is covered by existing buzzword tiers → must NOT be proposed
    path = _samples(str(tmp_path), ["delve into the topic one.", "delve into more two."])
    data = json.loads(run_mine(path, "--json"))
    assert not any("delve" in c["phrase"] for c in data["candidates"])


def test_single_occurrence_not_proposed(tmp_path):
    path = _samples(str(tmp_path), ["unique phrasing alpha only.", "different words entirely."])
    data = json.loads(run_mine(path, "--json"))
    assert data["candidates"] == []


def test_candidate_cap(tmp_path):
    texts = [" ".join(f"tok{i} tok{j}" for j in range(5)) for i in range(30)]
    # make every text share 60 distinct bigrams
    shared = [f"zzphrase{k} beta" for k in range(60)]
    texts = [t + " " + " ".join(shared) for t in texts]
    path = _samples(str(tmp_path), texts)
    data = json.loads(run_mine(path, "--json", "--max-candidates", "10"))
    assert len(data["candidates"]) == 10


def test_out_candidates_file(tmp_path):
    path = _samples(str(tmp_path), ["xray yankee one.", "xray yankee two."])
    out_file = os.path.join(tmp_path, "cand.json")
    run_mine(path, "--out-candidates", out_file)
    data = json.load(open(out_file, encoding="utf-8"))
    assert data["n_samples"] == 2
    assert any("xray yankee" in c["phrase"] for c in data["candidates"])


def test_generate_requires_endpoint(_tmp=None):
    env = os.environ.pop("OPENAI_BASE_URL", None)
    try:
        out = subprocess.run([sys.executable, SCRIPT, "generate", "--model", "m"],
                             capture_output=True, text=True, cwd=ROOT)
        assert out.returncode != 0
        assert "OPENAI_BASE_URL" in out.stderr
    finally:
        if env:
            os.environ["OPENAI_BASE_URL"] = env


if __name__ == "__main__":
    import tempfile
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_")]:
        with tempfile.TemporaryDirectory() as tmp:
            fn(tmp)
        print(f"ok {fn.__name__}")
    print("all passed")
