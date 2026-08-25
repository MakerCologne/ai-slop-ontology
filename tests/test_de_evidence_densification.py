"""Issue #76 Rest (RI-2-FU) — Evidence-Verdichtung der de_*-Phrasen.

Ziel: >= 2 unabhängige Belege für >= 50% der de_*-Phrasen. Zweite Belege
sind eigene handgeschriebene Belegtexte (eval/de_evidence_texts.jsonl,
source "own:corpus") — keine Kopien aus CC BY-SA-Drittkatalogen.

Verankert:
1. Coverage-Pin >= 50% (C4-Erweiterung in scripts/check_ssot.py).
2. Konsistenz: jede own:corpus-Evidenz referenziert eine existierende
   Belegtext-Id, und jede referenzierte Phrase kommt dort wörtlich vor.
3. Manipulationsprobe: Coverage unter 50% drücken -> check_ssot rc=1.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _de_phrases():
    with open(os.path.join(ROOT, "ontology.json"), encoding="utf-8") as f:
        d = json.load(f)
    cats = d["signals"]["text"]["phrases"]["categories"]
    out = {}
    for k, v in cats.items():
        if k.startswith("de_"):
            for p in v.get("items", []):
                out[(k, p)] = v["evidence"].get(p, [])
    return out


class TestEvidenceCoverage:
    def test_at_least_half_of_de_phrases_have_two_evidence(self):
        phrases = _de_phrases()
        multi = sum(1 for ev in phrases.values() if len(ev) >= 2)
        assert multi / len(phrases) >= 0.5, (
            f"nur {multi}/{len(phrases)} de_*-Phrasen mit >=2 Belegen "
            "(RI-2-FU-Ziel: >= 50%)")

    def test_second_evidence_sources_are_independent(self):
        """Der 2. Beleg darf nicht denselben source-String wie der 1.
        haben (Unabhängigkeit: Wikipedia vs. own:corpus/de-observation)."""
        for (cat, p), ev in _de_phrases().items():
            if len(ev) >= 2:
                sources = [e.get("source") for e in ev]
                assert len(set(sources)) == len(sources), (cat, p, sources)


class TestEvidenceTextsFile:
    def test_own_corpus_evidence_references_existing_text(self):
        path = os.path.join(ROOT, "eval", "de_evidence_texts.jsonl")
        assert os.path.isfile(path)
        with open(path, encoding="utf-8") as f:
            texts = {json.loads(l)["id"]: json.loads(l) for l in f if l.strip()}

        for (cat, p), ev in _de_phrases().items():
            for e in ev:
                if e.get("source") != "own:corpus":
                    continue
                note = e.get("note", "")
                refs = [tid for tid in texts if tid in note]
                assert refs, (cat, p, "own:corpus ohne Belegtext-Referenz")
                tid = refs[0]
                assert p in texts[tid]["text"].lower(), (
                    cat, p, f"Phrase fehlt wörtlich in {tid}")
                assert p in texts[tid]["phrases"], (cat, p, tid)

    def test_evidence_texts_are_own_handwritten(self):
        """Jeder Belegtext trägt source=own:corpus (eigene Handschrift,
        Lizenzregel: keine Kopien aus CC BY-SA-Katalogen)."""
        path = os.path.join(ROOT, "eval", "de_evidence_texts.jsonl")
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                assert rec["source"] == "own:corpus"
                assert rec["id"].startswith("de-ev-")


class TestC4CoveragePin:
    """C4-Erweiterung: >= 50%-Coverage ist ein Gate, nicht nur ein Bericht."""

    def _run_check(self, cwd):
        return subprocess.run(
            [sys.executable, "scripts/check_ssot.py"],
            capture_output=True, text=True, cwd=cwd)

    def test_clean_repo_passes_with_coverage_line(self):
        proc = self._run_check(ROOT)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "evidence" in proc.stdout.lower() and "50" in proc.stdout

    def test_below_half_coverage_fails(self, tmp_path):
        work = tmp_path / "w"
        shutil.copytree(ROOT, work,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
        ontpath = work / "ontology.json"
        d = json.loads(ontpath.read_text(encoding="utf-8"))
        cats = d["signals"]["text"]["phrases"]["categories"]
        # alle own:corpus-Zweitbelege streichen -> Coverage 0% << 50%
        for k, v in cats.items():
            if not k.startswith("de_"):
                continue
            for p, ev in v.get("evidence", {}).items():
                v["evidence"][p] = [e for e in ev
                                    if e.get("source") != "own:corpus"]
        # C1: Skill-Kopie identisch halten
        (work / "skills" / "ai-slop-detection" / "references" / "ontology.json")\
            .write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
        ontpath.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
        proc = self._run_check(str(work))
        assert proc.returncode == 1
        assert "50" in proc.stdout
