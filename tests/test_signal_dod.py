"""#64 — Signal-Definition-of-Done: heuristischer Check neuer Signale (scripts/check_signal_dod.py)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "check_signal_dod.py")


def make_fixture(tmp_path):
    """Fixture-Repo: ein vollständiges Signal, eines ohne Test, eines ohne keep_when."""
    scripts = tmp_path / "scripts"; scripts.mkdir()
    tests = tmp_path / "tests"; tests.mkdir()
    skill = tmp_path / "SKILL.md"; skill.write_text("Refs: good_signal\n", encoding="utf-8")

    good = scripts / "good_signal.py"
    good.write_text("# signal\n# keep_when: technical genre\nPATTERNS = []\n", encoding="utf-8")
    (tests / "test_good_signal.py").write_text("import good_signal\n", encoding="utf-8")

    no_test = scripts / "no_test_signal.py"
    no_test.write_text("# keep_when: none\nPATTERNS = []\n", encoding="utf-8")

    no_guard = scripts / "no_guard_signal.py"
    no_guard.write_text("PATTERNS = []\n", encoding="utf-8")
    (tests / "test_no_guard_signal.py").write_text("import no_guard_signal\n", encoding="utf-8")

    infra = scripts / "slop_scorer.py"; infra.write_text("INFRA = 1\n", encoding="utf-8")
    return scripts, tests, skill


def test_script_exists():
    assert os.path.isfile(SCRIPT)


def test_scan_reports_fixture(tmp_path):
    scripts, tests, skill = make_fixture(tmp_path)
    import importlib.util
    spec = importlib.util.spec_from_file_location("csd", SCRIPT)
    csd = importlib.util.module_from_spec(spec); spec.loader.exec_module(csd)
    report = csd.scan_signals(str(scripts), str(tests), str(skill))
    by_name = {r.module: r for r in report}
    assert by_name["good_signal"].ok, "vollständiges Signal muss ok sein"
    assert by_name["no_test_signal"].failures, "fehlender Test muss FAIL sein"
    assert by_name["no_guard_signal"].warnings, "fehlende keep_when-Doku muss WARN sein"
    assert by_name["slop_scorer"].infra, "Infra-Modul muss als infra erkannt werden"


def test_cli_reports_and_exits_zero(tmp_path):
    scripts, tests, skill = make_fixture(tmp_path)
    proc = subprocess.run(
        [sys.executable, SCRIPT,
         "--scripts-dir", str(scripts), "--tests-dir", str(tests),
         "--skill-md", str(skill)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, "Report-Modus muss exit 0 sein (reportet, kein Gate)"
    assert "no_test_signal" in proc.stdout
    assert "no_guard_signal" in proc.stdout


def test_cli_strict_fails_on_missing_test(tmp_path):
    scripts, tests, skill = make_fixture(tmp_path)
    proc = subprocess.run(
        [sys.executable, SCRIPT, "--strict",
         "--scripts-dir", str(scripts), "--tests-dir", str(tests),
         "--skill-md", str(skill)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1, "--strict muss bei FAIL exit 1 sein"


def test_dod_doc_exists():
    doc = os.path.join(ROOT, "docs", "SIGNAL-DOD.md")
    assert os.path.isfile(doc)
    text = open(doc, encoding="utf-8").read()
    for i in range(1, 9):
        assert str(i) in text, f"Must {i} fehlt in SIGNAL-DOD.md"
