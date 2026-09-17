"""Tests for src/paste_artifacts.py — 6 deterministic micro-signals
(issue #113: chat-paste artifacts & elision). Positive and negative
fixtures per signal."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from paste_artifacts import PasteArtifactClassifier  # noqa: E402


def _ids(res):
    return sorted({f.signal_id for f in res.signals_detected})


# -- elision-comment -------------------------------------------------------

def test_elision_positive():
    code = "\n".join([
        "import os",
        "# ... rest of the code unchanged ...",
        "def main(): pass",
    ])
    res = PasteArtifactClassifier().classify_text(code)
    assert "elision-comment" in _ids(res)


def test_elision_positive_bracketed():
    code = "x = 1\n[... existing code here ...]\ny = 2"
    res = PasteArtifactClassifier().classify_text(code)
    assert "elision-comment" in _ids(res)


def test_elision_positive_python_hash():
    code = "a = f(x)\n# ... rest of implementation not shown\nb = g(y)"
    res = PasteArtifactClassifier().classify_text(code)
    assert "elision-comment" in _ids(res)


def test_elision_negative_normal_comments():
    code = "\n".join([
        "# calculate the remaining part of the sum",
        "total = sum(rest_of_list)",
        "# unchanged input values are cached",
        "def cache(x): return x",
    ])
    res = PasteArtifactClassifier().classify_text(code)
    assert "elision-comment" not in _ids(res)


# -- chat-preamble ---------------------------------------------------------

def test_chat_preamble_positive_certainly():
    text = "Certainly!\n\n```python\ndef f(): pass\n```"
    res = PasteArtifactClassifier().classify_text(text)
    assert "chat-preamble" in _ids(res)


def test_chat_preamble_positive_heres_the_corrected():
    text = "Here's the corrected version of the function:\n\ndef f(): pass"
    res = PasteArtifactClassifier().classify_text(text)
    assert "chat-preamble" in _ids(res)


def test_chat_preamble_positive_as_an_ai():
    text = "As an AI, I cannot run this code, but the logic should work."
    res = PasteArtifactClassifier().classify_text(text)
    assert "chat-preamble" in _ids(res)


def test_chat_preamble_negative_normal_doc():
    text = "Here you find the documentation. Of course the API is stable."
    res = PasteArtifactClassifier().classify_text(text)
    assert "chat-preamble" not in _ids(res)


# -- fence-in-code ---------------------------------------------------------

def test_fence_positive_pair_in_code():
    code = "\n".join([
        "def f(): pass",
        "```",
        "g()",
        "```",
        "h()",
    ])
    res = PasteArtifactClassifier().classify_text(code)
    assert "fence-in-code" in _ids(res)


def test_fence_skipped_in_markdown():
    md = "Example:\n\n```python\ndef f(): pass\n```\n\nDone."
    res = PasteArtifactClassifier().classify_text(md, is_markdown=True)
    assert "fence-in-code" not in _ids(res)
    assert any("markdown" in n for n in res.notes)


# -- meta-process-comment --------------------------------------------------

def test_meta_process_positive_two_hits():
    code = "\n".join([
        "# Phase 2: verify the agent behavior in production",
        "x = 1",
        "# the model output is checked per my previous instruction",
        "y = 2",
    ])
    res = PasteArtifactClassifier().classify_text(code)
    assert "meta-process-comment" in _ids(res)


def test_meta_process_negative_single_legit_phase():
    code = "# Phase 2 of the migration: see docs/plan.md\nx = 1"
    res = PasteArtifactClassifier().classify_text(code)
    assert "meta-process-comment" not in _ids(res)


def test_meta_process_negative_normal_code():
    code = "\n".join([
        "# cache the model weights",
        "weights = load()",
        "# agent instance for background jobs",
        "agent = Agent()",
    ])
    res = PasteArtifactClassifier().classify_text(code)
    assert "meta-process-comment" not in _ids(res)


# -- list-label-marker -----------------------------------------------------

def test_list_label_positive_two_hits():
    doc = "\n".join([
        "- G1: intro line",
        "- NG2: counter-example line",
        "- normal item",
    ])
    res = PasteArtifactClassifier().classify_text(doc)
    assert "list-label-marker" in _ids(res)


def test_list_label_negative_single_reference():
    doc = "See BS-I7 for the aggregation method.\n\n- G1: only one marker here"
    res = PasteArtifactClassifier().classify_text(doc)
    assert "list-label-marker" not in _ids(res)


# -- placeholder-credential-shape ------------------------------------------

def test_placeholder_credential_positive_your():
    code = 'config.token = "your_api_key_here"'
    res = PasteArtifactClassifier().classify_text(code)
    assert "placeholder-credential-shape" in _ids(res)


def test_placeholder_credential_positive_insert():
    code = "# INSERT_TOKEN before running\nclient = Client(token)"
    res = PasteArtifactClassifier().classify_text(code)
    assert "placeholder-credential-shape" in _ids(res)


def test_placeholder_credential_negative_real_usage():
    code = "\n".join([
        "os.environ['API_KEY']",
        "token = auth.get_token()",
        "password = request.form['password']",
    ])
    res = PasteArtifactClassifier().classify_text(code)
    assert "placeholder-credential-shape" not in _ids(res)


# -- aggregate behavior ----------------------------------------------------

def test_clean_code_yields_no_signals():
    code = "\n".join([
        "import json",
        "",
        "def load(path):",
        "    with open(path) as f:",
        "        return json.load(f)",
        "",
        "if __name__ == '__main__':",
        "    print(load('data.json'))",
    ])
    res = PasteArtifactClassifier().classify_text(code)
    assert not res.is_slop
    assert res.summary() == "clean"


def test_every_finding_carries_evidence_and_severity():
    demo = "Certainly!\n# ... rest of code unchanged\n"
    res = PasteArtifactClassifier().classify_text(demo)
    assert res.is_slop
    for f in res.signals_detected:
        assert f.evidence
        assert f.severity in ("low", "medium", "high")
        assert f.confidence > 0


def test_signal_catalog_covers_all_six():
    pac = PasteArtifactClassifier()
    assert set(pac._signals.keys()) == {
        "elision-comment", "chat-preamble", "fence-in-code",
        "meta-process-comment", "list-label-marker",
        "placeholder-credential-shape",
    }
