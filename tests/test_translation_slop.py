"""Tests for src/translation_slop.py — TranslationSlop/MT-Calque-Klasse
(issue #53, Teil 2). Positive und negative Fixtures je Signal
(3+ pos / 3+ neg, inkl. FP-Guards: Metasprache, Code)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from translation_slop import TranslationSlopClassifier  # noqa: E402


def _ids(res):
    return sorted({f["signal_id"] for f in res})


# -- mt-calque-idiom-literal: positives ------------------------------------

def test_idiom_positive_de_to_en_yellow_of_the_egg():
    text = "The design is nice, but the performance is not the yellow of the egg."
    res = TranslationSlopClassifier().classify_text(text)
    assert "mt-calque-idiom-literal" in _ids(res)


def test_idiom_positive_de_to_en_train_station():
    text = "He explained the new API twice, but I understand only train station."
    assert "mt-calque-idiom-literal" in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_idiom_positive_en_to_de_cats_and_dogs():
    text = ("Der Bericht zeigt, dass die Qualität stimmt.\n"
            "Draußen regnet es Katzen und Hunde, sagte sie.")
    assert "mt-calque-idiom-literal" in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_idiom_positive_en_to_de_wrong_tree():
    text = ("Mit dieser Argumentation bellst du an dem falschen Baum, "
            "wie die Analyse zeigt.")
    assert "mt-calque-idiom-literal" in _ids(
        TranslationSlopClassifier().classify_text(text))


# -- mt-calque-idiom-literal: negatives ------------------------------------

def test_idiom_negative_correct_english():
    text = ("The design is nice, but the performance is not perfect. "
            "He explained it twice, but I still don't get it.")
    assert "mt-calque-idiom-literal" not in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_idiom_negative_correct_german():
    text = ("Draußen regnet es in Strömen, und ich verstehe nur Bahnhof, "
            "wenn er die API erklärt. Das ist nicht mein Ding.")
    assert "mt-calque-idiom-literal" not in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_idiom_negative_metalinguistic_context():
    # Doku über Calques: metasprachliche Zeilen werden uebersprungen
    text = ("The German idiom »nicht das Gelbe vom Ei« is often literally "
            "translated as »not the yellow of the egg« — a classic calque.")
    assert "mt-calque-idiom-literal" not in _ids(
        TranslationSlopClassifier().classify_text(text))


# -- mt-calque-lexeme: positives ------------------------------------------

def test_lexeme_positive_tag_question_or():
    text = "We will ship the feature on Friday, or?"
    assert "mt-calque-lexeme" in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_lexeme_positive_until_see_us():
    text = "Until soon! We see us at the conference next week."
    assert "mt-calque-lexeme" in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_lexeme_positive_i_have_years():
    text = "I have thirty years and work as an engineer in Munich."
    assert "mt-calque-lexeme" in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_lexeme_positive_since_years():
    text = "The team works on this product since three years."
    assert "mt-calque-lexeme" in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_lexeme_positive_de_take_a_break():
    text = ("Der Bericht ist lang.\n"
            "Wenn du muede bist: Nimm dir eine Pause und lies spaeter weiter.")
    assert "mt-calque-lexeme" in _ids(
        TranslationSlopClassifier().classify_text(text))


# -- mt-calque-lexeme: negatives ------------------------------------------

def test_lexeme_negative_correct_english():
    text = ("We will ship the feature on Friday, won't we? "
            "I am thirty years old and have worked here for three years. "
            "See you at the conference! Take a photo of the whiteboard.")
    assert "mt-calque-lexeme" not in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_lexeme_negative_correct_german():
    text = ("Wenn du muede bist: Mach eine Pause. "
            "Bis bald! Wir sehen uns auf der Konferenz.")
    assert "mt-calque-lexeme" not in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_lexeme_negative_code_block():
    # Calques in Code-Fences/Inline-Code duerfen nicht feuern
    text = ("Docs:\n```python\nMSG = \"We will ship Friday, or?\"\n```\n"
            "Und der Wert `until soon` steht im Config-Objekt.")
    assert "mt-calque-lexeme" not in _ids(
        TranslationSlopClassifier().classify_text(text))


def test_lexeme_negative_ordinary_or_question():
    # "or" in echten EN-Fragen ist kein Satzend-Tag
    text = "Do you want tea, or would you prefer coffee instead?"
    assert "mt-calque-lexeme" not in _ids(
        TranslationSlopClassifier().classify_text(text))


# -- API-Konvention ---------------------------------------------------------

def test_api_shape_detect_only():
    res = TranslationSlopClassifier().classify_text(
        "Until soon, we see us!")
    assert all(set(f) == {"signal_id", "confidence", "evidence"} for f in res)
    assert all(0.0 < f["confidence"] <= 1.0 for f in res)
    assert all(f["signal_id"].startswith("mt-calque") for f in res)
