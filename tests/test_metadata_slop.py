"""Tests for src/metadata_slop.py — detect-only metadata/config/data slop
(issue #45: commit messages, PR bodies, JSON data fields, config
boilerplate). Positive and negative fixtures per surface."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from metadata_slop import MetadataSlopClassifier  # noqa: E402


def test_commit_message_positive_classic():
    mdc = MetadataSlopClassifier()
    msg = ("This PR refactors the auth module to improve code readability "
           "and maintainability. It also updates the config to improve "
           "consistency across files.")
    res = mdc.classify_commit_message(msg)
    assert res.is_slop
    assert res.signals_detected[0].signal_id == "CommitMessageSlop"
    assert res.signals_detected[0].surface == "commit_message"
    assert 0.5 <= res.signals_detected[0].confidence <= 0.95


def test_commit_message_positive_imperative_i_have():
    mdc = MetadataSlopClassifier()
    msg = "I have implemented the login flow for you as requested. " \
          "This commit adds validation as per the requirements."
    res = mdc.classify_commit_message(msg)
    assert res.is_slop


def test_commit_message_negative_human():
    mdc = MetadataSlopClassifier()
    msg = ("auth: rotate refresh token on password change\n\n"
           "Closes #412. Without rotation a stolen refresh token stayed "
           "valid after the password was changed, so the session survived "
           "the intended logout.")
    assert not mdc.classify_commit_message(msg).is_slop


def test_commit_message_negative_single_weak_hit():
    """One weak hit alone must not fire (min 2 distinct patterns)."""
    mdc = MetadataSlopClassifier()
    msg = "Update dependencies"
    assert not mdc.classify_commit_message(msg).is_slop


def test_json_fields_positive_filler():
    mdc = MetadataSlopClassifier()
    data = ('{"name": "toolkit", "description": "A comprehensive suite of '
            'tools for developers", "notes": "TODO: add description"}')
    res = mdc.classify_json_fields(data)
    assert res.is_slop
    assert res.signals_detected[0].signal_id == "JsonFieldSlop"


def test_json_fields_positive_key_restatement():
    mdc = MetadataSlopClassifier()
    data = ('{"description": "The description of the service", '
            '"summary": "A powerful collection of features for users"}')
    res = mdc.classify_json_fields(data)
    assert res.is_slop


def test_json_fields_negative_real_content():
    mdc = MetadataSlopClassifier()
    data = ('{"name": "scorer", "description": "Scores text against 41 '
            'signals from ontology.json v2.3", "notes": "raises if weights '
            'sum > 1.0"}')
    assert not mdc.classify_json_fields(data).is_slop


def test_config_positive_dockerfile():
    mdc = MetadataSlopClassifier()
    dockerfile = ("# This script does the build setup\n"
                  "FROM python:3.12-slim\n"
                  "# Install dependencies\n"
                  "RUN pip install -r requirements.txt\n"
                  "# Configuration for the application\n")
    res = mdc.classify_config(dockerfile)
    assert res.is_slop
    assert res.signals_detected[0].signal_id == "ConfigBoilerplateSlop"
    assert res.signals_detected[0].severity == "low"


def test_config_positive_terraform():
    mdc = MetadataSlopClassifier()
    tf = ("# Create a bucket resource\n"
          "resource \"aws_s3_bucket\" \"logs\" {\n"
          "  bucket = \"logs\"\n"
          "}\n"
          "# Configuration for prod\n")
    res = mdc.classify_config(tf)
    assert res.is_slop


def test_config_negative_meaningful_comments():
    mdc = MetadataSlopClassifier()
    dockerfile = (
        "# 3.12-slim: glibc needed for pyodide native ext; alpine segfaults "
        "on load (see #77)\n"
        "FROM python:3.12-slim\n"
        "# Keep layer cache separate: requirements change less than source\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n")
    assert not mdc.classify_config(dockerfile).is_slop


def test_config_negative_no_comments():
    mdc = MetadataSlopClassifier()
    assert not mdc.classify_config("run:\n  - echo hi\n").is_slop


def test_empty_inputs():
    mdc = MetadataSlopClassifier()
    assert not mdc.classify_commit_message("").is_slop
    assert not mdc.classify_json_fields(None).is_slop
    assert not mdc.classify_config("").is_slop


def test_classify_all_merges():
    mdc = MetadataSlopClassifier()
    res = mdc.classify_all(
        commit_message="This PR refactors X to improve readability and "
                       "maintainability. This PR implements the endpoint "
                       "as per the requirements.",
        json_text='{"description": "A comprehensive tool", '
                  '"summary": "The summary of the tool"}',
        config_text="# This file contains settings\n# Configuration for app\n",
    )
    ids = {f.signal_id for f in res.signals_detected}
    assert ids == {"CommitMessageSlop", "JsonFieldSlop",
                   "ConfigBoilerplateSlop"}
    assert "clean" not in res.summary()


def test_summary_clean():
    mdc = MetadataSlopClassifier()
    assert mdc.classify_commit_message("fix: typo").summary() == "clean"


def test_detect_only_no_rewrite():
    """ADR-0001: the classifier must not offer rewrite/fix APIs."""
    mdc = MetadataSlopClassifier()
    assert not hasattr(mdc, "fix")
    assert not hasattr(mdc, "rewrite")
