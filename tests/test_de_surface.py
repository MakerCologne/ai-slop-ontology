"""Tests for src/de_surface.py — 4 deterministische DE-Quick-Wins
(issue #73 Punkt 3). Positive und negative Fixtures je Signal."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from de_surface import DeSurfaceClassifier  # noqa: E402


def _ids(res):
    return sorted({f["signal_id"] for f in res})


DE_CTX = "Der Bericht zeigt, dass die Qualität nicht mit dem Ziel übereinstimmt."


# -- de-mismatched-quotes --------------------------------------------------

def test_mismatched_quotes_positive_same_char():
    text = DE_CTX + "\nEr sagte „das ist okay„ und ging weiter."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-mismatched-quotes" in _ids(res)


def test_mismatched_quotes_positive_english_close():
    text = DE_CTX + "\nDie „Lösung” war falsch, wie man sieht."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-mismatched-quotes" in _ids(res)


def test_mismatched_quotes_positive_dangling():
    text = DE_CTX + "\nEin unverpaarter Oeffner „ steht hier ohne Schluss."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-mismatched-quotes" in _ids(res)


def test_mismatched_quotes_negative_correct_german():
    text = DE_CTX + "\nEr sagte „das ist okay“ und ging weiter."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-mismatched-quotes" not in _ids(res)


def test_mismatched_quotes_negative_english_text():
    # englischer Text: DE-Gate muss greifen
    text = "He said “this is fine” and the “report” was okay."
    res = DeSurfaceClassifier().classify_text(text)
    assert res == []


# -- de-genitive-apostroph -------------------------------------------------

def test_genitive_positive_proper_name():
    text = DE_CTX + "\nDas ist Peter's Hund, der im Garten läuft."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-genitive-apostroph" in _ids(res)


def test_genitive_positive_deppenapostroph():
    text = DE_CTX + "\nWir haben die Pizza's bestellt, weil alle Hunger hatten."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-genitive-apostroph" in _ids(res)


def test_genitive_negative_german_correct():
    text = DE_CTX + "\nDas ist Peters Hund, der im Garten läuft."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-genitive-apostroph" not in _ids(res)


def test_genitive_negative_english_line():
    text = DE_CTX + "\nThat is john's dog in the garden, it's fine."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-genitive-apostroph" not in _ids(res)


# -- de-us-format ----------------------------------------------------------

def test_us_format_positive_date():
    text = DE_CTX + "\nDie Frist endet am 12/25/2026 ohne Ausnahme."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-us-format" in _ids(res)


def test_us_format_positive_dot_decimal():
    text = DE_CTX + "\nDas Paket wiegt 3.5 kg und ist 25 cm breit."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-us-format" in _ids(res)


def test_us_format_negative_german_date():
    text = DE_CTX + "\nDie Frist endet am 25.12.2026 ohne Ausnahme."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-us-format" not in _ids(res)


def test_us_format_negative_german_decimal():
    text = DE_CTX + "\nDas Paket wiegt 3,5 kg und ist 25 cm breit."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-us-format" not in _ids(res)


def test_us_format_negative_version_number():
    text = DE_CTX + "\nWir nutzen v3.5 kg-Modul nicht, aber Version 2.1.0 läuft."
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-us-format" not in _ids(res)


# -- de-title-case ---------------------------------------------------------

def test_title_case_positive():
    text = (DE_CTX + "\n# Die Zukunft Der Arbeit Mit Und Für Neue Wege\n"
            "Ein Satz, der für sich steht.")
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-title-case" in _ids(res)


def test_title_case_positive_two_never_caps():
    text = (DE_CTX + "\n## Wichtig ist Nicht Alles, Aber Man Muss Wählen\n"
            "Zweiter Satz.")
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-title-case" in _ids(res)


def test_title_case_negative_correct_german_heading():
    text = (DE_CTX + "\n# Die Zukunft der Arbeit mit neuen Wegen\n"
            "Ein Satz, der für sich steht.")
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-title-case" not in _ids(res)


def test_title_case_negative_sentence_initial():
    # "Mit" am Satzanfang/Heading-Anfang ist erlaubt (i>0-Regel)
    text = (DE_CTX + "\n# Mit neuen Wegen in die Zukunft\n"
            "Ein Satz, der für sich steht.")
    res = DeSurfaceClassifier().classify_text(text)
    assert "de-title-case" not in _ids(res)


# -- DE-Gate ---------------------------------------------------------------

def test_gate_negative_english():
    text = "This is a report about quality management and Peter's dog."
    assert DeSurfaceClassifier().classify_text(text) == []


def test_gate_positive_all_signals_combined():
    text = (
        "Der Bericht zeigt, dass die Qualität nicht stimmt.\n"
        "Er sagte „okay„ und ging.\n"
        "Das ist Peter's Hund mit 3.5 kg.\n"
        "# Die Zukunft Der Arbeit Mit Und Für Neue Wege\n"
    )
    res = DeSurfaceClassifier().classify_text(text)
    ids = _ids(res)
    assert ids == [
        "de-genitive-apostroph", "de-mismatched-quotes",
        "de-title-case", "de-us-format",
    ]
